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
import { useAppContext } from '@/contexts/app-context'
import usePostDatabaseConnection from '@/hooks/api/usePostDatabaseConnection'
import { formatDriver } from '@/lib/domain/database'
import { cn } from '@/lib/utils'
import { DatabaseConnection } from '@/models/api'
import { yupResolver } from '@hookform/resolvers/yup'
import { AlertCircle, CheckCircle, Loader, UploadCloud } from 'lucide-react'
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
        ssh_settings: {
          db_driver: formValues.data_warehouse,
          db_name: formValues.ssh_settings.db_name as string,
          host: formValues.ssh_settings.host as string,
          username: formValues.ssh_settings.username as string,
          password: formValues.ssh_settings.password as string,
          remote_host: formValues.ssh_settings.remote_host as string,
          remote_db_name: formValues.ssh_settings.remote_db_name as string,
          remote_db_password: formValues.ssh_settings
            .remote_db_password as string,
          private_key_password: formValues.ssh_settings.private_key_password,
        },
      }

const DatabaseConnectionFormDialog: FC<{
  onConnected: () => void
  onFinish: () => void
}> = ({ onConnected, onFinish }) => {
  const form = useForm<DatabaseConnectionFormValues>({
    resolver: yupResolver(dbConnectionFormSchema),
    defaultValues: {
      use_ssh: false,
      alias: '',
      connection_uri: '',
      file: null,
      ssh_settings: {
        db_driver: '',
        db_name: '',
        host: '',
        username: '',
        password: '',
        remote_host: '',
        remote_db_name: '',
        remote_db_password: '',
        private_key_password: '',
      },
    },
  })

  const [databaseConnected, setDatabaseConnected] = useState(false)

  const connectDatabase = usePostDatabaseConnection()
  const { updateOrganization } = useAppContext()

  const onSubmit = async () => {
    try {
      const formFieldsValues = form.getValues()
      const { file, ...dbConnectionFields } = formFieldsValues
      await connectDatabase(
        mapDatabaseConnectionFormValues(dbConnectionFields),
        file as File | null | undefined,
      )
      await updateOrganization()
      setDatabaseConnected(true)
      onConnected()
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
      onFinish()
    }
  }

  const isSshFormDisplayed = form.watch('use_ssh')

  return (
    <>
      <Dialog onOpenChange={handleDialogOpenChange}>
        <DialogTrigger asChild>
          <Button size="lg">
            <UploadCloud className="mr-2" size={20} />
            Connect your Database
          </Button>
        </DialogTrigger>
        <DialogContent
          className={cn(
            isSshFormDisplayed ? 'h-[90vh]' : 'h-[70vh]',
            'max-w-[70vw] lg:max-w-[700px] flex flex-col',
          )}
          onInteractOutside={(e) => e.preventDefault()}
        >
          {databaseConnected ? (
            <>
              <DialogHeader className="flex-none px-1">
                <DialogTitle>
                  <div className="flex flex-row items-center gap-2">
                    <CheckCircle />
                    Database connected
                  </div>
                </DialogTitle>
              </DialogHeader>
              <div className="grow flex flex-col gap-5 px-1">
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
                  <Button>Done</Button>
                </DialogClose>
              </DialogFooter>
            </>
          ) : (
            <>
              <DialogHeader className="flex-none px-1">
                <DialogTitle>Connect your Database</DialogTitle>
                <DialogDescription>
                  Connect your database to start using the platform.
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
                        Connecting
                      </>
                    ) : (
                      'Connect Database'
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
