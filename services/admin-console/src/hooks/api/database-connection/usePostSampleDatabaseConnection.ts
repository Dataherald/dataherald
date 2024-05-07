import { API_URL } from '@/config'
import usePost from '@/hooks/api/generics/usePost'
import { DatabaseConnection } from '@/models/api'

type PostSampleDBRequest = { sample_db_id: string }

const usePostSampleDatabaseConnection = () => {
  const postUser = usePost<PostSampleDBRequest, DatabaseConnection>()
  return (resource: PostSampleDBRequest) =>
    postUser(`${API_URL}/database-connections/sample`, resource)
}

export default usePostSampleDatabaseConnection
