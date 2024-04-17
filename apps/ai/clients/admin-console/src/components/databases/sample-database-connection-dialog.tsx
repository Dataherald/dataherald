import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import DATABASE_PROVIDERS from '@/constants/database-providers'
import { useSelfServePlayground } from '@/contexts/self-serve-context'
import usePostSampleDatabaseConnection from '@/hooks/api/database-connection/usePostSampleDatabaseConnection'
import useSampleDatabaseConnections from '@/hooks/api/database-connection/useSampleDatabaseConnections'
import useDatabaseOptions from '@/hooks/database/useDatabaseOptions'
import {
  DatabaseConnection,
  Databases,
  ErrorResponse,
  SampleDatabaseConnection,
} from '@/models/api'
import {
  ArrowRightCircle,
  CheckCircle,
  Loader,
  Sparkles,
  TestTube2,
} from 'lucide-react'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { FC, useEffect, useState } from 'react'

interface SampleDatabaseConnectionDialogProps {
  onConnected: (newDatabases?: Databases, refresh?: boolean) => void
  onFinish?: () => void
}

const SampleDatabaseConnectionDialog: FC<
  SampleDatabaseConnectionDialogProps
> = ({ onConnected, onFinish }) => {
  const router = useRouter()
  const [isAdding, setIsAdding] = useState(false)
  const [sampleDBAdded, setSampleDBAdded] = useState(false)
  const [selectedSampleDB, setSelectedSampleDB] =
    useState<SampleDatabaseConnection>()
  const addSampleDatabase = usePostSampleDatabaseConnection()
  const [postDBError, setPostDBError] = useState<ErrorResponse | null>(null)
  const { sampleDBConnections } = useSampleDatabaseConnections()
  const sampleDBOptions = useDatabaseOptions(sampleDBConnections)
  const selectedDBProvider = DATABASE_PROVIDERS.find(
    ({ dialect }) => dialect === selectedSampleDB?.dialect,
  )
  const [sampleDatabaseConnetion, setSampleDatabaseConnection] =
    useState<DatabaseConnection>()
  const [examplePrompt, setExamplePrompt] = useState<string>()
  const { setSelfServePlaygroundData } = useSelfServePlayground()

  useEffect(() => {
    if (sampleDBConnections && sampleDBConnections.length > 0) {
      setSelectedSampleDB(sampleDBConnections[0]) // Select the first sample DB by default
    }
  }, [sampleDBConnections])

  useEffect(() => {
    if (sampleDatabaseConnetion && examplePrompt) {
      setSelfServePlaygroundData(
        sampleDatabaseConnetion.id as string,
        examplePrompt,
      )
      router.push('/playground')
    }
  }, [
    sampleDatabaseConnetion,
    examplePrompt,
    setSelfServePlaygroundData,
    router,
  ])

  const handleSampleDBSelect = (value: string) => {
    setSelectedSampleDB(sampleDBConnections?.find((db) => db.id === value))
  }

  const onSubmit = async () => {
    if (!selectedSampleDB) return
    try {
      setIsAdding(true)
      setPostDBError(null)
      const newDBConnection: DatabaseConnection = await addSampleDatabase({
        sample_db_id: selectedSampleDB?.id,
      })
      setSampleDatabaseConnection(newDBConnection)
      setSampleDBAdded(true)
      onConnected(undefined, false)
    } catch (e) {
      console.error(e)
      const { message: title, trace_id: description } = e as ErrorResponse
      setPostDBError(e as ErrorResponse)
      toast({
        variant: 'destructive',
        title,
        description,
        action: (
          <ToastAction altText="Try again" onClick={onSubmit}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setIsAdding(false)
    }
  }

  const handleDialogOpenChange = (open: boolean) => {
    if (sampleDBAdded && !open) {
      setSampleDBAdded(false)
      onFinish && onFinish()
    }
    if (!open) {
      setPostDBError(null)
    }
  }

  return (
    <>
      <Dialog onOpenChange={handleDialogOpenChange}>
        <DialogTrigger asChild>
          <Button variant="outline" className="px-4 py-1.5 h-fit w-full">
            <TestTube2 className="mr-2" size={20} strokeWidth={1.5} />
            Add sample Database
          </Button>
        </DialogTrigger>
        <DialogContent
          showClose={!sampleDBAdded && !isAdding}
          className="min-h-[60vh] w-[100vw] max-w-3xl overflow-auto flex flex-col"
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          {sampleDBAdded ? (
            <>
              <DialogHeader className="flex-none px-1">
                <DialogTitle>
                  <div className="flex flex-row items-center gap-2">
                    <CheckCircle />
                    Sample Database added
                  </div>
                </DialogTitle>
                <DialogDescription>Connection successful!</DialogDescription>
              </DialogHeader>
              <div className="grow flex flex-col mt-5 gap-5 px-1">
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <Sparkles size={18} strokeWidth={1.5} />
                    <h2>Example Prompts</h2>
                  </div>
                  <p className="text-sm text-slate-500">
                    Explore the sample database in our Playground by selecting
                    one of the example prompts below.
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-6">
                  {selectedSampleDB?.example_prompts.map((prompt, idx) => (
                    <ContentBox
                      key={idx}
                      onClick={() => setExamplePrompt(prompt)}
                      className="flex flex-col items-end justify-between text-sm text-slate-600 gap-2 hover:bg-slate-100 hover:shadow-md cursor-pointer"
                    >
                      {prompt}
                      <ArrowRightCircle strokeWidth={1} />
                    </ContentBox>
                  ))}
                </div>
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="ghost">Close</Button>
                </DialogClose>
              </DialogFooter>
            </>
          ) : (
            <>
              <DialogHeader className="flex-none">
                <DialogTitle>Select a sample Database</DialogTitle>
                <DialogDescription>
                  Sample databases are pre-configured databases that you can add
                  to your account to get started.
                </DialogDescription>
              </DialogHeader>
              <div className="mt-3 grow flex flex-col gap-6">
                <div className="max-w-xs">
                  <Select
                    value={selectedSampleDB?.id}
                    onValueChange={handleSampleDBSelect}
                    disabled={
                      !sampleDBOptions ||
                      sampleDBOptions.length === 0 ||
                      isAdding
                    }
                  >
                    <SelectTrigger
                      aria-label="Database"
                      className="bg-white border-slate-300"
                    >
                      <SelectValue placeholder="Select a Database" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        {sampleDBOptions?.map(({ label, value, icon }, idx) => (
                          <SelectItem key={label + idx} value={value}>
                            <div className="flex items-center gap-2">
                              {icon}
                              {label}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                </div>
                {selectedSampleDB && (
                  <div className="flex flex-col gap-3 text-sm">
                    {selectedDBProvider && (
                      <div className="flex items-center gap-2">
                        <Image
                          priority
                          src={selectedDBProvider.logoUrl}
                          alt={`${selectedDBProvider.name} logo`}
                          width={32}
                          height={32}
                        />
                        <span className="text-lg">
                          {selectedSampleDB.alias}
                        </span>
                      </div>
                    )}
                    <p>{selectedSampleDB.description}</p>
                  </div>
                )}
                {postDBError && (
                  <Alert variant="destructive">
                    <AlertDescription className="break-words">
                      {postDBError.description || postDBError.message}
                    </AlertDescription>
                  </Alert>
                )}
              </div>
              <DialogFooter>
                <Button onClick={onSubmit} type="button" disabled={isAdding}>
                  {isAdding ? (
                    <>
                      <Loader
                        className="mr-2 animate-spin"
                        size={16}
                        strokeWidth={2.5}
                      />{' '}
                      Adding Database
                    </>
                  ) : (
                    'Add Database'
                  )}
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
      <Toaster />
    </>
  )
}

export default SampleDatabaseConnectionDialog
