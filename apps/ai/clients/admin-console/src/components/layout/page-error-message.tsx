import { AlertOctagon } from 'lucide-react'
import { FC, HTMLAttributes } from 'react'

export type PageErrorMessageProps = HTMLAttributes<HTMLDivElement> & {
  message: string
}

const PageErrorMessage: FC<PageErrorMessageProps> = ({ message, ...props }) => (
  <div className="flex gap-3" {...props}>
    <AlertOctagon />
    <span>{message}</span>
  </div>
)

export default PageErrorMessage
