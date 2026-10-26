#!/usr/bin/env python3
"""Descarga el calendario de Booking.com (iCal) y actualiza availability.json.

Lo ejecuta la tarea automática de GitHub (.github/workflows/calendario-y-web.yml), pero también se puede
probar a mano:

    BOOKING_ICAL_URL='https://ical.booking.com/v1/export?t=...' python3 tools/sync_calendar.py

Variables de entorno
    BOOKING_ICAL_URL  (obligatoria) enlace secreto de exportación de Booking. Se guarda en GitHub como
                      "secreto" y este programa NUNCA lo imprime ni lo escribe en ningún archivo.
    CLOSED_FROM       (opcional) AAAA-MM-DD. Primer día desde el que Booking no tiene nada a la venta
                      (el .ics solo lista las noches cerradas o reservadas, no las que nunca se abrieron).
                      Si la fecha ya pasó o está vacía, se ignora.
    AVAIL_FILE        (opcional) ruta del archivo a escribir (por defecto availability.json en la raíz).

Reglas
    - Solo se acepta un enlace https de un dominio booking.com.
    - Si algo falla (sin conexión, respuesta que no es un calendario...) termina con error y deja el
      archivo anterior intacto: la web sigue mostrando los últimos datos buenos.
    - Solo reescribe el archivo si cambian las noches ocupadas, el campo closedFrom o si lo escrito
      tiene más de REFRESH_HOURS horas (así la web sabe que el calendario está al día).
    - Nunca se copian nombres, descripciones ni identificadores de los huéspedes.
"""
import datetime as dt
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ical_to_availability as ical  # noqa: E402

ROOT = HERE.parent
MONTHS = 16          # meses hacia delante que se guardan
REFRESH_HOURS = 20   # como mínimo se refresca "generated" cada tanto
RETRIES = 4
MAX_BYTES = 5_000_000


class SyncError(Exception):
    pass


def check_url(url, allow_local_test=False):
    """Solo https y solo booking.com (salvo el modo de pruebas con 127.0.0.1)."""
    try:
        p = urllib.parse.urlparse(url.strip())
    except ValueError:
        raise SyncError("BOOKING_ICAL_URL no es un enlace válido")
    host = (p.hostname or "").lower()
    if allow_local_test and p.scheme == "http" and host == "127.0.0.1":
        return url.strip()
    if p.scheme != "https":
        raise SyncError("BOOKING_ICAL_URL debe empezar por https://")
    if host != "booking.com" and not host.endswith(".booking.com"):
        raise SyncError("BOOKING_ICAL_URL no es un enlace de booking.com")
    return url.strip()


def download(url, retries=RETRIES, wait=lambda s: time.sleep(s)):
    """Descarga el texto. Los mensajes de error no incluyen el enlace (es secreto)."""
    last = "sin respuesta"
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "casa-sofia-calendar-sync/1.0", "Accept": "text/calendar,*/*"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise SyncError("la respuesta es demasiado grande para ser un calendario")
            text = raw.decode("utf-8", errors="replace")
            if "BEGIN:VCALENDAR" not in text or "END:VCALENDAR" not in text:
                # Booking a veces devuelve una página HTML de error; no se reintenta a ciegas
                raise SyncError("la respuesta no es un calendario iCal (¿el enlace ha caducado o se ha cambiado?)")
            return text
        except SyncError:
            raise
        except urllib.error.HTTPError as e:
            last = "HTTP %s" % e.code
            if e.code in (400, 401, 403, 404, 410):
                raise SyncError("Booking.com rechaza el enlace (%s): hay que copiar de nuevo el enlace de exportación" % last)
        except Exception as e:  # red, DNS, tiempo agotado...
            last = type(e).__name__
        if attempt < retries:
            wait(5 * attempt)
    raise SyncError("no se pudo descargar el calendario tras %d intentos (%s)" % (retries, last))


def madrid_today():
    if ical.LOCAL is not None:
        return dt.datetime.now(ical.LOCAL).date()
    return dt.date.today()


def parse_closed_from(value, today):
    value = (value or "").strip()
    if not value:
        return None
    try:
        d = dt.date.fromisoformat(value)
    except ValueError:
        raise SyncError("CLOSED_FROM debe tener el formato AAAA-MM-DD (por ejemplo 2027-02-01)")
    return d.isoformat() if d >= today else None


def load_previous(path):
    try:
        d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def parse_generated(value):
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


def sync(ics_text, out_path, today, now=None, closed_from=None):
    """Aplica el calendario al archivo. Devuelve (escrito: bool, resumen: str)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    try:
        merged, total, skipped = ical.build(ics_text, today, MONTHS)
    except ValueError:
        raise SyncError("el calendario tiene un formato de fecha inesperado")
    data = {
        "generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "booking-ical",
        "busy": [[a.isoformat(), b.isoformat()] for a, b in merged],
    }
    cf = parse_closed_from(closed_from, today)
    if cf:
        data["closedFrom"] = cf

    prev = load_previous(out_path)
    same = bool(prev) and prev.get("busy") == data["busy"] and prev.get("closedFrom") == data.get("closedFrom")
    fresh = False
    if same:
        g = parse_generated(prev.get("generated", ""))
        fresh = g is not None and (now - g) < dt.timedelta(hours=REFRESH_HOURS) and g <= now + dt.timedelta(minutes=5)
    nights = sum((b - a).days for a, b in merged)
    summary = "%d eventos leídos, %d bloques, %d noches ocupadas" % (total, len(merged), nights)
    if same and fresh:
        return False, summary + " (sin cambios)"
    pathlib.Path(out_path).write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return True, summary + (" (sin cambios en las noches; se refresca la fecha de actualización)" if same else " (calendario actualizado)")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    allow_local = "--allow-local-test" in argv
    url = os.environ.get("BOOKING_ICAL_URL", "").strip()
    if not url:
        print("ERROR: falta el secreto BOOKING_ICAL_URL. En GitHub: Settings > Secrets and variables > Actions > "
              "New repository secret, nombre BOOKING_ICAL_URL, y pega el enlace de exportación de Booking.", file=sys.stderr)
        return 2
    out = os.environ.get("AVAIL_FILE") or str(ROOT / "availability.json")
    try:
        check_url(url, allow_local)
        text = download(url)
        today = madrid_today()
        wrote, summary = sync(text, out, today, closed_from=os.environ.get("CLOSED_FROM"))
    except SyncError as e:
        print("ERROR: %s. Se conserva el calendario anterior." % e, file=sys.stderr)
        return 1
    print(summary)
    print("availability.json: %s" % ("escrito" if wrote else "sin tocar"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
