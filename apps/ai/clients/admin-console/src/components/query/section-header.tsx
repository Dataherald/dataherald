import { FC, ReactNode } from 'react'

export const SectionHeader: FC<{ children: ReactNode }> = ({ children }) => (
  <div className="bg-slate-200 w-full px-6 py-3 flex items-center justify-between gap-2">
    {children}
  </div>
)

export const SectionHeaderTitle: FC<{ children: ReactNode }> = ({
  children,
}) => (
  <div className="flex items-center gap-3 font-bold text-lg">{children}</div>
)
