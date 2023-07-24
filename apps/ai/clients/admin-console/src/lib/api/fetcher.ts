export const apiFetcher = async <T>(
  url: string,
  options?: RequestInit,
): Promise<T> => {
  const headers = {
    'Content-Type': 'application/json',
    ...(options?.headers || {}),
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = new Error('An error occurred while fetching the data.')
    throw error
  }

  return response.json()
}
