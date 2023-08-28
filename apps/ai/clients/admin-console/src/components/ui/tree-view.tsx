import { cn } from '@/lib/utils'
import { ChevronDown, ChevronRight, LucideIcon } from 'lucide-react'
import { FC, HTMLAttributes, useState } from 'react'

export interface TreeNode {
  name: string
  icon: LucideIcon
  children?: TreeNode[]
}

type TreeProps = HTMLAttributes<HTMLDivElement> & {
  node: TreeNode
}

const TreeNodeComponent: FC<TreeProps> = ({
  node,
  className,
  ...props
}: TreeProps) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className={cn('pl-7', className)} {...props}>
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
  data: TreeNode
}

const TreeView: FC<TreeViewProps & HTMLAttributes<HTMLDivElement>> = ({
  data,
  ...props
}) => {
  return <TreeNodeComponent node={data} {...props} />
}

export { TreeView }
