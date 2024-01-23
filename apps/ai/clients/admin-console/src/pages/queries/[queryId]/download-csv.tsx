import QueryMetadata from '@/components/query/query-metadata'
import QueryQuestion from '@/components/query/question'
import { Button } from '@/components/ui/button'
import { useQuery } from '@/hooks/api/query/useQuery'
import useDownloadFile, { DownloadStatus } from '@/hooks/api/useDownloadFile'
import { Query } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { CheckCircle, Loader, XCircle } from 'lucide-react'
import { useRouter } from 'next/router'
import { FC } from 'react'

const DownloadCsvPage: FC = () => {
  const {
    query: { promptId },
  } = useRouter()
  const { downloadFile, status: downloadStatus, error } = useDownloadFile()
  const { query, isLoading } = useQuery(promptId as string)

  let pageContent: JSX.Element = <></>

  if (isLoading && !query) {
    pageContent = <div>Loading...</div>
  }

  if (query) {
    const {
      created_at,
      confidence_score,
      prompt_text,
      created_by,
      status,
      display_id,
      db_connection_alias,
    } = query as Query

    const questionDate: Date = new Date(created_at)

    const handleDownload = () => {
      downloadFile(
        `generations/${promptId}/csv-file`,
        `query-${display_id}.csv`,
      )
    }

    if (query) {
      pageContent = (
        <>
          <div
            id="header"
            className="flex items-end justify-between gap-3 px-6"
          >
            <QueryQuestion
              className="max-w-2xl"
              {...{
                created_by,
                prompt_text,
                questionDate,
                db_connection_alias,
              }}
            />
            <QueryMetadata
              {...{
                promptId: display_id,
                status,
                confidenceLevel: confidence_score,
              }}
            />
          </div>
          <div className="flex flex-col items-center gap-5">
            <Button variant="outline" onClick={handleDownload}>
              Download CSV File
            </Button>
            <div className="flex gap-2 items-center">
              {downloadStatus === DownloadStatus.Pending && (
                <>
                  <Loader className="w-6 h-6 animate-spin" />
                  <p>Downloading...</p>
                </>
              )}
              {downloadStatus === DownloadStatus.Error && (
                <>
                  <XCircle className="w-6 h-6 text-destructive" />
                  <p className="text-destructive">
                    Download failed. Reason: {error}
                  </p>
                </>
              )}
              {downloadStatus === DownloadStatus.Success && (
                <>
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  <p className="text-green-600">Download complete</p>
                </>
              )}
            </div>
          </div>
        </>
      )
    }
  }
  return (
    <div className="flex flex-col gap-10 items-center justify-center w-100 h-screen">
      {pageContent}
    </div>
  )
}

export default withPageAuthRequired(DownloadCsvPage)
