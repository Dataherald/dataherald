import fetchMock from 'jest-fetch-mock'
import { serverFetcher } from './server-fetcher'

// Make sure to enable fetch mock before each test
beforeEach(() => {
  fetchMock.enableMocks()
})

// Reset all mocks after each test
afterEach(() => {
  fetchMock.resetMocks()
})

describe('serverFetcher', () => {
  test('Default config - GET request', async () => {
    fetchMock.mockOnce(JSON.stringify({ data: '12345' }))

    const data = await serverFetcher<{ data: string }>('/api/test')

    expect(data).toEqual({ data: '12345' })
    expect(fetchMock.mock.calls[0][1]?.method || 'GET').toEqual('GET')
    const headers = fetchMock.mock.calls[0][1]?.headers as Record<
      string,
      string
    >
    expect(headers['Content-Type']).toEqual('application/json')
  })

  it('POST request with JSON body', async () => {
    fetchMock.mockOnce(JSON.stringify({ result: 'success' }))

    const data = await serverFetcher<{ result: string }>('/api/test', {
      method: 'POST',
      body: JSON.stringify({ input: 'test' }),
    })

    expect(data).toEqual({ result: 'success' })
    expect(fetchMock.mock.calls[0][1]?.method).toEqual('POST')
    expect(fetchMock.mock.calls[0][1]?.body).toEqual(
      JSON.stringify({ input: 'test' }),
    )
  })

  it('GET request with custom headers', async () => {
    fetchMock.mockOnce(JSON.stringify({ result: 'success' }))

    const data = await serverFetcher<{ result: string }>('/api/test', {
      method: 'GET',
      headers: {
        'X-Custom-Header': 'test header value',
      },
    })

    expect(data).toEqual({ result: 'success' })
    const headers = fetchMock.mock.calls[0][1]?.headers as Record<
      string,
      string
    >
    expect(headers['X-Custom-Header']).toEqual('test header value')
  })

  it('POST request with NOT application/json content type', async () => {
    fetchMock.mockOnce(JSON.stringify({ result: 'success' }))

    const data = await serverFetcher<{ result: string }>('/api/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'key1=value1&key2=value2',
    })

    expect(data).toEqual({ result: 'success' })
    const headers = fetchMock.mock.calls[0][1]?.headers as Record<
      string,
      string
    >
    expect(headers['Content-Type']).toEqual('application/x-www-form-urlencoded')
    expect(fetchMock.mock.calls[0][1]?.body).toEqual('key1=value1&key2=value2')
  })

  it('throws an error when the fetch request fails', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({}), { status: 500 })

    await expect(serverFetcher('/api/test')).rejects.toThrow(
      'API Request failed\nURL: /api/test\nStatus: 500 Internal Server Error',
    )
  })
})
