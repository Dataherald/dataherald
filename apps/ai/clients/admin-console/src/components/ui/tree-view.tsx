import { cn } from '@/lib/utils'
import { ChevronDown, ChevronRight, LucideIcon } from 'lucide-react'
import { FC, HTMLAttributes, useState } from 'react'

export interface TreeNode {
  name: string
  icon: LucideIcon
  children?: TreeNode[]
}

interface TreeProps {
  node: TreeNode
}

const TreeNodeComponent: FC<TreeProps> = ({ node }: TreeProps) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="pl-7">
      <button
        className="flex items-center cursor-pointer hover:bg-gray-200 p-2 rounded w-full"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <div className="w-4">
          {node.children &&
            (isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />)}
        </div>
        <node.icon size={20} className="mx-2" />
        <span>{node.name}</span>
      </button>
      {isOpen && node.children && (
        <div className="transition-all duration-300">
          {node.children.map((childNode, idx) => (
            <TreeNodeComponent key={idx} node={childNode} />
          ))}
        </div>
      )}
    </div>
  )
}

interface TreeViewProps {
  data: TreeNode[]
}

const TreeView: FC<TreeViewProps & HTMLAttributes<HTMLDivElement>> = ({
  data,
  className,
  ...props
}) => (
  <div className={cn('flex flex-col gap-1', className)} {...props}>
    {data.map((node, idx) => (
      <TreeNodeComponent key={idx} node={node} />
    ))}
  </div>
)

export { TreeView }
