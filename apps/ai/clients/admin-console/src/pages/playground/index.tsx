import ErrorDetails from '@/components/error/error-details'
import PageLayout from '@/components/layout/page-layout'
import {
  SectionHeader,
  SectionHeaderTitle,
} from '@/components/query/section-header'
import SqlEditor from '@/components/query/sql-editor'
import SqlResultsTable from '@/components/query/sql-results-table'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import useFinetunings from '@/hooks/api/fine-tuning/useFinetunings'
import useQuerySubmit from '@/hooks/api/query/useQuerySubmit'
import useDatabaseConnections from '@/hooks/api/useDatabaseConnections'
import {
  formatQueryConfidence,
  getDomainStatusColors,
  mapQuery,
} from '@/lib/domain/query'
import { ErrorResponse, Query } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import clsx from 'clsx'
import {
  AlertOctagon,
  CaseSensitive,
  Code2,
  DatabaseZap,
  Eraser,
  Loader,
  PlayCircle,
  ServerCrash,
  StopCircle,
  Terminal,
  TerminalSquare,
} from 'lucide-react'
import Head from 'next/head'
import Link from 'next/link'
import { FC, useEffect, useState } from 'react'

const PlaygroundPage: FC = () => {
  const [submittingQuery, setSubmittingQuery] = useState(false)

  const [query, setQuery] = useState<Query | undefined>()
  const [prompt, setPrompt] = useState<string>('')
  const [previousQueryPrompt, setPreviousQueryPrompt] = useState<string>('')
  const [currentQueryPrompt, setCurrentQueryPrompt] = useState<string>('')
  const [queryError, setQueryError] = useState<string>()

  const {
    dbConnections,
    isLoading: loadingDatabases,
    error: dbError,
  } = useDatabaseConnections()

  // Database connections
  const [selectedDbConnectionId, setSelectedDbConnectionId] =
    useState<string>('')
  const [dbConnectionOptions, setDbConnectionOptions] = useState<
    {
      label: string
      value: string
    }[]
  >()

  useEffect(() => {
    if (!dbConnections) return
    if (dbConnections.length > 0) {
      setDbConnectionOptions(
        dbConnections.map(({ id, alias }) => ({
          label: (alias || id) as string,
          value: id as string,
        })),
      )
    }
  }, [dbConnections])

  useEffect(() => {
    if (!dbConnectionOptions) return
    if (dbConnectionOptions.length > 0) {
      setSelectedDbConnectionId(dbConnectionOptions[0].value) // default is first one
    }
  }, [dbConnectionOptions])

  const handleDatabaseSelect = (databaseId: string) => {
    setSelectedDbConnectionId(databaseId)
  }

  // Finetuining models
  const [selectedModelId, setSelectedModelId] = useState<string | undefined>()
  const [finetuningModels, setFinetuningModels] = useState<
    {
      label: string
      value: string
    }[]
  >([{ label: 'None', value: '' }])
  const { models } = useFinetunings()

  useEffect(() => {
    if (!models) return
    if (models.length > 0) {
      setFinetuningModels((prev) => [
        ...prev,
        ...models
          .filter((model) => model.status === 'SUCCEEDED')
          .map((model) => ({
            label: model.alias || model.id,
            value: model.id,
          })),
      ])
    }
  }, [models])

  useEffect(() => {
    if (!finetuningModels) return
    if (finetuningModels.length > 0) {
      setSelectedModelId(finetuningModels[0].value) // default is None
    }
  }, [finetuningModels])

  const handleModelSelect = (modelId: string) => {
    setSelectedModelId(modelId)
  }

  const { submitQuery, cancelSubmitQuery } = useQuerySubmit()

  const handleSubmitQuery = async () => {
    setQueryError(undefined)
    setSubmittingQuery(true)
    setPreviousQueryPrompt(currentQueryPrompt)
    setCurrentQueryPrompt(prompt)
    try {
      const query = await submitQuery(
        prompt,
        selectedDbConnectionId,
        selectedModelId || undefined,
      )
      setQuery(mapQuery(query))
      toast({
        title: 'Generation completed',
      })
    } catch (e) {
      console.error(e)
      if ((e as Error)?.name === 'AbortError') {
        toast({
          title: 'Generation cancelled',
        })
      } else {
        const { message: title, trace_id: description } = e as ErrorResponse
        toast({
          variant: 'destructive',
          title,
          description,
          action: (
            <ToastAction altText="Try again" onClick={handleSubmitQuery}>
              Try again
            </ToastAction>
          ),
        })
        setQueryError(title)
      }
    } finally {
      setSubmittingQuery(false)
    }
  }

  const handleStopGenerating = () => {
    cancelSubmitQuery()
    setCurrentQueryPrompt(previousQueryPrompt)
  }

  const handleClear = () => {
    setQuery(undefined)
    setPrompt('')
    setPreviousQueryPrompt('')
    setCurrentQueryPrompt('')
  }

  let content = <div className="grow"></div>

  if (dbError) {
    content = (
      <div className="grow text-slate-500 flex flex-col items-center justify-center gap-3">
        <AlertOctagon size={50} strokeWidth={1} />
        <span>There was a problem fetching your database connections.</span>
        <ErrorDetails
          error={dbError}
          displayTitle={false}
          className="items-center justify-center text-xs"
        />
      </div>
    )
  } else if (!dbConnectionOptions?.length) {
    content = (
      <div className="grow text-slate-500 flex flex-col items-center justify-center gap-3">
        <DatabaseZap size={50} strokeWidth={1} />
        <span>
          Set up your first database connection before using the Playground
        </span>
        <Link href="/databases" className="link">
          <Button variant="link">Go to Databases</Button>
        </Link>
      </div>
    )
  } else if (queryError) {
    content = (
      <div className="grow text-slate-500 flex flex-col items-center justify-center gap-3">
        <ServerCrash size={50} strokeWidth={1} />
        <span>
          There was a problem with the SQL Generation. Please try again.
        </span>
      </div>
    )
  } else if (submittingQuery) {
    content = (
      <div className="grow flex flex-col items-center justify-center gap-3">
        <div className="flex items-center gap-1 font-source-code">
          <Terminal size={16} strokeWidth={2} className="animate-bounce" />
          Generating SQL from natural language prompt...
        </div>
        <div className="w-2/3 xl:w-2/5 h-2 relative rounded overflow-hidden">
          <div className="h-full bg-progress-gradient animate-slide"></div>
        </div>
      </div>
    )
  } else if (query) {
    const { status, confidence_score, sql, sql_result, sql_generation_error } =
      query
    content = sql_generation_error ? (
      <div className="grow text-slate-500 flex flex-col items-center justify-center gap-3 max-w-2xl text-justify m-auto">
        <ServerCrash size={50} strokeWidth={1} />
        <span>{sql_generation_error}</span>
      </div>
    ) : (
      <div className="grow flex flex-col overflow-auto">
        <SectionHeader className="border-t-0">
          <SectionHeaderTitle>
            <CaseSensitive size={24} strokeWidth={2} />
            Natural Language Prompt
          </SectionHeaderTitle>
        </SectionHeader>
        <p className="px-6 py-5 break-words whitespace-break-spaces text-sm">
          {currentQueryPrompt}
        </p>
        <SectionHeader>
          <SectionHeaderTitle>
            <Code2 size={20} strokeWidth={2.5} />
            Generated SQL
          </SectionHeaderTitle>
          {confidence_score && (
            <div className="flex flex-row text-sm items-center gap-2 font-semibold">
              <span
                className={getDomainStatusColors(status, confidence_score).text}
              >
                {formatQueryConfidence(confidence_score)}
              </span>
            </div>
          )}
        </SectionHeader>
        <div className="grow flex flex-col gap-5 mx-6 my-4">
          <div className="h-[30vh] overflow-auto">
            <SqlEditor disabled query={sql} />
          </div>
          <div id="query_results" className="flex flex-col border bg-white">
            {sql_result === null ||
            !sql_result ||
            !sql_result.columns ||
            !sql_result.rows ? (
              <div className="w-full h-20 flex items-center justify-center bg-slate-100">
                <div className="text-slate-600">No Results</div>
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
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Playground - Dataherald AI API</title>
      </Head>
      <PageLayout>
        {loadingDatabases ? (
          <div className="grow flex items-center justify-center gap-2">
            <TerminalSquare
              size={25}
              strokeWidth={1.5}
              className="animate-bounce"
            />
            <span className="font-source-code font-semibold">
              Preparing everything...
            </span>
          </div>
        ) : (
          <div className="grow flex flex-col overflow-auto">
            {content}
            <div className="bg-slate-50 px-5 py-3 flex flex-col gap-2 grow-0 rounded-none border-b-0 border-s-0 border-e-0 border-t border-slate-200">
              <div className="px-2 flex items-center justify-between gap-2">
                <div className="w-3/4 grid grid-cols-2 gap-3">
                  <div className="flex items-center gap-2">
                    <strong className="w-fit">Database</strong>
                    <Select
                      value={selectedDbConnectionId}
                      onValueChange={handleDatabaseSelect}
                      disabled={
                        loadingDatabases ||
                        !dbConnectionOptions?.length ||
                        submittingQuery
                      }
                    >
                      <SelectTrigger
                        aria-label="Database"
                        className="bg-white border-slate-300"
                      >
                        <SelectValue
                          placeholder={
                            loadingDatabases
                              ? 'Loading...'
                              : 'Select a Database'
                          }
                        />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          {dbConnectionOptions?.map(({ label, value }) => (
                            <SelectItem key={label} value={value}>
                              {label}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center gap-2">
                    <strong>Model</strong>
                    <Select
                      value={selectedModelId}
                      onValueChange={handleModelSelect}
                      disabled={
                        loadingDatabases ||
                        !dbConnectionOptions?.length ||
                        submittingQuery
                      }
                    >
                      <SelectTrigger
                        aria-label="Model"
                        className="bg-white border-slate-300"
                      >
                        <SelectValue placeholder="Select model" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          {finetuningModels?.map(({ label, value }) => (
                            <SelectItem key={label} value={value}>
                              {label}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button
                  className="px-3 py-1 w-fit h-fit font-normal"
                  variant="ghost"
                  disabled={
                    loadingDatabases ||
                    !dbConnectionOptions?.length ||
                    submittingQuery ||
                    !query
                  }
                  size="sm"
                  onClick={handleClear}
                >
                  <Eraser size={14} className="mr-2" /> Clear
                </Button>
              </div>
              <div className="bg-white border border-slate-300 rounded-xl p-2 flex flex-col items-end gap-1">
                <Textarea
                  className="text-base border-none resize-none outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:ring-offset-transparent"
                  placeholder="Enter your natural language prompt..."
                  disabled={
                    loadingDatabases ||
                    !dbConnectionOptions?.length ||
                    submittingQuery
                  }
                  rows={3}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
                <div className="flex items-center gap-3">
                  {submittingQuery && (
                    <Button
                      className="px-3 py-1 h-fit text-slate-500"
                      variant="ghost"
                      onClick={handleStopGenerating}
                    >
                      <StopCircle size={16} className="mr-2" />
                      Stop generating
                    </Button>
                  )}
                  <Button
                    className="px-3 py-1 h-fit"
                    variant="primary"
                    onClick={handleSubmitQuery}
                    disabled={
                      !dbConnectionOptions?.length || submittingQuery || !prompt
                    }
                  >
                    {submittingQuery ? (
                      <Loader size={16} className="mr-2 animate-spin" />
                    ) : (
                      <PlayCircle
                        size={16}
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
              <p className="text-xs text-slate-500 text-center">
                Playground prompts can be viewed from the Queries page and be
                verified as Golden SQL
              </p>
            </div>
          </div>
        )}
      </PageLayout>
      <Toaster />
    </>
  )
}

export default withPageAuthRequired(PlaygroundPage)
