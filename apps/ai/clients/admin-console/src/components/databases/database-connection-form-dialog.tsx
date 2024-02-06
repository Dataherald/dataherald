import DatabaseConnectionForm from '@/components/databases/database-connection-form'
import {
  DatabaseConnectionFormValues,
  dbConnectionFormSchema,
} from '@/components/databases/form-schema'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Databases } from '@/models/api'
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
import { formatDriver } from '@/lib/domain/database'
import { DatabaseConnection } from '@/models/api'
import { yupResolver } from '@hookform/resolvers/yup'
import {
  AlertCircle,
  CheckCircle,
  DatabaseZap,
  Loader,
  Plus,
} from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'

const mapDatabaseConnectionFormValues = (
  formValues: DatabaseConnectionFormValues,
): DatabaseConnection =>
  formValues.use_ssh === false
    ? {
        alias: formValues.alias,
        use_ssh: false,
        connection_uri:
          formatDriver(formValues.data_warehouse) + formValues.connection_uri,
      }
    : {
        alias: formValues.alias,
        use_ssh: true,
        connection_uri:
          formatDriver(formValues.data_warehouse) + formValues.connection_uri,
        ssh_settings: {
          host: formValues.ssh_settings.host as string,
          port: formValues.ssh_settings.port as string,
          username: formValues.ssh_settings.username as string,
          password: formValues.ssh_settings.password as string,
        },
      }

interface DatabaseConnectionFormDialogProps {
  isFirstConnection?: boolean
  onConnected: (newDatabases?: Databases, refresh?: boolean) => void
  onFinish?: () => void
}

const DatabaseConnectionFormDialog: FC<DatabaseConnectionFormDialogProps> = ({
  isFirstConnection = false,
  onConnected,
  onFinish,
}) => {
  const form = useForm<DatabaseConnectionFormValues>({
    resolver: yupResolver(dbConnectionFormSchema),
    defaultValues: {
      use_ssh: false,
      alias: '',
      connection_uri: '',
      file: null,
      ssh_settings: {
        host: '',
        port: '',
        username: '',
        password: '',
      },
    },
  })

  const [databaseConnected, setDatabaseConnected] = useState(false)

  const connectDatabase = usePostDatabaseConnection()

  const onSubmit = async () => {
    try {
      const formFieldsValues = form.getValues()
      const { file, ...dbConnectionFields } = formFieldsValues
      await connectDatabase(
        mapDatabaseConnectionFormValues(dbConnectionFields),
        file as File | null | undefined,
      )
      setDatabaseConnected(true)
      onConnected(undefined, false)
    } catch (e) {
      toast({
        variant: 'destructive',
        title: 'Oops! Something went wrong.',
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
      onFinish && onFinish()
    }
  }

  return (
    <>
      <Dialog onOpenChange={handleDialogOpenChange}>
        <DialogTrigger asChild>
          <Button size={isFirstConnection ? 'lg' : 'default'}>
            {isFirstConnection ? (
              <>
                <DatabaseZap className="mr-2" size={18} />
                Connect your Database
              </>
            ) : (
              <>
                <Plus className="mr-2" size={18} />
                Add Database
              </>
            )}
          </Button>
        </DialogTrigger>
        <DialogContent
          className="max-w-[70vw] lg:max-w-[700px] h-[75vh] flex flex-col"
          onInteractOutside={(e) => e.preventDefault()}
        >
          {databaseConnected ? (
            <>
              <DialogHeader className="flex-none px-1">
                <DialogTitle>
                  <div className="flex flex-row items-center gap-2">
                    <CheckCircle />
                    {isFirstConnection
                      ? 'Database Connected'
                      : 'Database Added'}
                  </div>
                </DialogTitle>
              </DialogHeader>
              <div className="grow flex flex-col gap-5 px-1">
                <p>
                  Connection successful! To begin using this database for
                  queries, select the tables you wish to scan and synchronize
                  with the platform.
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
                  <Button>Done</Button>
                </DialogClose>
              </DialogFooter>
            </>
          ) : (
            <>
              <DialogHeader className="flex-none px-1">
                <DialogTitle>
                  {isFirstConnection ? 'Connect your Database' : 'Add Database'}
                </DialogTitle>
                <DialogDescription>
                  {isFirstConnection
                    ? 'Connect your database to start using the platform.'
                    : 'Connect another database to the platform.'}
                </DialogDescription>
              </DialogHeader>
              <div className="grow flex flex-col overflow-auto p-1">
                <div className="grow">
                  <DatabaseConnectionForm form={form} />
                </div>
                <DialogFooter className="mt-5">
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
                        {isFirstConnection ? 'Connecting' : 'Adding'} Database
                      </>
                    ) : (
                      <>
                        {isFirstConnection
                          ? 'Connect Database'
                          : 'Add Database'}
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
      <Toaster />
    </>
  )
}

export default DatabaseConnectionFormDialog
