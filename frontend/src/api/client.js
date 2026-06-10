export async function convertFile(file, engine) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('engine', engine)

  const response = await fetch('/api/v1/convert', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const err = await response.json()
    throw new Error(err.detail || 'Conversion failed')
  }

  return response.json()
}
