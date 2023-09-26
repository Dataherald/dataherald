import useSWR from 'swr'

export const useMockGetter = <T>(
  mockUrl: string,
  mockData: T,
  delayDuration = 1000,
) => {
  const fetchMockData = () => {
    return new Promise<T>((resolve) => {
      setTimeout(() => {
        resolve(mockData as T)
      }, delayDuration)
    })
  }
  const { data, isLoading, error, mutate } = useSWR<T>(mockUrl, fetchMockData)

  return {
    data,
    isLoading,
    error,
    mutate,
  }
}
