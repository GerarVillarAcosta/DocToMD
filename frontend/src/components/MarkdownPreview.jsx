import ReactMarkdown from 'react-markdown'

export default function MarkdownPreview({ markdown, loading }) {
  if (loading) {
    return <div className="spinner" aria-label="loading">Convirtiendo...</div>
  }
  if (!markdown) {
    return <div className="preview-empty">El resultado aparecerá aquí</div>
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown)
  }

  const handleDownload = () => {
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'resultado.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="preview">
      <div className="preview-actions">
        <button onClick={handleCopy}>Copiar MD</button>
        <button onClick={handleDownload}>Descargar .md</button>
      </div>
      <div className="preview-content">
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </div>
    </div>
  )
}
