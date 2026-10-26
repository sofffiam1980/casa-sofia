# Casa Sofía en Grazalema: web con calendario automático

Esta carpeta es la web completa, lista para GitHub. Cada 2 horas, aproximadamente, una tarea de GitHub lee tu calendario de Booking.com, actualiza las noches ocupadas y vuelve a publicar la web. Tú solo tienes que hacer una vez los pasos de abajo (unos 10 minutos).

Sentido único: lo que se cierra o se reserva en Booking aparece ocupado en la web. Lo que se reserva en la web (por WhatsApp) no pasa solo a Booking: bloquea esas noches en el panel de la web (para que no se puedan volver a reservar enseguida) y ciérralas también a mano en Booking (la noche de salida no se cierra: del 3 al 6 de noviembre se cierran las noches del 3, 4 y 5). Las noches que cierres en Booking aparecen ocupadas en la web al cabo de unas horas.

## Qué hay en la carpeta

- `index.html`, `img/`: la web y sus fotos.
- `availability.json`: el calendario. Lo reescribe la tarea automática.
- `configuracion-reservas.json`: precio por noche, estancia mínima, descuentos por noche, temporadas, fechas bloqueadas a mano, mascota y fianza. Lo cambias desde el panel de la web; ver `RESERVAS-como-cambiarlas.md`.
- `RESERVAS-como-cambiarlas.md`: cómo usar el panel de administración y conectar GitHub, paso a paso.
- `tools/`: el programa que lee el calendario de Booking y el que comprueba la configuración.
- `workflow-para-pegar.txt`: las instrucciones de la tarea automática (se pega en el paso 5).

## Antes de empezar

- Una cuenta gratuita en github.com.
- El enlace de exportación del calendario de Booking (el que empieza por `https://ical.booking.com/`). Es secreto: quien lo tenga puede ver tus noches ocupadas. Solo se pega en el paso 3, nunca en un archivo.

## Paso 1. Crear el repositorio

En GitHub pulsa el botón `+` (arriba a la derecha) y luego `New repository`.

- Repository name: `casa-sofia` (la dirección de la web será `https://TU-USUARIO.github.io/casa-sofia/`).
- Elige `Public`. Las páginas gratuitas de GitHub necesitan que sea público; el enlace secreto de Booking no se ve nunca, porque va guardado como secreto.
- No marques ninguna casilla (ni README, ni .gitignore, ni licencia).
- Pulsa `Create repository`.

## Paso 2. Subir los archivos

En el repositorio vacío pulsa el enlace `uploading an existing file`.

1. Descomprime el zip.
2. Abre la carpeta `casa-sofia-github` y selecciona todo lo que hay dentro (`index.html`, `availability.json`, `configuracion-reservas.json`, `README.md`, `RESERVAS-como-cambiarlas.md`, `workflow-para-pegar.txt` y las carpetas `img` y `tools`).
3. Arrástralo a la ventana de GitHub (no el zip) y espera a que termine de cargar.
4. Abajo pulsa `Commit changes`.

Comprueba que en la lista del repositorio aparecen `img`, `tools`, `index.html`, `availability.json`, `configuracion-reservas.json`, `README.md`, `RESERVAS-como-cambiarlas.md` y `workflow-para-pegar.txt`.

## Paso 3. Guardar el enlace secreto de Booking

1. En el repositorio entra en `Settings` (la pestaña de la derecha) y luego, en el menú de la izquierda, `Secrets and variables` y `Actions`.
2. Pulsa `New repository secret`.
3. Name: `BOOKING_ICAL_URL` (exactamente así, en mayúsculas y con los guiones bajos).
4. Secret: pega tu enlace de exportación de Booking.
5. Pulsa `Add secret`.

Una vez guardado nadie puede volver a verlo, ni tú. Si algún día generas un enlace nuevo en Booking, repite estos pasos con el mismo nombre para sustituirlo.

## Paso 4. Activar GitHub Pages

En `Settings`, menú de la izquierda `Pages`. En `Build and deployment`, en `Source`, elige `GitHub Actions` (no `Deploy from a branch`).

## Paso 5. Crear la tarea automática

1. Vuelve a la pestaña `Code`, pulsa `Add file` y luego `Create new file`.
2. En el cuadro del nombre escribe exactamente `.github/workflows/calendario-y-web.yml` (al escribir cada `/` se crea una carpeta).
3. Abre `workflow-para-pegar.txt` con el Bloc de notas (o TextEdit), copia todo el contenido y pégalo en el cuadro grande.
4. Pulsa `Commit changes` y confirma.

Al guardar, la tarea se lanza sola por primera vez.

## Paso 6. Comprobar que funciona

1. Entra en la pestaña `Actions`. Verás `Calendario y web` ejecutándose (círculo amarillo). En 1 o 2 minutos debe salir una marca verde.
2. En `Settings` y `Pages` aparecerá `Your site is live at ...`. Abre esa dirección.
3. Mira el calendario de reservas: las noches cerradas en Booking deben salir tachadas.

Si sale una cruz roja, abre esa ejecución y pulsa en el paso que falla. Los mensajes más habituales:

