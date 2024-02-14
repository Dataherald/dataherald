import { clsx, type ClassValue } from 'clsx'
import { format } from 'date-fns'
import { LucideIcon } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

export const cn = (...inputs: ClassValue[]): string => {
  return twMerge(clsx(inputs))
}

export const formatUrl = (segment: string): string =>
  segment
    .replace(/-/g, ' ')
    .replace('sql', 'SQL')
    .replace('api', 'API')
    .replace('fine tuning', 'fine-tuning')

export const formatKey = (key: string): string =>
  key.replace('_', ' ').toLowerCase()

export const renderIcon = (
  IconComponent: LucideIcon | null,
  config: { className?: string; size?: number; strokeWidth?: number } = {
    className: '',
    size: 16,
    strokeWidth: 2,
  },
) => {
  if (IconComponent) {
    return (
      <IconComponent
        {...config}
        className={
          IconComponent?.displayName === 'Loader' ? 'animate-spin' : ''
        }
      />
    )
  }
  return null
}

export const copyToClipboard = async (value?: string): Promise<void> => {
  if (!value) return
  return navigator.clipboard.writeText(value)
}

export const capitalize = (value: string) =>
  value
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

export const capitalizeFirstLetter = (value: string) =>
  value
    .split(' ')
    .map((word, index) =>
      index === 0
        ? word.charAt(0).toUpperCase() + word.slice(1)
        : word.toLowerCase(),
    )
    .join(' ')

export const formatStatus = (status?: string): string =>
  status ? capitalize(status?.replace('_', ' ').toLowerCase()) : ''

// Convert values from cents to dollars
export const toDollars = (value: number, withDecimals = true): string =>
  (value / 100).toFixed(withDecimals ? 2 : 0)

export const toCents = (value: number): number => value * 100

export const toDateCycle = (start: string, end: string): string =>
  format(new Date(start), 'MMM d') + ' - ' + format(new Date(end), 'MMM d')
