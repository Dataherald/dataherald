import { ApiError } from 'next/dist/server/api-utils';
import { HTTP_METHOD } from 'next/dist/server/web/http';

export interface HTTP_OPTIONS {
  method?: HTTP_METHOD;
  body?: unknown;
  headers?: HeadersInit;
  signal?: AbortSignal;
}

export const fetchAPI = async <T>(
  url: string,
  options: HTTP_OPTIONS = {},
  queryParams?: Record<string, string>,
): Promise<T> => {
  const {
    method = 'GET',
    body,
    headers = { 'Content-Type': 'application/json' },
    signal,
  } = options;

  // Append query parameters to the URL, if provided
  if (queryParams) {
    const searchParams = new URLSearchParams(queryParams);
    url += `?${searchParams.toString()}`;
  }

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
      signal,
    });
    return response.json() as Promise<T>;
  } catch (error) {
    console.error('API Service Error:', (error as ApiError).message);
    throw error;
  }
};

export const isAbortError = (e: any) =>
  e instanceof DOMException && e.name === 'AbortError';
