import PageLayout from '@/components/layout/page-layout'
import {
  SectionHeader,
  SectionHeaderTitle,
} from '@/components/query/section-header'
import SqlEditor from '@/components/query/sql-editor'
import SqlResultsTable from '@/components/query/sql-results-table'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import useQuerySubmit from '@/hooks/api/query/useQuerySubmit'
import useDatabases from '@/hooks/api/useDatabases'
import {
  formatQueryConfidence,
  getDomainStatusColors,
  mapQuery,
} from '@/lib/domain/query'
import { Query } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import clsx from 'clsx'
import {
  CaseSensitive,
  Code2,
  Eraser,
  Loader2,
  PlayCircle,
  StopCircle,
  XOctagon,
} from 'lucide-react'
import { FC, useState } from 'react'

const PlaygroundPage: FC = () => {
  const [submittingQuery, setSubmittingQuery] = useState(false)
  const [prompt, setPrompt] = useState<string>('')
  const [previousQueryPrompt, setPreviousQueryPrompt] = useState<string>('')
  const [currentQueryPrompt, setCurrentQueryPrompt] = useState<string>('')
  const [query, setQuery] = useState<Query | undefined>()
  const { databases } = useDatabases()
  const activeDatabase = databases?.length ? databases[0].alias : 'Loading...'

  const { submitQuery, cancelSubmitQuery } = useQuerySubmit()

  const handleSubmitQuery = async () => {
    setSubmittingQuery(true)
    setPreviousQueryPrompt(currentQueryPrompt)
    setCurrentQueryPrompt(prompt)
    try {
      const query = await submitQuery(prompt)
      setQuery(mapQuery(query))
    } catch (error) {
      console.error(error)
      toast({
        variant: 'destructive',
        title: 'Oops! Something went wrong.',
        description: 'There was a problem with running the query',
        action: (
          <ToastAction altText="Try again" onClick={handleSubmitQuery}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setSubmittingQuery(false)
    }
  }

  const handleStopGenerating = () => {
    cancelSubmitQuery()
    setCurrentQueryPrompt(previousQueryPrompt)
    setSubmittingQuery(false)
  }

  const handleClear = () => {
    setQuery(undefined)
    setPrompt('')
    setPreviousQueryPrompt('')
    setCurrentQueryPrompt('')
  }

  let pageContent = <></>

  if (submittingQuery) {
    pageContent = (
      <div className="grow flex flex-col items-center justify-center gap-3">
        Generating SQL from Natural Language prompt...
        <div className="w-2/3 xl:w-2/5 h-2 relative rounded overflow-hidden">
          <div className="h-full bg-progress-gradient animate-slide"></div>
        </div>
      </div>
    )
  } else if (query) {
    const { status, confidence_score, sql, sql_result, sql_generation_error } =
      query
    pageContent = (
      <div className="grow flex flex-col overflow-auto">
        <SectionHeader>
          <SectionHeaderTitle>
            <CaseSensitive size={28} strokeWidth={2} />
            Natural Language Prompt
          </SectionHeaderTitle>
        </SectionHeader>
        <p className="px-6 py-4 max-h-[150px] overflow-auto break-words whitespace-break-spaces">
          {currentQueryPrompt}
        </p>
        <div className="grow flex flex-col">
          <SectionHeader>
            <SectionHeaderTitle>
              <Code2 size={24} strokeWidth={2}></Code2>
              Generated SQL
            </SectionHeaderTitle>
            <div className="flex flex-row text-sm items-center gap-2 font-semibold">
              <span
                className={getDomainStatusColors(status, confidence_score).text}
              >
                {formatQueryConfidence(confidence_score)}
              </span>
            </div>
          </SectionHeader>
          <div className="grow flex flex-col gap-2 mx-6 my-4">
            <div className="grow shrink-0 min-h-fit">
              <SqlEditor disabled query={sql} />
            </div>
            {sql_generation_error ? (
              <div className="shrink-0 h-32 flex flex-col items-center border bg-white border-red-600 text-red-600">
                <div className="flex items-center gap-3 py-5 font-bold">
                  <XOctagon size={28} />
                  <span>SQL Error</span>
                </div>
                <div className="w-full overflow-auto px-8 pb-3">
                  {sql_generation_error}
                </div>
              </div>
            ) : (
              <div
                id="query_results"
                className="grow min-h-[10rem] max-h-80 flex flex-col border bg-white"
              >
                {sql_result === null ? (
                  <div className="w-full h-44 flex items-center justify-center bg-gray-100">
                    <div className="text-gray-600">No Results</div>
                  </div>
                ) : (
                  <SqlResultsTable
                    columns={sql_result.columns.map((columnKey: string) => ({
                      id: columnKey,
                      header: columnKey,
                      accessorKey: columnKey,
                    }))}
                    data={sql_result.rows}
                  />
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <PageLayout>
        <div className="grow flex flex-col gap-5 overflow-auto">
          <div className="grow flex flex-col overflow-auto">{pageContent}</div>
          <div className="bg-slate-50 p-5 flex flex-col gap-3 grow-0 rounded-none border-b-0 border-s-0 border-e-0 border-t">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <strong>Active database:</strong>
                {activeDatabase}
              </div>
              <Button
                className="px-3 py-1 w-fit h-fit font-normal"
                variant="ghost"
                disabled={!query || submittingQuery}
                size="sm"
                onClick={handleClear}
              >
                <Eraser size={14} className="mr-2" /> Clear
              </Button>
            </div>
            <div className="bg-white border-2 border-slate-200 rounded-xl p-3 flex flex-col items-end gap-2">
              <Textarea
                className="border-none text-md resize-none shadow-none outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:ring-offset-transparent"
                placeholder="Enter your Natural Language inquiry..."
                disabled={submittingQuery}
                rows={2}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
              <div className="flex items-center gap-3">
                {submittingQuery && (
                  <Button
                    className="px-3 py-1 h-fit"
                    variant="ghost"
                    onClick={handleStopGenerating}
                  >
                    <StopCircle size={18} className="mr-2" />
                    Stop generating
                  </Button>
                )}
                <Button
                  className="px-3 py-1 h-fit"
                  variant="primary"
                  onClick={handleSubmitQuery}
                  disabled={submittingQuery || !prompt}
                >
                  {submittingQuery ? (
                    <Loader2 size={18} className="mr-2 animate-spin" />
                  ) : (
                    <PlayCircle
                      size={18}
                      className={clsx(
                        'mr-2',
                        submittingQuery
                          ? 'opacity-50'
                          : 'hover:opacity-80 hover:cursor-pointer',
                      )}
                    />
                  )}
                  Generate SQL
                </Button>
              </div>
            </div>
          </div>
        </div>
      </PageLayout>
      <Toaster />
    </>
  )
}

export default withPageAuthRequired(PlaygroundPage)
