import DATABASE_PROVIDERS from '@/constants/database-providers'
import { z } from 'zod'

export const dbConnectionFormSchema = z.object({
  data_warehouse: z.enum(
    DATABASE_PROVIDERS.map(({ driver }) => driver) as [string],
    { required_error: 'Please select a data warehouse' },
  ),
  use_ssh: z.boolean(),
  alias: z
    .string({ required_error: "The database alias can't be empty" })
    .min(1, { message: `The database alias can't be empty` })
    .max(50, { message: 'The database alias is too long' }),
  connection_uri: z
    .string({ required_error: "The database connection URI can't be empty" })
    .min(1, { message: `The database connection URI can't be empty` })
    .max(250, { message: 'The database connection URI is too long' }),
})

export type DatabaseConnectionFormValues = z.infer<
  typeof dbConnectionFormSchema
>
