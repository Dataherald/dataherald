import * as React from 'react'

import { cn } from '@/lib/utils'

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <label className="flex items-center">
        <input
          type={type}
          className={cn('opacity-0 absolute h-0 w-0', className)}
          ref={ref}
          {...props}
        />
        {type === 'checkbox' && (
          <span
            className={cn(
              'h-5 w-5 cursor-pointer border border-gray-300 rounded-md',
              props.checked ? 'bg-black' : 'bg-white',
            )}
          ></span>
        )}
      </label>
    )
  },
)

Input.displayName = 'Input'

export { Input }
