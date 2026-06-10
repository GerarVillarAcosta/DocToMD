# DocToMD

Convierte documentos a Markdown desde una interfaz web. Sube un PDF, imagen, Word, PowerPoint o Excel y obtén el contenido en Markdown limpio, listo para copiar o descargar.

---

## ¿Cómo funciona?

La app tiene dos partes:

- **Backend (Python / FastAPI)** — recibe el archivo, lo procesa con el motor de conversión elegido y devuelve el Markdown resultante.
- **Frontend (React)** — interfaz de dos paneles: sube el archivo a la izquierda, lee el resultado renderizado a la derecha.

Todo corre en un único contenedor Docker. No requiere configuración adicional.

### Motores de conversión

| Motor | Velocidad | Mejor para |
|---|---|---|
| **markitdown** (Microsoft) | Rápido | DOCX, PPTX, XLSX, imágenes, PDFs simples |
| **Docling** (IBM) | Lento | PDFs complejos con tablas, columnas múltiples y layouts densos |

---

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo.

---

## Cómo ejecutarlo

```bash
git clone https://github.com/GerarVillarAcosta/DocToMD.git
cd DocToMD
docker compose up --build
```

Abre [http://localhost:8000](http://localhost:8000) en el navegador.

> La primera build tarda entre 10 y 15 minutos porque Docling descarga sus modelos (~1–2 GB). Las siguientes builds son instantáneas si el código no cambia.

---

## Uso

1. Arrastra o selecciona un archivo en el panel izquierdo.
2. Elige el motor de conversión (pasa el cursor por encima para ver cuál usar).
3. Haz clic en **Convertir**.
4. Lee el resultado renderizado en el panel derecho.
5. Usa **Copiar MD** para copiar el Markdown al portapapeles, o **Descargar .md** para guardarlo.

---

## Formatos soportados

`PDF` `DOCX` `PPTX` `XLSX` `PNG` `JPG` `JPEG` `WEBP`

---

## Stack

- **Backend:** Python 3.12 + FastAPI + Uvicorn
- **Frontend:** React 18 + Vite + react-markdown
- **Conversión:** markitdown (Microsoft) · Docling (IBM)
- **Deploy:** Docker (imagen única, multi-stage build)
