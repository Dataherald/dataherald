import useApiFetcher from '@/hooks/api/generics/useApiFetcher'
import { useCallback, useState } from 'react'

export enum DownloadStatus {
  Error = 'error',
  Success = 'success',
  Pending = 'pending',
}

const useDownloadFile = () => {
  const [status, setStatus] = useState<DownloadStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const { apiDownloadFile } = useApiFetcher()

  const downloadFile = useCallback(
    async (endpointUrl: string, filename = 'file') => {
      try {
        setStatus(DownloadStatus.Pending)
        const blob = await apiDownloadFile(endpointUrl)

        if (!blob) {
          setStatus(DownloadStatus.Error)
          setError('No file received')
          return
        }

        const fileURL = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = fileURL
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        setStatus(DownloadStatus.Success)
      } catch (error) {
        setStatus(DownloadStatus.Error)
        setError((error as Error).message)
        console.error('Download error:', error)
      }
    },
    [apiDownloadFile],
  )

  return { downloadFile, status, error }
}

export default useDownloadFile
