import ErrorDetails from '@/components/error/error-details'
import PageLayout from '@/components/layout/page-layout'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import MarkdownRenderer from '@/components/ui/markdown-renderer'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectOption,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { API_URL } from '@/config'
import LLM_MODELS from '@/constants/llm-models'
import { useAuth } from '@/contexts/auth-context'
import { useSelfServePlayground } from '@/contexts/self-serve-context'
import { useSubscription } from '@/contexts/subscription-context'
import useDatabaseConnections from '@/hooks/api/database-connection/useDatabaseConnections'
import useFinetunings from '@/hooks/api/fine-tuning/useFinetunings'
import useDatabaseOptions, {
  DBConnectionOptionData,
} from '@/hooks/database/useDatabaseOptions'
import { isSubscriptionErrorCode } from '@/lib/domain/error'
import { ErrorResponse } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { useCompletion } from 'ai/react'
import clsx from 'clsx'
import {
  AlertOctagon,
  Bot,
  CircleSlash,
  DatabaseZap,
  Loader,
  PlayCircle,
  ServerCrash,
  Sliders,
  Sparkles,
  StopCircle,
  TerminalSquare,
} from 'lucide-react'
import Head from 'next/head'
import Image from 'next/image'
import Link from 'next/link'
import { FC, useEffect, useRef, useState } from 'react'

const STREAM_CHUNK_SIZE = 5

const NONE_FINE_TUNING_MODEL: SelectOption = {
  label: 'None',
  value: '',
  icon: <Sliders size={16} />,
}

const LOADING_MORE_FINE_TUNING_MODELS: SelectOption = {
  label: 'Loading...',
  value: 'loading',
  icon: <Loader size={16} className="animate-spin" />,
}

