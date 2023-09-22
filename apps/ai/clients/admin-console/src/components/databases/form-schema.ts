import DATABASE_PROVIDERS from '@/constants/database-providers'
import { z } from 'zod'

export const dbConnectionFormSchema = z
  .object({
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
    file: z.union([z.null({}), z.any()]).optional(),
  })
  .superRefine((values, ctx) => {
    if (values.data_warehouse === 'bigquery' && !values.file) {
      ctx.addIssue({
        message: 'Service account key file is required for BigQuery',
        code: z.ZodIssueCode.custom,
        path: ['file'],
      })
    }
  })

export type DatabaseConnectionFormValues = z.infer<
  typeof dbConnectionFormSchema
>
