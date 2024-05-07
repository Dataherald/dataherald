import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { ToastAction } from '@/components/ui/toast'
import { Toaster } from '@/components/ui/toaster'
import { toast } from '@/components/ui/use-toast'
import { usePostApiKey } from '@/hooks/api/api-keys/usePostApiKey'
import { copyToClipboard } from '@/lib/utils'
import { ErrorResponse } from '@/models/api'
import { yupResolver } from '@hookform/resolvers/yup'
import { Copy, Loader, Plus } from 'lucide-react'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const apiKeyFormSchema = Yup.object({
  name: Yup.string()
    .min(3, `The name is required and must have more than 3 characters`)
    .max(50, `The name must have less than 50 characters`)
    .required(),
})

type ApiKeyFormValues = Yup.InferType<typeof apiKeyFormSchema>

interface AddApiKeyDialogProps {
  onGeneratedKey: () => void
}

const GenerateApiKeyDialog: FC<AddApiKeyDialogProps> = ({ onGeneratedKey }) => {
  const [open, setOpen] = useState(false)
  const [generatingApiKey, setGeneratingApiKey] = useState(false)
  const [showNewKey, setShowNewKey] = useState(false)
  const [apiKey, setApiKey] = useState<string | undefined>()
  const postApiKey = usePostApiKey()

  const form = useForm<ApiKeyFormValues>({
    resolver: yupResolver(apiKeyFormSchema),
    defaultValues: {
      name: '',
    },
  })

  const handleClose = async () => {
    if (generatingApiKey) return
    setOpen(false)
    setShowNewKey(false)
    setApiKey(undefined)
    form.reset()
  }

  const handleCopyClick = async () => {
    try {
      await copyToClipboard(apiKey)
      toast({
        variant: 'success',
        title: 'API Key copied!',
      })
    } catch (error) {
      console.error('Could not copy text: ', error)
      toast({
        variant: 'destructive',
        title: 'Could not copy API Key',
      })
    }
  }

  const handleGenerateApiKey = async (apiKeyFormValues: ApiKeyFormValues) => {
    setGeneratingApiKey(true)
    try {
      const { api_key } = await postApiKey(apiKeyFormValues)
      setApiKey(api_key)
      onGeneratedKey()
      setShowNewKey(true)
      form.reset()
      toast({
        variant: 'success',
        title: 'Secret API key generated',
        description: `Your secret key was generated successfully.`,
      })
    } catch (e) {
      console.error(e)
      const { message: title, trace_id: description } = e as ErrorResponse
      toast({
        variant: 'destructive',
        title,
        description,
        action: (
          <ToastAction
            altText="Try again"
            onClick={() => form.handleSubmit(handleGenerateApiKey)()}
          >
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setGeneratingApiKey(false)
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={handleClose}>
      <Button onClick={() => setOpen(true)}>
        <Plus className="mr-2" size={16} />
        Generate new secret key
      </Button>
      <AlertDialogContent>
        <AlertDialogHeader>
          <h1 className="font-semibold">Generate new secret key</h1>
        </AlertDialogHeader>
        {showNewKey ? (
          <>
            <div className="flex flex-col">
              <p>
                Please save this secret key somewhere safe and accessible. For
                security reasons,{' '}
                <strong>{`you won't be able to view it again`}</strong>{' '}
                {`through your
            Dataherald account. If you lose this secret key, you'll need to
            generate a new one.`}
              </p>
              <div className="py-4 flex gap-2">
                <Input value={apiKey} readOnly />
                <Button onClick={handleCopyClick}>
                  <Copy size={20} />
                </Button>
              </div>
            </div>
            <AlertDialogFooter className="pt-4">
              <Button onClick={handleClose}>Done</Button>
            </AlertDialogFooter>
          </>
        ) : (
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(handleGenerateApiKey)}
              className="space-y-8 grow flex flex-col"
            >
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        disabled={generatingApiKey}
                        placeholder="My secret key name"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <AlertDialogFooter className="pt-4">
                <Button
                  type="button"
                  variant="ghost"
                  disabled={generatingApiKey}
                  onClick={handleClose}
                >
                  Cancel
                </Button>
                <Button>
                  {generatingApiKey ? (
                    <>
                      <Loader
                        className="mr-2 animate-spin"
                        size={20}
                        strokeWidth={2.5}
                      />{' '}
                      Generating key
                    </>
                  ) : (
                    'Generate secret key'
                  )}
                </Button>
              </AlertDialogFooter>
            </form>
          </Form>
        )}
      </AlertDialogContent>
      <Toaster />
    </AlertDialog>
  )
}

export default GenerateApiKeyDialog
