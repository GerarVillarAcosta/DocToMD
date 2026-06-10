import { render, screen, fireEvent } from '@testing-library/react'
import FileUpload from './FileUpload.jsx'

describe('FileUpload', () => {
  it('shows upload prompt when no file selected', () => {
    render(<FileUpload file={null} onFileChange={() => {}} />)
    expect(screen.getByText(/arrastra o selecciona/i)).toBeInTheDocument()
  })

  it('shows change prompt when a file is present', () => {
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    render(<FileUpload file={file} onFileChange={() => {}} />)
    expect(screen.getByText(/cambiar archivo/i)).toBeInTheDocument()
  })

  it('calls onFileChange when a file is selected via input', () => {
    const onFileChange = vi.fn()
    render(<FileUpload file={null} onFileChange={onFileChange} />)
    const input = document.querySelector('input[type="file"]')
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    Object.defineProperty(input, 'files', { value: [file] })
    fireEvent.change(input)
    expect(onFileChange).toHaveBeenCalledWith(file)
  })

  it('calls onFileChange on drop', () => {
    const onFileChange = vi.fn()
    render(<FileUpload file={null} onFileChange={onFileChange} />)
    const dropZone = screen.getByRole('button', { name: /upload file/i })
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    fireEvent.drop(dropZone, { dataTransfer: { files: [file] } })
    expect(onFileChange).toHaveBeenCalledWith(file)
  })
})
