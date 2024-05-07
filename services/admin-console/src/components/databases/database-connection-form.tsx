import { DatabaseConnectionFormValues } from '@/components/databases/form-schema'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'
import DATABASE_PROVIDERS from '@/constants/database-providers'
import { formatDriver, supportsSchemas } from '@/lib/domain/database'
import { AlertCircle, Eraser, FileKey2, X } from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'
import { FC, useEffect, useState } from 'react'
import { UseFormReturn } from 'react-hook-form'

const SSHForm: FC<{
  form: UseFormReturn<DatabaseConnectionFormValues>
}> = ({ form }) => (
  <>
    <div className="grid grid-cols-2 gap-4">
      <div className="max-w-full overflow-hidden text-slate-500 col-span-2 pt-1 flex items-center justify-evenly gap-2">
        <Separator className="bg-slate-500" />
        <div className="min-w-fit font-semibold">SSH settings</div>
        <Separator className="bg-slate-500" />
      </div>
      <Alert variant="info" className="col-span-2 flex items-center gap-2">
        <div>
          <FileKey2 size={22} className="text-slate-700" />
        </div>
        <AlertDescription>
          Download our{' '}
          <Link
            href="https://k2-public-resources.s3.amazonaws.com/prod_pem_key.pub"
            download
          >
            <Button
              type="button"
              variant="external-link"
              size="sm"
              className="p-0"
            >
              public SSH key
            </Button>
          </Link>{' '}
          and add it to the{' '}
          <span className="font-source-code text-xs bg-gray-100 border border-gray-400 text-gray-900 rounded py-0 px-1">
            authorized_keys
          </span>{' '}
          file from your server.
        </AlertDescription>
      </Alert>
      <FormField
        control={form.control}
        name="ssh_settings.host"
        render={({ field }) => (
          <FormItem>
            <FormLabel>SSH host</FormLabel>
            <FormControl>
              <Input placeholder="SSH host" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="ssh_settings.port"
        render={({ field }) => (
          <FormItem>
            <FormLabel>SSH port</FormLabel>
            <div className="flex items-center gap-3">
              <FormControl>
                <Input placeholder="SSH port" {...field} />
              </FormControl>
            </div>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="ssh_settings.username"
        render={({ field }) => (
          <FormItem>
            <FormLabel>SSH username</FormLabel>
            <FormControl>
              <Input placeholder="SSH username" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="ssh_settings.password"
        render={({ field }) => (
          <FormItem>
            <FormLabel>SSH password</FormLabel>
            <div className="flex items-center gap-3">
              <FormControl>
                <Input placeholder="SSH password" {...field} />
              </FormControl>
            </div>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  </>
)

const DatabaseConnectionForm: FC<{
  form: UseFormReturn<DatabaseConnectionFormValues>
}> = ({ form }) => {
  const { setValue, watch } = form
  const useSsh = watch('use_ssh')
  const dataWarehouse = watch('data_warehouse')
  const schemas = watch('schemas')
  const selectedDatabaseProvider = DATABASE_PROVIDERS.find(
    (dp) => dp.driver === dataWarehouse,
  )
  const [schemaInput, setSchemaInput] = useState('')

  useEffect(() => {
    setValue('schemas', [], { shouldValidate: true })
    if (selectedDatabaseProvider?.driver === 'bigquery') {
      setValue('use_ssh', false, { shouldValidate: true })
    } else {
      setValue('file', undefined, { shouldValidate: true })
    }
  }, [selectedDatabaseProvider, setValue])

  useEffect(() => {
    if (useSsh !== true) {
      setValue('ssh_settings', {}, { shouldValidate: true })
    }
    setValue('file', undefined, { shouldValidate: true })
  }, [setValue, useSsh])

  const handleSchemaEnter = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      if (!schemaInput) return
      const newSchemas = [...(schemas || []), schemaInput]
      updateSchemas(newSchemas)
      setSchemaInput('')
    }
  }

  const removeSchema = (schema: string) => {
    if (!schemas) return
    const newSchemas = schemas.filter((s) => s !== schema)
    updateSchemas(newSchemas)
  }

  const updateSchemas = (newSchemas: string[]) => {
    setValue('schemas', newSchemas, { shouldValidate: true })
  }

  return (
    <Form {...form}>
      <form>
        <fieldset
          disabled={form.formState.isSubmitting}
          className="flex flex-col gap-3"
        >
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="data_warehouse"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Data warehouse</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue
                          placeholder={
                            selectedDatabaseProvider ? (
                              <div className="flex items-center gap-2">
                                <Image
                                  priority
                                  src={selectedDatabaseProvider.logoUrl}
                                  alt={selectedDatabaseProvider.name}
                                  width={18}
                                  height={18}
                                />
                                {selectedDatabaseProvider.name}
                              </div>
                            ) : (
                              <span className="text-[#64748B]">
                                Select your database provider
                              </span>
                            )
                          }
                        />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {DATABASE_PROVIDERS?.map((option, idx) => (
                        <SelectItem key={idx} value={option.driver}>
                          <div className="flex items-center gap-2">
                            <Image
                              priority
                              src={option.logoUrl}
                              alt={option.name}
                              width={18}
                              height={18}
                            />
                            {option.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormItem>
              )}
            />
            {selectedDatabaseProvider?.driver === 'bigquery' ? (
              <Alert variant="info" className="self-end flex items-start gap-2">
                <div>
                  <AlertCircle />
                </div>
                <AlertDescription>
                  SSH tunnel is not supported for BigQuery data warehouse.
                </AlertDescription>
              </Alert>
            ) : (
              <div className="self-end justify-self-end pb-2">
                <FormField
                  control={form.control}
                  name="use_ssh"
                  render={({ field }) => (
                    <div className="flex items-center">
                      <FormLabel className="mr-2 font-normal pointer-events-none">
                        Connect through SSH tunnel
                      </FormLabel>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </div>
                  )}
                />
              </div>
            )}
          </div>
          <FormMessage>
            {form.getFieldState('data_warehouse').error?.message}
          </FormMessage>
          <FormField
            control={form.control}
            name="alias"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Alias</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Type an alias for the database"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="connection_uri"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Connection URI</FormLabel>
                <div className="flex items-start gap-3">
                  {selectedDatabaseProvider && (
                    <FormDescription className="py-2.5">
                      {`jdbc:${formatDriver(selectedDatabaseProvider.driver)}`}
                    </FormDescription>
                  )}
                  <FormControl>
                    <div className="w-full flex flex-col gap-2">
                      <Input placeholder="Connection URI" {...field} />
                      <FormMessage />
                    </div>
                  </FormControl>
                </div>
              </FormItem>
            )}
          />
          {supportsSchemas(selectedDatabaseProvider?.dialect) && (
            <FormField
              control={form.control}
              name="schemas"
              render={() => (
                <FormItem>
                  <FormLabel className="flex items-start gap-3">
                    Schemas
                    <FormDescription className="text-2xs h-fit">
                      Press Enter to add a schema
                    </FormDescription>
                  </FormLabel>
                  <FormControl>
                    <Input
                      value={schemaInput}
                      onKeyDown={handleSchemaEnter}
                      onChange={(e) => setSchemaInput(e.target.value)}
                      placeholder="Enter the schemas you want to connect to"
                    />
                  </FormControl>

                  <div className="flex items-center flex-wrap gap-2">
                    {schemas?.map((schema, idx) => (
                      <Badge
                        key={idx}
                        className="text-sm py-0.5 px-2 bg-slate-200 flex gap-1 font-medium"
                      >
                        {schema}
                        <Button
                          type="button"
                          variant="icon"
                          size="sm"
                          className="p-0 pl-1 h-fit"
                          onClick={() => removeSchema(schema)}
                        >
                          <X size={10} strokeWidth={3} />
                        </Button>
                      </Badge>
                    ))}
                    {!!schemas?.length && (
                      <Button
                        variant="ghost"
                        className="text-xs px-2 py-1 h-fit flex items-center gap-2"
                        onClick={() => updateSchemas([])}
                      >
                        <Eraser size={12} />
                        Clear
                      </Button>
                    )}
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}
          {selectedDatabaseProvider?.driver === 'bigquery' && (
            <FormField
              control={form.control}
              name="file"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Service Account Key File</FormLabel>
                  <FormControl>
                    <Input
                      className="cursor-pointer"
                      placeholder="Upload key file"
                      type="file"
                      ref={field.ref}
                      onChange={(e) => {
                        const files = e.target.files
                        if (files) {
                          setValue('file', files[0], {
                            shouldValidate: true,
                          })
                        }
                      }}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}
          {useSsh && <SSHForm form={form} />}
        </fieldset>
      </form>
    </Form>
  )
}

export default DatabaseConnectionForm
