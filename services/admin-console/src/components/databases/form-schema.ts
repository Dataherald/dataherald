import DATABASE_PROVIDERS from '@/constants/database-providers'
import { SshSettings } from '@/models/api'
import * as Yup from 'yup'

export const dbConnectionFormSchema = Yup.object({
  data_warehouse: Yup.string()
    .oneOf(DATABASE_PROVIDERS.map(({ driver }) => driver))
    .required('Please select a data warehouse'),
  use_ssh: Yup.boolean().defined().required(),
  alias: Yup.string()
    .required("The database alias can't be empty")
    .max(50, 'The database alias is too long'),
  connection_uri: Yup.string()
    .required("The database connection URI can't be empty")
    .max(250, 'The database connection URI is too long'),
  schemas: Yup.array().of(Yup.string().required('Schema cannot be empty')),
  file: Yup.mixed()
    .nullable()
    .when(['data_warehouse'], ([data_warehouse], schema) => {
      return data_warehouse === 'bigquery'
        ? schema.required('Service account key file is required for BigQuery')
        : schema.notRequired()
    }),
  ssh_settings: Yup.object<SshSettings>()
    .shape({
      host: Yup.string(),
      port: Yup.string(),
      username: Yup.string(),
      password: Yup.string(),
    })
    .when('use_ssh', ([use_ssh], schema) => {
      return use_ssh === true
        ? schema
            .shape({
              host: Yup.string().required("The SSH host can't be empty"),
              port: Yup.string(),
              username: Yup.string().required(
                "The SSH username can't be empty",
              ),
              password: Yup.string(),
            })
            .required()
        : schema
            .shape({
              host: Yup.string().notRequired(),
              port: Yup.string().notRequired(),
              username: Yup.string().notRequired(),
              password: Yup.string().notRequired(),
            })
            .notRequired()
    }),
})

export type DatabaseConnectionFormValues = Yup.InferType<
  typeof dbConnectionFormSchema
>
