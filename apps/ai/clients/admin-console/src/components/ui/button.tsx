import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import * as React from 'react'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:ring-offset-1 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-black/80 text-white hover:bg-black',
        outline:
          'border border-slate-900 bg-white text-slate-900 hover:bg-slate-100',
        primary: 'bg-primary text-gray-100 hover:opacity-90',
        secondary: 'bg-secondary text-secondary-foreground hover:opacity-90',
        'secondary-outline':
          'border border-secondary bg-white text-secondary hover:bg-muted',
        destructive:
          'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        ['destructive-outline']:
          'bg-white text-destructive border-destructive hover:bg-destructive/10',
        ghost: 'hover:bg-slate-200 text-slate-900',
        'ghost-outline':
          'bg-transparent border border-slate-200 hover:bg-slate-200 text-slate-900',
        link: 'text-primary underline-offset-4 hover:underline',
        ['external-link']:
          'font-semibold text-blue-700 hover:text-blue-900 text-sm hover:no-underline p-0',
        icon: 'text-slate-900 p-0 h-fit',
      },
      size: {
        default: 'h-8 px-4 py-2',
        sm: 'h-9 rounded-md px-3 text-sm',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-fit p-2',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  },
)
Button.displayName = 'Button'

export { Button, buttonVariants }
