import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { ToastAction } from '@/components/ui/toast'
import { toast } from '@/components/ui/use-toast'
import { useAppContext } from '@/contexts/app-context'
import { usePutOrganization } from '@/hooks/api/organization/usePutOrganization'
import { ErrorResponse } from '@/models/api'
import { yupResolver } from '@hookform/resolvers/yup'
import { AlertCircle, Edit, Loader } from 'lucide-react'
import Image from 'next/image'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as Yup from 'yup'

const llmApiKeyFormSchema = Yup.object({
  llm_api_key: Yup.string()
    .min(1, `The LLM API key can't be empty`)
    .required(`The LLM API key can't be empty`),
})

type LlmApiKeyFormValues = Yup.InferType<typeof llmApiKeyFormSchema>

interface LlmApiKeyConfigProps {
  onOrganizationUpdate: () => void
}

const LlmApiKeyConfig: FC<LlmApiKeyConfigProps> = ({
  onOrganizationUpdate,
}) => {
  const [updating, setUpdating] = useState(false)
  const [editEnabled, setEditEnabled] = useState(false)

  const { organization } = useAppContext()
  const putOrganization = usePutOrganization()

  const form = useForm<LlmApiKeyFormValues>({
    resolver: yupResolver(llmApiKeyFormSchema),
    defaultValues: {
      llm_api_key: '',
    },
  })

  const updateLlmApiKey = async () => {
    if (!organization) throw new Error('No organization found in app state')
    setUpdating(true)
    try {
      await putOrganization(organization.id, {
        ...organization,
        ...form.getValues(),
      })
      toast({
        variant: 'success',
        title: 'OpenAI API key updated',
        description: `The OpenAI API key has been updated.`,
      })
      onOrganizationUpdate()
      setEditEnabled(false)
      form.reset()
    } catch (e) {
      console.error(e)
      const { message: title, trace_id: description } = e as ErrorResponse
      toast({
        variant: 'destructive',
        title,
        description,
        action: (
          <ToastAction altText="Try again" onClick={() => updateLlmApiKey()}>
            Try again
          </ToastAction>
        ),
      })
      form.setError('llm_api_key', {
        message: 'Invalid API key',
      })
    } finally {
      setUpdating(false)
    }
  }

  const handleCancel = () => {
    form.reset()
    setEditEnabled(false)
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <Image
          src="/images/openai.png"
          width={20}
          height={20}
          alt="Slack icon"
        />
        <h1 className="font-semibold">OpenAI API Key</h1>
      </div>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(updateLlmApiKey)}
          className="mt-3 grow space-y-4 flex flex-col"
        >
          <FormDescription>
            Connect your own OpenAI API key to the platform
          </FormDescription>
          <FormField
            control={form.control}
            name="llm_api_key"
            render={({ field }) => (
              <FormItem>
                <div className="flex items-center justify-between gap-2">
                  <FormLabel>
                    {editEnabled ? 'Enter your API key' : 'API Key'}
                  </FormLabel>
                  <Button
                    variant="link"
                    type="button"
                    disabled={editEnabled}
                    className="text-sm text-black flex items-center gap-1 p-0"
                    onClick={() => setEditEnabled(true)}
                  >
                    <Edit size={14} strokeWidth={2}></Edit>
                    Edit
                  </Button>
                </div>
                <FormControl>
                  <Input
                    {...field}
                    placeholder={
                      editEnabled
                        ? ''
                        : 'sk-••••••••••••••••••••••••••••••••••••••••••••••••'
                    }
                    disabled={!editEnabled || updating}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          {!editEnabled && (
            <Alert variant="info" className="flex items-center gap-2">
              <div>
                <AlertCircle size={14} />
              </div>
              <AlertDescription className="text-xs">
                The API Key is not visible for security reasons
              </AlertDescription>
            </Alert>
          )}
          {editEnabled && (
            <div className="flex items-center justify-between gap-2">
              <Button variant="ghost" type="button" onClick={handleCancel}>
                Cancel
              </Button>
              <Button type="submit" disabled={updating}>
                {updating ? (
                  <>
                    <Loader
                      className="mr-2 animate-spin"
                      size={20}
                      strokeWidth={2.5}
                    />{' '}
                    Saving
                  </>
                ) : (
                  'Save'
                )}
              </Button>
            </div>
          )}
        </form>
      </Form>
    </>
  )
}

export default LlmApiKeyConfig
