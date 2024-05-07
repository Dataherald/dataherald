import { DataTable } from '@/components/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import PageErrorMessage from '@/components/error/page-error-message'
import { finetunningsColumns } from '@/components/fine-tunnings/columns'
import PageLayout from '@/components/layout/page-layout'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import useFinetunings from '@/hooks/api/fine-tuning/useFinetunings'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { RefreshCcw, SlidersIcon } from 'lucide-react'
import Head from 'next/head'
import { FC, useMemo } from 'react'

const FineTuningPage: FC = () => {
  const { isLoading, isValidating, error, models, mutate } = useFinetunings()
  const columns = useMemo(() => finetunningsColumns, [])

  let pageContent = <></>

  if (isLoading) {
    pageContent = (
      <LoadingTable columnLength={5} rowLength={5} className="rounded-none" />
    )
  } else if (error) {
    pageContent = (
      <PageErrorMessage
        message="Something went wrong while fetching the fine-tunning models."
        error={error}
      />
    )
  } else if (models?.length === 0) {
    pageContent = <div className="text-slate-500">No models created yet.</div>
  } else {
    pageContent = models ? (
      <DataTable id="fine-tuning" columns={columns} data={models} />
    ) : (
      <></>
    )
  }

  return (
    <PageLayout>
      <Head>
        <title>Fine-tuning - Dataherald API</title>
      </Head>
      <div className="gap-4 m-6">
        <ContentBox className="w-100 max-w-3xl min-h-[50vh]">
          <div className="w-full flex justify-between gap-2">
            <div className="flex items-center gap-2">
              <SlidersIcon size={20} strokeWidth={2.5} />
              <h1 className="font-semibold">Fine-tuning models</h1>
            </div>
            <Button
              variant="ghost"
              size="icon"
              disabled={isLoading || isValidating}
              onClick={() => mutate()}
            >
              <RefreshCcw
                size={16}
                className={isLoading || isValidating ? 'animate-spin' : ''}
              />
            </Button>
          </div>
          <div className="grow">{pageContent}</div>
        </ContentBox>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(FineTuningPage)