const PlaygroundPage: FC = () => {
  const submitBtnRef = useRef<HTMLButtonElement>(null)
  const {
    dbConnections,
    isLoading: loadingDatabases,
    error: dbError,
  } = useDatabaseConnections()

  // Database connections
  const [selectedDbConnectionId, setSelectedDbConnectionId] =
    useState<string>('')

  const dbConnectionOptions: SelectOption[] = useDatabaseOptions(
    dbConnections as DBConnectionOptionData[],
  )
  useEffect(() => {
    if (!dbConnectionOptions) return
    if (dbConnectionOptions.length > 0) {
      setSelectedDbConnectionId(dbConnectionOptions[0].value) // default is first one
    }
  }, [dbConnectionOptions])

  const handleDatabaseSelect = (databaseId: string) => {
    setSelectedDbConnectionId(databaseId)
  }

  // Finetuning models
  const [selectedModelId, setSelectedModelId] = useState<string | undefined>()
  const [finetuningModelOptions, setFinetuningModelOptions] = useState<
    SelectOption[]
  >([NONE_FINE_TUNING_MODEL])
  const {
    models,
    error: modelsError,
    isValidating: loadingModels,
  } = useFinetunings(selectedDbConnectionId)

  useEffect(() => {
    if (loadingModels) {
      setFinetuningModelOptions([
        NONE_FINE_TUNING_MODEL,
        LOADING_MORE_FINE_TUNING_MODELS,
      ])
    } else {
      if (modelsError || !models) {
        setFinetuningModelOptions([NONE_FINE_TUNING_MODEL])
      } else {
        setFinetuningModelOptions([
          NONE_FINE_TUNING_MODEL,
          ...models
            .filter((model) => model.status === 'SUCCEEDED')
            .map((model) => ({
              ...model,
              base_llm: { ...model.base_llm, model_provider: 'openai' },
            })) // TODO hardcoded to openai as is the only one supported
            .map((model) => ({
              label: model.alias || model.id,
              value: model.id,
              icon: LLM_MODELS.filter(
                (llm_model) =>
                  llm_model.provider === model.base_llm.model_provider,
              )
                .map((llm_model) =>
                  llm_model ? (
                    <Image
                      key={llm_model.logoUrl}
                      priority
                      src={llm_model.logoUrl}
                      alt={model.base_llm?.model_name || ''}
                      width={18}
                      height={18}
                    />
                  ) : null,
                )
                .pop() || <></>,
            })),
        ])
      }
    }
  }, [loadingModels, models, modelsError])

  useEffect(() => {
    if (finetuningModelOptions === undefined) return
    if (finetuningModelOptions.length > 0) {
      setSelectedModelId(finetuningModelOptions[0].value) // default is None
    }
  }, [finetuningModelOptions])

  const handleModelSelect = (modelId: string) => {
    setSelectedModelId(modelId)
  }

  // AI completion
  const [streamText, setStreamText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [agentStopped, setAgentStopped] = useState(false)
  const [agentError, setAgentError] = useState<ErrorResponse>()
  const streamEndRef = useRef<HTMLDivElement>(null)

  const { token } = useAuth()
  const {
    completion,
    input,
    stop,
    isLoading,
    handleInputChange,
    handleSubmit,
    error,
    setInput,
    setCompletion,
  } = useCompletion({
    api: `${API_URL}/generations/prompts/sql-generations/stream`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: {
      db_connection_id: selectedDbConnectionId,
      ...(selectedModelId ? { finetuning_id: selectedModelId } : {}),
    },
  })

  // handle streaming
  useEffect(() => {
    if (agentStopped) {
      setCompletion(streamText)
    } else {
      const streamTimeout = setTimeout(() => {
        if (completion && completion.length > streamText.length) {
          const remainingStreamingChars = completion.length - streamText.length
          const completionSliceStart = streamText.length
          const completionSliceEnd =
            remainingStreamingChars > STREAM_CHUNK_SIZE
              ? completionSliceStart + STREAM_CHUNK_SIZE
              : undefined // if remaining chars are less than STREAM_CHUNK_SIZE, slice until the end

          const nextStreamChunk = completion.slice(
            completionSliceStart,
            completionSliceEnd,
          )
          setStreamText((stream) => stream + nextStreamChunk)
        }
      }, 15)
      return () => clearTimeout(streamTimeout)
    }
  }, [agentStopped, completion, setCompletion, streamText])

  useEffect(() => {
    if (isLoading) {
      setIsStreaming(true)
    } else {
      setIsStreaming(completion?.length > streamText.length)
    }
  }, [completion, isLoading, streamText])

  // streaming error handling
  const { setSubscriptionStatus } = useSubscription()

  useEffect(() => {
    if (error) {
      if (error.message.includes('error_code')) {
        setAgentError(JSON.parse(error.message))
      }
    } else if (
      !isStreaming &&
      !agentStopped &&
      streamText?.includes('error_code')
    ) {
      setAgentError(JSON.parse(streamText))
    }
  }, [streamText, error, isStreaming, agentStopped])

  // handle subscription status error
  useEffect(() => {
    if (agentError && isSubscriptionErrorCode(agentError.error_code)) {
      setSubscriptionStatus(agentError.error_code)
    }
  }, [agentError, setSubscriptionStatus])

  useEffect(() => {
    // Scroll to the end of the stream only when the scroll is at the bottom
    if (streamEndRef.current && isStreaming) {
      if (
        streamEndRef.current.getBoundingClientRect().bottom <=
        window.innerHeight + 30
      ) {
        streamEndRef.current.scrollIntoView({
          behavior: 'instant',
          block: 'end',
          inline: 'nearest',
        })
      }
    }
  }, [isStreaming, streamText])

  // Self Serve flow
  const [isSubmitButtonReady, setIsSubmitButtonReady] = useState(false)
  const {
    dbConnectionId: selfServeDBConnectionId,
    examplePrompt: selfServeExamplePrompt,
    clearSelfServePlaygroundData,
  } = useSelfServePlayground()

  useEffect(() => {
    const interval = setInterval(() => {
      if (submitBtnRef.current && submitBtnRef.current.disabled === false) {
        setIsSubmitButtonReady(true)
        clearInterval(interval)
      }
    }, 100)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (selfServeDBConnectionId && selfServeExamplePrompt) {
      if (selfServeDBConnectionId !== selectedDbConnectionId) {
        setSelectedDbConnectionId(selfServeDBConnectionId)
      }
      if (selfServeExamplePrompt !== input) {
        setInput(selfServeExamplePrompt)
      }
      if (isSubmitButtonReady) {
        submitBtnRef.current?.click()
        clearSelfServePlaygroundData()
      }
    }
  }, [
    clearSelfServePlaygroundData,
    input,
    isSubmitButtonReady,
    selectedDbConnectionId,
    selfServeDBConnectionId,
    selfServeExamplePrompt,
    setInput,
  ])

  const handleClear = () => {
    setInput('')
    setCompletion('')
    setStreamText('')
    setAgentStopped(false)
    setAgentError(undefined)
  }

  const handleStop = () => {
    setAgentStopped(true)
    setAgentError(undefined)
    stop()
  }

  const handleGenerate = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setStreamText('')
    setAgentStopped(false)
    setAgentError(undefined)
    handleSubmit(e)
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
  } else {
    const agentConfig: {
      color: string
      bg: string
      text: string
      icon: JSX.Element
    } | null = isStreaming
      ? {
          color: 'text-slate-700',
          bg: 'bg-sky-200',
          text: 'Agent processing',
          icon: <Loader size={12} strokeWidth={2} className="animate-spin" />,
        }
      : agentStopped
      ? {
          color: 'text-slate-500',
          bg: 'bg-slate-200',
          text: 'Agent stopped',
          icon: <CircleSlash size={12} strokeWidth={2} />,
        }
      : null
    content = (
      <div className="grow my-1 flex flex-col gap-2 overflow-auto">
        {agentConfig && (
          <div className={clsx('flex items-center gap-2', agentConfig.color)}>
            <div className={clsx('p-1.5 rounded-full', agentConfig.bg)}>
              <Bot size={16} strokeWidth={2} />
            </div>
            <div className="w-fit flex items-center gap-2">
              <span className="text-sm">{agentConfig.text}</span>
              {agentConfig.icon}
            </div>
          </div>
        )}
        {agentError ? (
          <div className="grow max-w-2xl mx-auto text-slate-500 flex flex-col items-center justify-center gap-3">
            <ServerCrash size={50} strokeWidth={1} />
            <span>
              There was a problem with the SQL Generation. Please try again.
            </span>
            <ErrorDetails className="max-w-sm" error={agentError} />
          </div>
        ) : (
          streamText !== undefined && (
            <div
              className={clsx(
                'grow overflow-auto whitespace-pre-wrap text-slate-900',
              )}
            >
              <MarkdownRenderer>{streamText}</MarkdownRenderer>
              <div ref={streamEndRef} />
            </div>
          )
        )}
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Playground - Dataherald API</title>
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
          <>
            <div className="h-2/5 p-6 flex flex-col gap-3">
              <div className="flex gap-1 items-start text-slate-500">
                <Sparkles size={14} strokeWidth={1.75} />
                <Label className="font-semibold">Natural Language Prompt</Label>
              </div>
              <form className="grow flex flex-col" onSubmit={handleGenerate}>
                <Textarea
                  className="p-0 grow text-base border-none resize-none outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:ring-offset-transparent"
                  placeholder="Enter a natural language prompt to generate an SQL query..."
                  disabled={
                    loadingDatabases ||
                    !dbConnectionOptions?.length ||
                    isStreaming
                  }
                  rows={5}
                  value={input}
                  onChange={handleInputChange}
                />
                <div className="flex items-center self-end gap-3">
                  {!isStreaming && (
                    <Button
                      type="button"
                      variant="ghost"
                      disabled={!input && !streamText}
                      onClick={handleClear}
                    >
                      Clear
                    </Button>
                  )}
                  {isStreaming && (
                    <Button
                      type="button"
                      className="w-44 py-1 h-fit text-slate-500"
                      variant="ghost"
                      onClick={handleStop}
                    >
                      <StopCircle size={18} className="mr-2" />
                      Stop generation
                    </Button>
                  )}
                  <Button
                    ref={submitBtnRef}
                    className="w-44 py-1 h-fit"
                    disabled={
                      isStreaming || !dbConnectionOptions?.length || !input
                    }
                  >
                    {isStreaming ? (
                      <>
                        <Loader size={16} className="mr-2 animate-spin" />
                        Generating SQL
                      </>
                    ) : (
                      <>
                        <PlayCircle size={16} className="mr-2" />
                        Generate SQL
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </div>
            <div className="h-3/5 bg-slate-50 flex flex-col overflow-auto">
              <div className="overflow-auto p-6 h-full flex flex-col gap-2 grow-0 rounded-none border-b-0 border-s-0 border-e-0 border-t border-slate-200">
                {dbConnectionOptions && dbConnectionOptions.length > 0 && (
                  <div className="w-4/5 max-w-3xl grid grid-cols-2 gap-3">
                    <div className="flex items-center gap-2">
                      <Select
                        value={selectedDbConnectionId}
                        onValueChange={handleDatabaseSelect}
                        disabled={
                          !!dbError ||
                          loadingDatabases ||
                          !dbConnectionOptions?.length ||
                          isStreaming
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
                            <SelectLabel>Databases</SelectLabel>
                            {dbConnectionOptions?.map(
                              ({ label, value, icon }, idx) => (
                                <SelectItem key={label + idx} value={value}>
                                  <div className="flex items-center gap-2">
                                    {icon}
                                    {label}
                                  </div>
                                </SelectItem>
                              ),
                            )}
                          </SelectGroup>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center gap-2">
                      <Select
                        value={selectedModelId}
                        onValueChange={handleModelSelect}
                        disabled={
                          !!modelsError || loadingDatabases || isStreaming
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
                            <SelectLabel>Fine-tuning models</SelectLabel>
                            {finetuningModelOptions?.map(
                              ({ label, value, icon }, idx) => (
                                <SelectItem key={label + idx} value={value}>
                                  <div className="flex items-center gap-2">
                                    {icon}
                                    {label}
                                  </div>
                                </SelectItem>
                              ),
                            )}
                          </SelectGroup>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}
                <div className="grow overflow-auto flex flex-col gap-2">
                  {content}
                </div>
              </div>
            </div>
          </>
        )}
      </PageLayout>
    </>
  )
}

export default withPageAuthRequired(PlaygroundPage)
