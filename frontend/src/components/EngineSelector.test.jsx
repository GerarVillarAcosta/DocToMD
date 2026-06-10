import { render, screen, fireEvent } from '@testing-library/react'
import EngineSelector from './EngineSelector.jsx'

describe('EngineSelector', () => {
  it('renders both engine buttons', () => {
    render(<EngineSelector value="markitdown" onChange={() => {}} />)
    expect(screen.getByText('markitdown')).toBeInTheDocument()
    expect(screen.getByText('Docling')).toBeInTheDocument()
  })

  it('marks active engine with active class', () => {
    render(<EngineSelector value="docling" onChange={() => {}} />)
    expect(screen.getByText('Docling')).toHaveClass('active')
    expect(screen.getByText('markitdown')).not.toHaveClass('active')
  })

  it('calls onChange when a button is clicked', () => {
    const onChange = vi.fn()
    render(<EngineSelector value="markitdown" onChange={onChange} />)
    fireEvent.click(screen.getByText('Docling'))
    expect(onChange).toHaveBeenCalledWith('docling')
  })

  it('renders tooltip text for each engine', () => {
    render(<EngineSelector value="markitdown" onChange={() => {}} />)
    expect(screen.getByText(/ideal para DOCX/i)).toBeInTheDocument()
    expect(screen.getByText(/alta fidelidad/i)).toBeInTheDocument()
  })
})
