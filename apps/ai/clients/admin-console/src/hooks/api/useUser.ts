import useSWR from 'swr'

export interface User {
  id: number
  name: string
  organization: string
}

export function useUser(userId: number) {
  const { data, error } = useSWR<User>(`/api/user/${userId}`)

  return {
    user: data,
    isLoading: !error && !data,
    isError: error,
  }
}
