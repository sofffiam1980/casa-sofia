"""Comprueba configuracion-reservas.json y dice, en cristiano, que ha entendido (o que esta mal).

Se usa en tres sitios: al construir la web (tools/build.py), en la tarea automática de GitHub antes de
publicar, y a mano:   python3 tools/check_config.py configuracion-reservas.json

Normalmente NO hace falta tocarlo a mano: se cambia desde el panel de administración de la web (?admin=1).
Formato (las fechas son AAAA-MM-DD; los precios son por NOCHE y por TODA la casa, en euros):

    {
      "precioBase": 170,                       precio normal de la noche
      "nochesMinimas": 2,                      mínimo de noches para reservar (1 = sin mínimo)
      "descuentos": [                          descuento por noche, según el número de noche de la estancia
        {"desde": 3, "pct": 10},               noches 3 a 5: 10 %
        {"desde": 6, "pct": 25}                desde la noche 6: 25 %
      ],
      "temporadas": [                          fechas con otro precio y/o otra estancia mínima
        {"nombre": "Navidad", "desde": "2026-12-24", "hasta": "2027-01-02", "precio": 220, "minNoches": 4}
      ],
      "bloqueos": [                            noches que no se pueden reservar (aparte de las de Booking)
        {"id": "a1", "etiqueta": "Reservado", "tipo": "rango", "desde": "2026-11-01", "hasta": "2026-11-03"}
      ],
      "mascota": 20,                           suplemento por mascota, una vez por estancia
      "fianza": 150                            fianza de las reservas directas
    }

En las temporadas, "precio" y "minNoches" son opcionales (hace falta al menos uno): sin "precio" vale el precio
base; sin "minNoches" vale la estancia mínima general. La estancia mínima de una temporada vale para las
reservas cuyo día de ENTRADA cae en esas fechas. "desde" y "hasta" cuentan los dos (son noches).
Las claves que empiezan por "_" son notas y la web las ignora.
"""
import datetime as dt
import json
import pathlib
import re
import sys

MAX_PRICE = 9999
MAX_NIGHTS = 365
MAX_SPAN_DAYS = 1500
TOP_KEYS = {"precioBase", "nochesMinimas", "descuentos", "temporadas", "bloqueos", "mascota", "fianza"}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _date(v):
    if not isinstance(v, str) or not DATE_RE.fullmatch(v):
        return None
    try:
        return dt.date.fromisoformat(v)
    except ValueError:
        return None


def _price_ok(v):
    return _num(v) and 0 < v <= MAX_PRICE and abs(v * 100 - round(v * 100)) < 1e-6


def fmt(v):
    """180 -> '180', 180.5 -> '180,50' (Spanish decimal comma)."""
    if float(v).is_integer():
        return str(int(v))
    return ("%.2f" % v).replace(".", ",")


def _d(d):
    return d.strftime("%d/%m/%Y")


