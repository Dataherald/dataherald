import { clsx, type ClassValue } from 'clsx'
import { ParsedUrlQuery } from 'querystring'
import { twMerge } from 'tailwind-merge'

export const cn = (...inputs: ClassValue[]): string => {
  return twMerge(clsx(inputs))
}

export const buildIdHref = (
  basePath: string,
  id: string,
  display_id: string,
): { pathname: string; query: ParsedUrlQuery } => ({
  pathname: `${basePath}/${id}`,
  query: { d_id: display_id },
})

export const formatUrl = (segment: string): string =>
  segment.replace('sql', 'SQL')

export const formatKey = (key: string): string =>
  key.replace('_', ' ').toLowerCase()
