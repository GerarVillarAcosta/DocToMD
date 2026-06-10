import { convertFile } from './client.js'

describe('convertFile', () => {
  it('sends multipart form and returns JSON on success', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ markdown: '# Hello', engine: 'markitdown', filename: 'test.pdf' }),
    })
    const file = new File(['content'], 'test.pdf')
    const result = await convertFile(file, 'markitdown')
    expect(result.markdown).toBe('# Hello')
    expect(fetch).toHaveBeenCalledWith('/api/v1/convert', expect.objectContaining({ method: 'POST' }))
  })

  it('throws with detail message when response is not ok', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ detail: 'Unsupported format: .xyz' }),
    })
    const file = new File(['content'], 'test.xyz')
    await expect(convertFile(file, 'markitdown')).rejects.toThrow('Unsupported format: .xyz')
  })
})
