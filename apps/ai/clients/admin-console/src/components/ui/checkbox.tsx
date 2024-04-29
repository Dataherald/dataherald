import * as CheckboxPrimitive from '@radix-ui/react-checkbox'
import { Check, Minus } from 'lucide-react'
import * as React from 'react'

import { cn } from '@/lib/utils'

const Checkbox = React.forwardRef<
  React.ElementRef<typeof CheckboxPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root> & {
    checked: boolean | 'indeterminate'
  }
>(({ className, checked, ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={cn(
      'peer h-5 w-5 shrink-0 rounded-sm border border-slate-600 ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-50',
      checked === true
        ? 'bg-black/90 text-white'
        : checked === 'indeterminate'
        ? 'bg-slate-400 text-white'
        : '',
      className,
    )}
    {...props}
  >
    <div className="flex items-center justify-center">
      {checked === true && <Check size={12} strokeWidth={5} />}
      {checked === 'indeterminate' && <Minus size={12} strokeWidth={5} />}
    </div>
  </CheckboxPrimitive.Root>
))

Checkbox.displayName = CheckboxPrimitive.Root.displayName

export { Checkbox }
