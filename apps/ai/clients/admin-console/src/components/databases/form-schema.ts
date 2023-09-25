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
  connection_uri: Yup.string().when('use_ssh', {
    is: false,
    then: (fieldSchema) =>
      fieldSchema
        .defined()
        .required("The database connection URI can't be empty")
        .max(250, 'The database connection URI is too long'),
    otherwise: (fieldSchema) => fieldSchema.notRequired().nullable(),
  }),
  file: Yup.mixed()
    .nullable()
    .when(['use_ssh', 'data_warehouse'], ([useSsh, data_warehouse], schema) => {
      return data_warehouse === 'bigquery'
        ? schema.required('Service account key file is required for BigQuery')
        : useSsh
        ? schema.required('Private key file is required')
        : schema.notRequired()
    }),
  ssh_settings: Yup.object<SshSettings>()
    .shape({
      db_driver: Yup.string(),
      db_name: Yup.string(),
      host: Yup.string(),
      username: Yup.string(),
      password: Yup.string(),
      remote_host: Yup.string(),
      remote_db_name: Yup.string(),
      remote_db_password: Yup.string(),
      private_key_password: Yup.string(),
    })
    .when('use_ssh', ([use_ssh], schema) => {
      return use_ssh === true
        ? schema
            .shape({
              db_driver: Yup.string().notRequired(),
              db_name: Yup.string().required(
                "The database name can't be empty",
              ),
              host: Yup.string().required("The host can't be empty"),
              username: Yup.string().required("The username can't be empty"),
              password: Yup.string().required("The password can't be empty"),
              remote_host: Yup.string().required(
                "The remote host can't be empty",
              ),
              remote_db_name: Yup.string().required(
                "The remote database name can't be empty",
              ),
              remote_db_password: Yup.string().required(
                "The remote database password can't be empty",
              ),
              private_key_password: Yup.string().notRequired(),
            })
            .required()
        : schema
            .shape({
              db_driver: Yup.string().notRequired(),
              db_name: Yup.string().notRequired(),
              host: Yup.string().notRequired(),
              username: Yup.string().notRequired(),
              password: Yup.string().notRequired(),
              remote_host: Yup.string().notRequired(),
              remote_db_name: Yup.string().notRequired(),
              remote_db_password: Yup.string().notRequired(),
              private_key_password: Yup.string().notRequired(),
            })
            .notRequired()
    }),
})

export type DatabaseConnectionFormValues = Yup.InferType<
  typeof dbConnectionFormSchema
>
