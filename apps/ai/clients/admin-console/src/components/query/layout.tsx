import { FC, HTMLAttributes } from 'react'

const QueryLayout: FC<HTMLAttributes<HTMLDivElement>> = ({ children }) => (
  <div className="rounded-xl border bg-gray-50 p-6 gap-4 flex-1 flex flex-col max-h-[calc(100vh-110px)]">
    {children}
  </div>
)

export default QueryLayout