def check(data):
    """Returns (errors, summary_lines). errors is a list of Spanish messages; empty means valid."""
    errors, lines = [], []
    if not isinstance(data, dict):
        return ["El archivo tiene que empezar con { y acabar con } (un objeto con 'precioBase', 'nochesMinimas'...)."], lines
    for k in data:
        if k not in TOP_KEYS and not str(k).startswith("_"):
            errors.append("Hay una palabra que no conozco: \"%s\". Solo valen precioBase, nochesMinimas, descuentos, temporadas, bloqueos, mascota y fianza (las notas deben empezar por _)." % k)

    if "precioBase" not in data:
        errors.append("Falta la línea \"precioBase\": 170 (el precio normal de la noche).")
    elif not _price_ok(data["precioBase"]):
        errors.append("\"precioBase\" tiene que ser un número mayor que 0 y como mucho %d, sin comillas ni el símbolo del euro (por ejemplo 170)." % MAX_PRICE)
    else:
        lines.append("Precio normal: %s € por noche (toda la casa)." % fmt(data["precioBase"]))

    if "nochesMinimas" not in data:
        errors.append("Falta la línea \"nochesMinimas\": 2 (el mínimo de noches para reservar).")
    elif not (_int(data["nochesMinimas"]) and 1 <= data["nochesMinimas"] <= MAX_NIGHTS):
        errors.append("\"nochesMinimas\" tiene que ser un número entero entre 1 y %d, sin comillas (por ejemplo 2)." % MAX_NIGHTS)
    else:
        n = data["nochesMinimas"]
        lines.append("Estancia mínima: %d noche%s%s." % (n, "" if n == 1 else "s", " (sin mínimo)" if n == 1 else ""))

    for key, label, what, example in (("mascota", "Mascota", "por estancia (no por noche)", 20), ("fianza", "Fianza", "en reservas directas", 150)):
        if key not in data:
            errors.append("Falta la línea \"%s\": %d (el importe en euros)." % (key, example))
        elif not _price_ok(data[key]):
            errors.append("\"%s\" tiene que ser un número mayor que 0 y como mucho %d, sin comillas ni el símbolo del euro (por ejemplo %d)." % (key, MAX_PRICE, example))
        else:
            lines.append("%s: %s € %s." % (label, fmt(data[key]), what))

    desc = data.get("descuentos", [])
    if not isinstance(desc, list):
        errors.append("\"descuentos\" tiene que ser una lista entre corchetes [ ... ].")
        desc = []
    seen = set()
    tiers = []
    for i, t in enumerate(desc, 1):
        where = "En \"descuentos\", línea %d" % i
        if not isinstance(t, dict) or not _int(t.get("desde")) or not 1 <= t["desde"] <= MAX_NIGHTS:
            errors.append("%s: hace falta {\"desde\": 3, \"pct\": 10} (\"desde\" = número de noche, de 1 a %d)." % (where, MAX_NIGHTS))
            continue
        if not _num(t.get("pct")) or not 0 <= t["pct"] <= 100:
            errors.append("%s: \"pct\" tiene que ser un número de 0 a 100 (el porcentaje de descuento)." % where)
            continue
        if t["desde"] in seen:
            errors.append("%s: la noche %d aparece dos veces." % (where, t["desde"]))
            continue
        seen.add(t["desde"])
        tiers.append(t)
    tiers.sort(key=lambda t: t["desde"])
    for i, t in enumerate(tiers):
        end = tiers[i + 1]["desde"] - 1 if i + 1 < len(tiers) else None
        rng = "Desde la noche %d" % t["desde"] if end is None else ("Noche %d" % t["desde"] if end == t["desde"] else "Noches %d a %d" % (t["desde"], end))
        lines.append("%s: %s %% de descuento en cada noche." % (rng, fmt(t["pct"])))

    temps = data.get("temporadas", [])
    if not isinstance(temps, list):
        errors.append("\"temporadas\" tiene que ser una lista entre corchetes [ ... ].")
        temps = []
    for i, s in enumerate(temps, 1):
        where = "En \"temporadas\", línea %d" % i
        if not isinstance(s, dict):
            errors.append("%s: cada temporada tiene que ir entre llaves { ... }." % where)
            continue
        bad = [k for k in s if k not in {"nombre", "desde", "hasta", "precio", "minNoches"} and not str(k).startswith("_")]
        if bad:
            errors.append("%s: no conozco \"%s\". Solo valen nombre, desde, hasta, precio y minNoches." % (where, bad[0]))
        a, b = _date(s.get("desde")), _date(s.get("hasta"))
        ok = True
        if not isinstance(s.get("nombre"), str) or not s["nombre"].strip():
            errors.append("%s: falta el \"nombre\" de la temporada." % where)
            ok = False
        if a is None or b is None:
            errors.append("%s: \"desde\" y \"hasta\" tienen que ser fechas reales escritas así: \"2026-12-31\" (año-mes-día, con comillas)." % where)
            ok = False
        elif b < a:
            errors.append("%s: \"hasta\" (%s) es anterior a \"desde\" (%s)." % (where, s.get("hasta"), s.get("desde")))
            ok = False
        elif (b - a).days > MAX_SPAN_DAYS:
            errors.append("%s: la temporada es demasiado larga (máximo %d días)." % (where, MAX_SPAN_DAYS))
            ok = False
        pr, mn = s.get("precio"), s.get("minNoches")
        if pr is None and mn is None:
            errors.append("%s: pon un \"precio\", un \"minNoches\", o los dos." % where)
            ok = False
        if pr is not None and not _price_ok(pr):
            errors.append("%s: \"precio\" tiene que ser un número mayor que 0 y como mucho %d (por ejemplo 200)." % (where, MAX_PRICE))
            ok = False
        if mn is not None and not (_int(mn) and 1 <= mn <= MAX_NIGHTS):
            errors.append("%s: \"minNoches\" tiene que ser un número entero entre 1 y %d." % (where, MAX_NIGHTS))
            ok = False
        if ok:
            parts = []
            if pr is not None:
                parts.append("%s € por noche" % fmt(pr))
            if mn is not None:
                parts.append("estancia mínima %d noche%s" % (mn, "" if mn == 1 else "s"))
            lines.append("%s (%s al %s): %s." % (s["nombre"].strip(), _d(a), _d(b), ", ".join(parts)))

    blocks = data.get("bloqueos", [])
    if not isinstance(blocks, list):
        errors.append("\"bloqueos\" tiene que ser una lista entre corchetes [ ... ].")
        blocks = []
    nb = 0
    for i, b in enumerate(blocks, 1):
        where = "En \"bloqueos\", línea %d" % i
        if not isinstance(b, dict):
            errors.append("%s: cada bloqueo tiene que ir entre llaves { ... }." % where)
            continue
        a = _date(b.get("desde"))
        z = _date(b.get("hasta", b.get("desde")))
        if a is None or z is None:
            errors.append("%s: \"desde\" y \"hasta\" tienen que ser fechas reales escritas así: \"2026-12-31\"." % where)
        elif z < a:
            errors.append("%s: \"hasta\" (%s) es anterior a \"desde\" (%s)." % (where, b.get("hasta"), b.get("desde")))
        elif (z - a).days > MAX_SPAN_DAYS:
            errors.append("%s: el bloqueo es demasiado largo (máximo %d días)." % (where, MAX_SPAN_DAYS))
        else:
            nb += 1
    lines.append("Fechas bloqueadas a mano: %d." % nb if nb else "Sin fechas bloqueadas a mano.")
    return errors, lines


def load(path):
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8")
    except OSError as ex:
        return None, ["No se puede abrir %s: %s" % (path, ex)]
    try:
        return json.loads(text), []
    except json.JSONDecodeError as ex:
        return None, ["El archivo no se puede leer (línea %d, columna %d): %s. Suele ser una coma de más o de menos, unas comillas que faltan, o una llave sin cerrar." % (ex.lineno, ex.colno, ex.msg)]


def main(argv):
    path = argv[1] if len(argv) > 1 and not argv[1].startswith("--") else "configuracion-reservas.json"
    data, errs = load(path)
    lines = []
    if not errs:
        errs, lines = check(data)
    for ln in lines:
        print("  " + ln)
    if errs:
        for e in errs:
            print("::error file=%s::%s" % (path, e) if "--gh" in argv else "ERROR: " + e)
        print("\nEl archivo de reservas tiene fallos. La web se queda con la configuración anterior hasta que lo arregles.")
        return 1
    print("Archivo de reservas correcto.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
