const ENGINES = [
  {
    id: 'markitdown',
    label: 'markitdown',
    tip: 'Rápido. Ideal para DOCX, PPTX, XLSX e imágenes. Buena cobertura general.',
  },
  {
    id: 'docling',
    label: 'Docling',
    tip: 'Alta fidelidad. Mejor para PDFs complejos con tablas, columnas y layouts densos.',
  },
]

export default function EngineSelector({ value, onChange }) {
  return (
    <div className="engine-selector">
      <span className="engine-label">Motor de conversión</span>
      <div className="engine-buttons">
        {ENGINES.map(({ id, label, tip }) => (
          <div key={id} className="engine-btn-wrap">
            <button
              className={`engine-btn${value === id ? ' active' : ''}`}
              onClick={() => onChange(id)}
            >
              {label}
            </button>
            <div className="engine-tooltip">{tip}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
