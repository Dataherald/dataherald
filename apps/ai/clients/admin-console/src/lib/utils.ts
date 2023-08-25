import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export const cn = (...inputs: ClassValue[]): string => {
  return twMerge(clsx(inputs))
}

export const formatUrl = (segment: string): string =>
  segment.replace('sql', 'SQL').replace('-', ' ')

export const formatKey = (key: string): string =>
  key.replace('_', ' ').toLowerCase()
