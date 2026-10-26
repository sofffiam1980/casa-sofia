# Cómo cambiar precios, descuentos, temporadas y fechas bloqueadas

Todo lo que controla el calendario de reservas de la web se cambia desde un **panel de administración** que está en la propia web. No hace falta editar archivos ni instalar nada. Lo que cambies se publica solo y tus clientes lo ven en 1 o 2 minutos.

Lo que se puede cambiar desde el panel:

- **Fechas bloqueadas**: noches que no se pueden reservar (una reserva directa, mantenimiento, uso propio...). Las noches cerradas o reservadas en Booking.com se bloquean solas, sin que hagas nada.
- **Precio por noche** (toda la casa), **estancia mínima**, **suplemento de mascota** (una vez por estancia) y **fianza**.
- **Descuento por noche**: por ejemplo, 10 % desde la noche 3 y 25 % desde la noche 6.
- **Temporadas**: unas fechas con otro precio, otra estancia mínima o las dos cosas.

## Cómo se ve para el visitante

El visitante elige entrada y salida en el calendario. La web le enseña el precio de cada noche, el descuento si lo hay, la mascota si la marca y el total. Ese total va escrito en el mensaje de WhatsApp que se abre al pulsar "Reservar por WhatsApp", así que no hay formulario: la reserva se cierra hablando contigo.

Reglas del calendario:

- Las noches de Booking y las que bloqueas tú salen tachadas y no se pueden elegir.
- El día de salida puede ser el primer día ocupado: quien sale el día que otro entra no ocupa esa noche.
- La estancia mínima general sale en un recuadro encima del calendario. Si una temporada tiene su propia estancia mínima, vale para las reservas cuyo **día de entrada** cae en esas fechas.
- El descuento se aplica **noche a noche**: con 10 % desde la noche 3, las dos primeras noches se cobran enteras y desde la tercera se cobran con descuento. No es un descuento sobre el total.
- La mascota se suma al total **una sola vez** y no lleva descuento. La fianza no entra en el total: se indica aparte.

## Entrar en el panel

1. Abre tu web (`https://TU-USUARIO.github.io/casa-sofia/`), baja hasta el final de la página y pulsa **Acceso del propietario**, el enlace pequeño con un candado que hay debajo de las letras pequeñas. (También puedes escribir `#admin` al final de la dirección: `https://TU-USUARIO.github.io/casa-sofia/#admin`.)
2. Escribe tu contraseña del panel y pulsa `Entrar`.

El enlace lo ve cualquiera que llegue al final de la página, pero sin la contraseña solo se ve la ventanita de la contraseña, nunca los ajustes. Funciona en la web publicada en GitHub (o en tu propio dominio si más adelante lo conectas). En la vista previa de Claude también se abre, pero ahí no se puede publicar ni descargar la copia: los cambios solo quedan en ese navegador.

La contraseña del panel solo cierra la puerta del panel en el navegador: la huella de la contraseña (no la contraseña en sí) viaja dentro de la página, que es pública. Lo que de verdad protege tu web es la **clave de GitHub** del siguiente apartado: sin ella nadie puede publicar cambios, aunque entre en el panel. Aun así, no uses en el panel una contraseña que tengas en otros sitios. Puedes cambiarla en el panel (`Cambiar contraseña`); el cambio vale solo en ese navegador.

## Conectar el panel con GitHub (una sola vez por navegador)

Hasta que lo conectes, los cambios solo se guardan en tu navegador y los clientes no los ven. El panel te lo dice arriba, en `Publicar en la web`.

1. En GitHub: tu foto, luego `Settings`, `Developer settings`, `Personal access tokens`, `Fine-grained tokens` y `Generate new token`.
2. Ponle un nombre (por ejemplo `panel casa sofia`) y una caducidad (lo máximo que te deje).
3. En `Repository access` elige `Only select repositories` y marca solo el repositorio `casa-sofia`.
4. En `Permissions`, `Repository permissions`, pon `Contents` en `Read and write`. No hace falta nada más.
5. Pulsa `Generate token` y copia la clave (empieza por `github_pat_`). GitHub solo la enseña una vez.
6. En el panel, en `Publicar en la web`, pega la clave y pulsa `Conectar y publicar`.

La clave se guarda solo en este navegador (nunca en la web ni en el repositorio). Si usas el panel desde otro ordenador o desde el móvil, repite el paso 6 allí. Si pierdes la clave o caduca, genera otra y pégala igual; con `Quitar clave` la borras de ese navegador.

A partir de ahí, cada cambio se publica solo: el panel sube `configuracion-reservas.json` al repositorio, GitHub lo revisa y vuelve a publicar la web. El botón `Publicar ahora` fuerza la subida si algún cambio se quedó sin publicar.

Qué se publica y qué no: las etiquetas de los bloqueos ("Reserva de Ana"...) **no se publican**; en el archivo público sale solo "Bloqueado" y tus etiquetas se quedan en el navegador donde las escribiste. El archivo de configuración publicado no lleva etiquetas ni contraseña.

## Fechas bloqueadas

En `Fechas bloqueadas` escribe una etiqueta si quieres (solo para ti), elige `Desde` y `Hasta (incluido)` y pulsa `Bloquear fechas`. Para un solo día deja `Hasta` vacío. Los dos días cuentan como noches: bloquear del 3 al 5 de noviembre bloquea las noches del 3, 4 y 5, y la salida es el día 6. Para quitar un bloqueo (o una temporada o un tramo de descuento), pulsa la `×` de su fila en la lista.

