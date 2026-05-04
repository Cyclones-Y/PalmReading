const JSON_HEADERS = {
  Accept: 'application/json'
}

export async function createPalmReading(file, handSide) {
  const body = new FormData()
  body.append('image', file)
  body.append('handSide', handSide)
  const response = await fetch('/api/v1/palm-readings', {
    method: 'POST',
    body,
    headers: JSON_HEADERS
  })
  return parseResponse(response)
}

export async function getPalmReading(readingId) {
  const response = await fetch(`/api/v1/palm-readings/${readingId}`, {
    headers: JSON_HEADERS
  })
  return parseResponse(response)
}

export async function getPublicReading(shareToken) {
  const response = await fetch(`/api/v1/public-readings/${shareToken}`, {
    headers: JSON_HEADERS
  })
  return parseResponse(response)
}

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = payload.detail || '请求失败，请稍后再试'
    const error = new Error(message)
    error.status = response.status
    throw error
  }
  return payload
}
