# DocToMD

Convierte documentos a Markdown desde una aplicación de escritorio nativa. Abre un PDF, imagen, Word, PowerPoint o Excel y obtén el contenido en Markdown limpio, listo para copiar o descargar.

---

## ¿Cómo funciona?

- **UI nativa (PyQt6)** — dos paneles: sube el archivo a la izquierda, lee el resultado renderizado a la derecha.
- **Detección de hardware** — al primer arranque detecta tu GPU automáticamente e instala solo las dependencias necesarias (CUDA, ROCm o CPU).
- **Sin servidor, sin Docker** — todo corre localmente en tu máquina.

### Motores de conversión

| Motor | Velocidad | Mejor para |
|---|---|---|
| **markitdown** (Microsoft) | Rápido | DOCX, PPTX, XLSX, imágenes, PDFs simples |
| **Docling** (IBM) | Lento | PDFs complejos con tablas, columnas múltiples y layouts densos |

---

## Requisitos

- Python 3.11 o superior
- Conexión a internet (solo en el primer arranque, para descargar dependencias)

---

## Iniciar el programa

### Windows

Doble-clic en `DocToMD.pyw`.

- **Primera vez:** se abre una ventana que instala las dependencias automáticamente, luego abre la app.
- **Siguientes veces:** abre directo, sin ninguna ventana de consola.

### Unix

```bash
python3 DocToMD.pyw
```

- **Primera vez:** instala las dependencias automáticamente en la terminal, luego abre la app.
- **Siguientes veces:** abre directo.

> La primera ejecución puede tardar varios minutos — descarga Docling y PyTorch con soporte para tu GPU (~2–4 GB).

---

## Uso

1. Arrastra o selecciona un archivo en el panel izquierdo.
2. Elige el motor de conversión (pasa el cursor para ver cuál usar).
3. Haz clic en **Convertir**.
4. Lee el resultado renderizado en el panel derecho.
5. Usa **Copiar MD** para copiar al portapapeles, o **Descargar .md** para guardarlo.

---

## Desinstalar

### Windows

Doble-clic en `uninstall.pyw` y confirma en el diálogo que aparece.

Elimina: PyQt6, markitdown, docling, torch y todas sus dependencias, además del perfil de hardware guardado en `%USERPROFILE%\.config\doctomd\`.

### Unix

```bash
python3 uninstall.pyw
```

Elimina: PyQt6, markitdown, docling, torch y todas sus dependencias, además del perfil de hardware guardado en `~/.config/doctomd/`.

Después puedes borrar la carpeta del proyecto manualmente.

---

## Formatos soportados

`PDF` `DOCX` `PPTX` `XLSX` `PNG` `JPG` `JPEG` `WEBP`

---

## Stack

- **UI:** Python 3.11+ + PyQt6
- **Conversión:** markitdown (Microsoft) · Docling (IBM)
- **Detector de hardware:** C (compilado en primer arranque)
- **GPU:** NVIDIA CUDA · AMD ROCm · CPU (detectado automáticamente)
