import DatabaseConnectionForm from '@/components/databases/database-connection-form'
import {
  DatabaseConnectionFormValues,
  dbConnectionFormSchema,
} from '@/components/databases/form-schema'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
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
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import usePostDatabaseConnection from '@/hooks/api/usePostDatabaseConnection'
import { zodResolver } from '@hookform/resolvers/zod'
import { AlertCircle, CheckCircle, Loader, UploadCloud } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'

const DatabaseConnectionFormDialog: FC<{
  onConnected: () => void
  onFinish: () => void
}> = ({ onConnected, onFinish }) => {
  const form = useForm<DatabaseConnectionFormValues>({
    resolver: zodResolver(dbConnectionFormSchema as never),
    defaultValues: {
      use_ssh: false,
      alias: '',
      connection_uri: '',
      file: '',
    },
  })

  const [databaseConnected, setDatabaseConnected] = useState(false)

  const connectDatabase = usePostDatabaseConnection()

  const onSubmit = async () => {
    if (!form.formState.isValid) return
    try {
      const formFieldsValues = form.getValues()
      const { file, ...dbConnectionFields } = formFieldsValues
      await connectDatabase(dbConnectionFields, file)
      setDatabaseConnected(true)
      onConnected()
    } catch (e) {
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description: 'There was a problem connecting your Database.',
        action: (
          <ToastAction
            altText="Try again"
            onClick={() => form.handleSubmit(onSubmit)()}
          >
            Try again
          </ToastAction>
        ),
      })
    }
  }

  const handleDialogOpenChange = (open: boolean) => {
    if (databaseConnected && !open) {
      form.reset()
      setDatabaseConnected(false)
      onFinish()
    }
  }

  return (
    <>
      <Dialog onOpenChange={handleDialogOpenChange}>
        <DialogTrigger asChild>
          <Button size="lg">
            <UploadCloud className="mr-2" />
            Connect your Database
          </Button>
        </DialogTrigger>
        <DialogContent className="h-[80vh] max-w-[70vw] lg:max-w-[700px] flex flex-col">
          {databaseConnected ? (
            <>
              <DialogHeader className="flex-none">
                <DialogTitle>
                  <div className="flex flex-row items-center gap-2">
                    <CheckCircle />
                    Database connected
                  </div>
                </DialogTitle>
              </DialogHeader>
              <div className="grow flex flex-col gap-5">
                <p>
                  Connection successful! To begin using this database for
                  queries, select the tables you wish to synchronize with the
                  platform.
                </p>
                <Alert variant="info" className="flex items-start gap-2">
                  <div>
                    <AlertCircle />
                  </div>
                  <AlertDescription>
                    This process can take a few minutes for small tables up to
                    several hours for large datasets.
                  </AlertDescription>
                </Alert>
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button>Finish</Button>
                </DialogClose>
              </DialogFooter>
            </>
          ) : (
            <>
              <DialogHeader className="flex-none">
                <DialogTitle>Connect Database</DialogTitle>
                <DialogDescription>
                  Connect your database to start using the platform.
                </DialogDescription>
              </DialogHeader>
              <div className="grow">
                <DatabaseConnectionForm form={form} />
              </div>
              <DialogFooter>
                <Button
                  onClick={form.handleSubmit(onSubmit)}
                  type="button"
                  disabled={form.formState.isSubmitting}
                >
                  {form.formState.isSubmitting ? (
                    <>
                      <Loader
                        className="mr-2 animate-spin"
                        size={16}
                        strokeWidth={2.5}
                      />{' '}
                      Connecting
                    </>
                  ) : (
                    <>
                      <UploadCloud
                        size={16}
                        strokeWidth={2.5}
                        className="mr-2"
                      />
                      Connect
                    </>
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

export default DatabaseConnectionFormDialog
