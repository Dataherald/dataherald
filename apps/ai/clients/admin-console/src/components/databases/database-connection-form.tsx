import { DatabaseConnectionFormValues } from '@/components/databases/form-schema'
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
import { Switch } from '@/components/ui/switch'
import DATABASE_PROVIDERS from '@/constants/database-providers'
import Image from 'next/image'
import { FC } from 'react'
import { UseFormReturn } from 'react-hook-form'

const DatabaseConnectionForm: FC<{
  form: UseFormReturn<DatabaseConnectionFormValues>
}> = ({ form }) => {
  const selectedDatabaseProvider = DATABASE_PROVIDERS.find(
    (dp) => dp.driver === form.watch('data_warehouse'),
  )

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
                  <FormLabel>Data Warehouse</FormLabel>
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
                                  style={{ objectFit: 'contain' }}
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
                              style={{
                                width: 18,
                                height: 18,
                                objectFit: 'contain',
                              }}
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
            <div className="self-end justify-self-end pb-2">
              <FormField
                control={form.control}
                name="use_ssh"
                render={({ field }) => (
                  <div className="flex items-center">
                    <FormLabel className="mr-2 font-normal">
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
          </div>
          <FormMessage>
            {form.control.getFieldState('data_warehouse').error?.message}
          </FormMessage>
          <FormField
            control={form.control}
            name="alias"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Database Alias</FormLabel>
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
                <div className="flex items-center gap-3">
                  {selectedDatabaseProvider && (
                    <FormDescription>{`jdbc:${selectedDatabaseProvider.driver}://`}</FormDescription>
                  )}
                  <FormControl>
                    <Input placeholder="Connection URI" {...field} />
                  </FormControl>
                </div>
                <FormMessage />
              </FormItem>
            )}
          />
        </fieldset>
      </form>
    </Form>
  )
}

export default DatabaseConnectionForm
