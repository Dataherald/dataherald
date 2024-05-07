import { FC } from 'react'

export interface QueryProcessProps {
  processSteps: string[]
}

const QueryProcess: FC<QueryProcessProps> = ({ processSteps }) => (
  <ol>
    {processSteps.map((step, idx) => (
      <li key={idx} className="mb-2 last:mb-0">
        <div className="flex gap-2">
          <span className="text-primary font-bold">{idx + 1}. </span>
          {step}
        </div>
      </li>
    ))}
  </ol>
)

export default QueryProcess