Cuando alguien reserve por WhatsApp, bloquea aquí esas noches y, además, ciérralas a mano en Booking (la tarea automática solo lee Booking, no escribe en él).

## Precio y condiciones

En `Precio y condiciones` cambia el precio por noche, la estancia mínima, la mascota o la fianza y pulsa `Guardar`. Los números se actualizan solos en todos los sitios de la web donde aparecen (los recuadros de encima del calendario, la casilla de la mascota, las condiciones de reserva y el mensaje de WhatsApp).

La estancia mínima 1 significa que no hay mínimo y el recuadro desaparece.

## Descuento por noche

Cada tramo vale desde la noche que indiques hasta que empieza el siguiente. Las noches anteriores al primer tramo se cobran enteras. Si añades un tramo con una noche que ya existe, lo sustituye. Debajo de la lista, el panel enseña ejemplos con el precio base para que veas el resultado.

Con los valores de ahora (10 % desde la noche 3 y 25 % desde la noche 6), una estancia de 7 noches a 170 € cuesta 2 × 170 + 3 × 153 + 2 × 127,50 = 1.054 €. Para no tener descuentos, borra todos los tramos.

## Temporadas

En `Temporadas` pones un nombre, las fechas (las dos cuentan) y, al menos, un precio o una estancia mínima. Lo que dejes vacío usa el valor general. Si dos temporadas se pisan en un día, para el precio gana la primera por fecha de comienzo.

Ejemplo: "Navidad", del 24/12/2026 al 02/01/2027, 220 € la noche y mínimo 4 noches.

## Copia de seguridad

`Descargar configuración` guarda un archivo con todo (incluidas tus etiquetas de bloqueos) y `Cargar configuración` lo vuelve a poner. Úsalo antes de cambios grandes. Ese archivo tiene tus etiquetas, así que no lo subas a ningún sitio público.

## Si algo no sale bien

- **El panel dice "Sin conectar"**: falta la clave de GitHub (apartado de arriba).
- **El panel dice que la clave no vale**: ha caducado o no tiene el permiso `Contents: Read and write` sobre el repositorio. Genera otra clave.
- **Publiqué un cambio y no lo veo**: espera 1 o 2 minutos y recarga la página. Puedes mirar en la pestaña `Actions` de GitHub si la tarea `Calendario y web` está en marcha (círculo amarillo) o ha terminado (marca verde).
- **Una cruz roja en `Actions`**: antes de publicar, GitHub comprueba el archivo. Si algo está mal, te llega un correo, la web se queda con la configuración anterior (nadie ve precios rotos) y el mensaje de la tarea explica en español qué falla. Vuelve a guardar desde el panel o corrige el archivo.
- **Si el archivo publicado no se pudiera leer**, la web funciona con los valores con que se construyó (precio, estancia mínima, descuentos, mascota y fianza). Las noches de Booking siguen bloqueadas porque vienen de otro archivo.

## Editar el archivo a mano (opcional)

El panel escribe un único archivo, `configuracion-reservas.json`, que también puedes editar a mano en GitHub (lápiz arriba a la derecha, `Commit changes`). Es lo que hay ahora:

    {
      "precioBase": 170,
      "nochesMinimas": 2,
      "descuentos": [
        { "desde": 3, "pct": 10 },
        { "desde": 6, "pct": 25 }
      ],
      "temporadas": [
        { "nombre": "Navidad", "desde": "2026-12-24", "hasta": "2027-01-02", "precio": 220, "minNoches": 4 }
      ],
      "bloqueos": [
        { "id": "a1", "etiqueta": "Bloqueado", "tipo": "rango", "desde": "2026-11-01", "hasta": "2026-11-03" }
      ],
      "mascota": 20,
      "fianza": 150
    }

(El ejemplo lleva una temporada y un bloqueo para que veas la forma; el archivo real puede tener las listas vacías, `[]`.)

- Las fechas se escriben `AAAA-MM-DD`, entre comillas. Los números, sin comillas ni símbolo del euro, y con punto para los decimales (`170.5`).
- En `bloqueos`, `tipo` es `"rango"` (con `desde` y `hasta`) o `"dia"` (un solo día, con `desde`).
- En las temporadas, `precio` y `minNoches` son opcionales, pero hace falta uno de los dos.
- Cuidado con las comas: hay una al final de cada línea menos la última de cada lista.
- Para comprobar el archivo antes de subirlo (opcional, si tienes Python): `python3 tools/check_config.py configuracion-reservas.json`.

Si editas el archivo a mano mientras tienes el panel abierto con la clave conectada, vuelve a cargar el panel antes de seguir, para que no pise tu cambio.

## Cosas que conviene saber

- Estos precios son los de la web. Booking.com no comparte sus tarifas en el calendario, así que si cambias un precio en Booking, cámbialo también aquí (y al revés).
- El total que ve el visitante es la suma de las noches (con su descuento) más la mascota si la marca, y el mensaje de WhatsApp dice que se confirma contigo. La web no suma limpieza ni otros extras: si los cobras, díselo al visitante en la conversación.
- La tarea automática del calendario no toca `configuracion-reservas.json`: el calendario de Booking se actualiza solo y la configuración solo cambia cuando tú la cambias.
- Los textos de cancelación (15 días de antelación sin penalización, excepto festivos o puentes), de pago y de devolución de la fianza (48 horas después del check-out, comprobado que todo está correcto) están escritos en la web, en "Antes de venir". Si cambian las condiciones, hay que actualizar la web; no salen de este archivo.
