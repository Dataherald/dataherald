import { FC, HTMLAttributes } from 'react'

const QueryLayout: FC<HTMLAttributes<HTMLDivElement>> = ({ children }) => (
  <div className="rounded-xl border bg-gray-50 p-6 flex flex-col gap-4 max-h-[calc(100vh-150px)]">
    {children}
  </div>
)

export default QueryLayout