- `falta el secreto BOOKING_ICAL_URL`: repite el paso 3 y escribe el nombre exactamente igual.
- `Booking.com rechaza el enlace`: el enlace ha caducado o está mal copiado; genera uno nuevo en Booking y repite el paso 3.
- `la respuesta no es un calendario iCal`: lo mismo, el enlace no es el de exportación del calendario.
- `Get Pages site failed` o `Not Found` al publicar: falta el paso 4 (Source: GitHub Actions). Hazlo y en `Actions` pulsa `Run workflow`.

## Día a día

- No tienes que hacer nada: cada 2 horas, más o menos, se revisa el calendario. GitHub puede retrasar las tareas programadas unos minutos o más en horas de mucha carga, y Booking tarda un tiempo en reflejar sus propios cambios.
- Para actualizar al momento: pestaña `Actions`, `Calendario y web`, `Run workflow`, `Run workflow`.
- Para cambiar precios, descuentos, temporadas o fechas bloqueadas: el panel de la web (apartado Precios y reservas, más abajo).
- Para cambiar la web: sube un nuevo `index.html` (o fotos) con `Add file` y `Upload files`. Se republica sola.
- Si algo falla, GitHub te manda un correo. El calendario que se ve en la web sigue siendo el último que se leyó bien; si pasan más de 3 días sin actualizarse, la web muestra un aviso.

## Precios y reservas (panel de administración)

El calendario de Reservar enseña el precio de cada noche libre (170 € por toda la casa), aplica el descuento por noche (10 % desde la noche 3 y 25 % desde la noche 6), exige una estancia mínima (2 noches, o la de la temporada si hay una), suma la mascota (20 € por estancia, si el visitante la marca), indica la fianza (150 €) y escribe el total en el mensaje de WhatsApp. Las noches de Booking salen tachadas solas.

Todo eso, y las fechas que quieras bloquear a mano, se cambia desde el panel de administración: abre tu web, baja al final de la página y pulsa el enlace pequeño **Acceso del propietario** (junto al candado), entra con tu contraseña y conecta una vez la clave de GitHub. Los cambios se publican solos en 1 o 2 minutos. Los pasos, con los permisos que necesita la clave, están en `RESERVAS-como-cambiarlas.md`.

Detrás del panel hay un solo archivo, `configuracion-reservas.json`, que también se puede editar a mano en GitHub (el lápiz). Antes de publicar, GitHub lo comprueba: si hay un fallo te llega un correo y la web se queda con la configuración anterior.

## Fechas que Booking todavía no ha abierto

El calendario de Booking solo indica las noches cerradas o reservadas; las noches que nunca se abrieron (sin tarifas) no aparecen y la web las mostraría libres aunque no se puedan reservar. Ahora mismo Booking no vende nada desde el 1 de febrero de 2027, y eso está indicado en la tarea con la línea `CLOSED_FROM: "2027-02-01"`.

Cuando abras fechas nuevas en Booking, edita esa línea: `Code`, `.github`, `workflows`, `calendario-y-web.yml`, el lápiz de arriba a la derecha, y bórrala (o pon la nueva fecha, con el formato AAAA-MM-DD). Si la fecha ya ha pasado, se ignora sola.

## Cosas que conviene saber

- Si el repositorio pasa 60 días sin actividad, GitHub puede desactivar las tareas programadas de los repositorios públicos. La tarea guarda el calendario al menos una vez al día, lo que debería contar como actividad. Si GitHub te avisa de que la desactivó, entra en `Actions`, `Calendario y web` y pulsa `Enable workflow`.
- Cualquiera puede ver el código, el archivo `availability.json` (las noches ocupadas, que la web ya muestra) y `configuracion-reservas.json` (precios, descuentos, temporadas y fechas bloqueadas, sin las etiquetas que escribes en el panel).
- La contraseña del panel solo cierra la puerta del panel en el navegador; quien protege de verdad la web es la clave de GitHub, que se guarda solo en tu navegador. Si la pierdes o sospechas de ella, bórrala en GitHub (Settings, Developer settings, Personal access tokens) y crea otra. El enlace de Booking no se guarda en ningún archivo ni aparece en los registros: GitHub lo oculta y el programa nunca lo imprime.
- Esta tarea no puede crear reservas en Booking. Solo lee su calendario.
- En la portada, junto a la foto de la chimenea, aparece la foto del cartel «Uno de los pueblos más bonitos de España: Grazalema» (`img/pueblosbonitos.jpg`), enlazada a la ficha de Grazalema en la web de la asociación. El logotipo es de la asociación: la foto debe ser tuya o tener permiso. Para quitarla, borra el enlace `hero__sign` de `index.html`.
- Algunas fotos del pueblo y de las rutas (Grazalema, la plaza, una calle, el Pinsapar, la Garganta Verde, El Torreón, los Llanos del Endrinal, la Calzada Romana, el Salto del Cabrero, el Llano del Republicano, el Río Majaceite, la Cueva del Gato, la calzada medieval de Grazalema, la fábrica de mantas, el monumento al toro de cuerda, la plaza con banderines, una vista panorámica del pueblo y otra con nieve) son de Wikimedia Commons y tienen licencia libre CC BY-SA. La licencia obliga a mostrar el autor y la licencia junto a cada foto; la web ya lo hace (línea "Foto: autor · CC BY-SA · Wikimedia Commons" bajo cada una) y lo repite en el pie. Si cambias esas fotos o las quitas de la web, quita también su crédito.
