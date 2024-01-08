import { DataTable } from '@/components/data-table/data-table'
import { LoadingTable } from '@/components/data-table/loading-table'
import { finetunningsColumns } from '@/components/fine-tunnings/columns'
import FineTunningsError from '@/components/fine-tunnings/error'
import PageLayout from '@/components/layout/page-layout'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import useFinetunings from '@/hooks/api/fine-tuning/useFinetunings'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { RefreshCcw, SlidersIcon } from 'lucide-react'
import { FC, useMemo } from 'react'

const FineTuningPage: FC = () => {
  const { isLoading, isValidating, error, models, mutate } = useFinetunings()
  const columns = useMemo(() => finetunningsColumns, [])

  let pageContent = <></>

  if (isLoading) {
    pageContent = (
      <LoadingTable columnLength={3} rowLength={5} className="rounded-none" />
    )
  } else if (error) {
    pageContent = <FineTunningsError />
  } else if (models?.length === 0) {
    pageContent = <div className="text-slate-500">No models created yet.</div>
  } else {
    pageContent = models ? <DataTable columns={columns} data={models} /> : <></>
  }

  return (
    <PageLayout>
      <div className="gap-4 m-6">
        <ContentBox className="w-100 max-w-2xl min-h-[50vh] max-h-[50vh]">
          <div className="w-full flex justify-between gap-2">
            <div className="flex items-center gap-2">
              <SlidersIcon size={20} strokeWidth={2.5} />
              <h1 className="font-semibold">Fine-tuning models</h1>
            </div>
            <Button
              variant="ghost"
              disabled={isLoading || isValidating}
              onClick={() => mutate()}
            >
              <RefreshCcw
                size={18}
                className={isLoading || isValidating ? 'animate-spin' : ''}
              />
            </Button>
          </div>
          <div className="grow overflow-auto">{pageContent}</div>
        </ContentBox>
      </div>
    </PageLayout>
  )
}

export default withPageAuthRequired(FineTuningPage)
