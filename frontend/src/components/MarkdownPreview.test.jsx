import { render, screen } from '@testing-library/react'
import MarkdownPreview from './MarkdownPreview.jsx'

describe('MarkdownPreview', () => {
  it('shows empty state when no markdown', () => {
    render(<MarkdownPreview markdown={null} loading={false} />)
    expect(screen.getByText(/resultado aparecerá aquí/i)).toBeInTheDocument()
  })

  it('shows spinner while loading', () => {
    render(<MarkdownPreview markdown={null} loading={true} />)
    expect(screen.getByLabelText('loading')).toBeInTheDocument()
  })

  it('renders markdown heading as HTML', () => {
    render(<MarkdownPreview markdown="# Hello World" loading={false} />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Hello World')
  })

  it('shows copy and download buttons when markdown is present', () => {
    render(<MarkdownPreview markdown="# Hello" loading={false} />)
    expect(screen.getByText('Copiar MD')).toBeInTheDocument()
    expect(screen.getByText('Descargar .md')).toBeInTheDocument()
  })
})
