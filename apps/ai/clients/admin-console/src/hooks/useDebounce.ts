import { useEffect, useState } from 'react'

const DEFAULT_DEBOUNCE_DELAY = 500

/**
 * useDebounce hook to debounce a value over a specified delay.
 *
 * @param value The value to be debounced.
 * @param delay The debounce delay in milliseconds.
 * @returns The debounced value.
 */
function useDebounce<T>(value: T, delay = DEFAULT_DEBOUNCE_DELAY): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

export default useDebounce
