import { FC, HTMLAttributes } from 'react'

const QueriesLayout: FC<HTMLAttributes<HTMLDivElement>> = ({ children }) => (
  <div className="container mx-auto p-8">
    <div className="rounded-xl bg-gray-100 p-6 flex flex-col gap-4 max-h-[calc(100vh-150px)]">
      {children}
    </div>
  </div>
)

export default QueriesLayout
