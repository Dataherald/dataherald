import QueryMetadata from '@/components/query/query-metadata'
import QueryQuestion from '@/components/query/question'
import { Button } from '@/components/ui/button'
import { useQuery } from '@/hooks/api/query/useQuery'
import useDownloadFile, { DownloadStatus } from '@/hooks/api/useDownloadFile'
import { Query } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { CheckCircle, Download, Loader, XCircle } from 'lucide-react'
import Head from 'next/head'
import Image from 'next/image'
import { useRouter } from 'next/router'
import { FC } from 'react'

const DownloadCsvPage: FC = () => {
  const {
    query: { queryId: promptId },
  } = useRouter()
  const { downloadFile, status: downloadStatus, error } = useDownloadFile()
  const { query, isLoading } = useQuery(promptId as string)

  let pageContent: JSX.Element = <></>

  if (isLoading && !query) {
    pageContent = (
      <div className="grow flex items-center justify-center">
        <Loader className="animate-spin mr-2" />
        Loading...
      </div>
    )
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
        <div className="grow flex flex-col items-center justify-between gap-10">
          <div id="header" className="flex items-end justify-between gap-3">
            <QueryQuestion
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
            <Button
              onClick={handleDownload}
              disabled={downloadStatus === DownloadStatus.Pending}
            >
              {downloadStatus === DownloadStatus.Pending ? (
                <>
                  <Loader
                    size={20}
                    strokeWidth={2}
                    className="animate-spin mr-2"
                  />
                  <p>Downloading file...</p>
                </>
              ) : (
                <>
                  <Download size={20} strokeWidth={2} className="mr-2" />
                  <p>Download CSV File</p>
                </>
              )}
            </Button>
            <div className="flex gap-2 items-center h-6">
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
        </div>
      )
    }
  }
  return (
    <div className="flex items-center justify-center min-h-screen relative">
      <Head>
        <title>Download CSV - Dataherald API</title>
      </Head>
      <Image
        src="/images/dh_background.png"
        alt="Background"
        fill
        style={{ objectFit: 'cover', objectPosition: 'center' }}
        quality={100}
      />
      <div className="absolute flex flex-col bg-white shadow-lg w-full min-h-[40vh] max-w-3xl p-14 rounded-2xl">
        {pageContent}
      </div>
    </div>
  )
}

export default withPageAuthRequired(DownloadCsvPage)
