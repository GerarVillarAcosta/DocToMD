import { useState } from 'react'
import FileUpload from './components/FileUpload.jsx'
import EngineSelector from './components/EngineSelector.jsx'
import MarkdownPreview from './components/MarkdownPreview.jsx'
import { convertFile } from './api/client.js'
import './App.css'

export default function App() {
  const [file, setFile] = useState(null)
  const [engine, setEngine] = useState('markitdown')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileChange = (newFile) => {
    setFile(newFile)
    setResult(null)
    setError(null)
  }

  const handleConvert = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const data = await convertFile(file, engine)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>DocToMD</h1>
      </header>
      <main className="app-main">
        <section className="panel panel-left">
          <FileUpload file={file} onFileChange={handleFileChange} />
          {file && (
            <p className="file-info">
              {file.name} · {(file.size / 1024 / 1024).toFixed(1)} MB
            </p>
          )}
          <EngineSelector value={engine} onChange={setEngine} />
          <button
            className="btn-convert"
            onClick={handleConvert}
            disabled={!file || loading}
          >
            {loading ? 'Convirtiendo...' : 'Convertir'}
          </button>
          {error && <p className="error">{error}</p>}
        </section>
        <section className="panel panel-right">
          <MarkdownPreview markdown={result?.markdown} loading={loading} />
        </section>
      </main>
    </div>
  )
}
