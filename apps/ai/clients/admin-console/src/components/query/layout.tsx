import { FC, HTMLAttributes } from 'react'

const QueryLayout: FC<HTMLAttributes<HTMLDivElement>> = ({ children }) => (
  <div className="grow flex flex-col gap-4 rounded-xl border bg-gray-50 p-6">
    {children}
  </div>
)

export default QueryLayout
