import { useRef } from 'react'

const ACCEPTED = '.pdf,.docx,.pptx,.xlsx,.png,.jpg,.jpeg,.webp'

export default function FileUpload({ file, onFileChange }) {
  const inputRef = useRef(null)

  const handleDrop = (e) => {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (dropped) onFileChange(dropped)
  }

  const handleDragOver = (e) => e.preventDefault()

  const handleClick = () => inputRef.current?.click()

  const handleInput = (e) => {
    const selected = e.target.files[0]
    if (selected) onFileChange(selected)
  }

  return (
    <div
      className={`drop-zone${file ? ' has-file' : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onClick={handleClick}
      role="button"
      aria-label="Upload file"
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        onChange={handleInput}
        style={{ display: 'none' }}
      />
      <span>{file ? '↑ Cambiar archivo' : '↑ Arrastra o selecciona'}</span>
      <small>PDF · DOCX · PPTX · XLSX · Imágenes</small>
    </div>
  )
}
