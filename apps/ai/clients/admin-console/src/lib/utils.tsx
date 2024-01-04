import { clsx, type ClassValue } from 'clsx'
import { LucideIcon } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

export const cn = (...inputs: ClassValue[]): string => {
  return twMerge(clsx(inputs))
}

export const formatUrl = (segment: string): string =>
  segment.replace('sql', 'SQL')

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
    return <IconComponent {...config} />
  }
  return null
}

export const capitalize = (value: string) =>
  value
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

export const formatStatus = (status?: string): string =>
  status ? capitalize(status?.replace('_', ' ').toLowerCase()) : ''
