import { Organization } from '@/models/api'

export const isEnterprise = (organization?: Organization | null): boolean =>
  organization?.invoice_details.plan === 'ENTERPRISE'
