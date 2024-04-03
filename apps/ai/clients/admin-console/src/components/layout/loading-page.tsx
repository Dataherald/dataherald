import { Loader } from 'lucide-react'
import { FC } from 'react'

const LoadingPage: FC = () => (
  <div className="grow flex items-center justify-center text-slate-500">
    <Loader className="animate-spin" size="30" />
  </div>
)

export default LoadingPage
