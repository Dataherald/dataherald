import { Checkbox } from '@/components/ui/checkbox'
import { useTree } from '@/components/ui/tree-view-context'
import { cn } from '@/lib/utils'
import { ChevronDown, ChevronRight, LucideIcon } from 'lucide-react'
import { FC, HTMLAttributes, useEffect, useState } from 'react'

export interface TreeNode {
  id: string
  name: string
  type: string
  icon: LucideIcon
  children?: TreeNode[]
  defaultOpen?: boolean
  selectable?: boolean
  clickable?: boolean
  slot?: JSX.Element
}

interface TreeProps {
  node: TreeNode
  isRoot?: boolean
}

const TreeNodeComponent: FC<TreeProps> = ({
  node,
  isRoot = false,
}: TreeProps) => {
  const {
    selectedNodes,
    findSelectionNodeByName,
    handleNodeSelectionChange,
    setClickedRow,
  } = useTree()
  const [isOpen, setIsOpen] = useState(node.defaultOpen || false)
  const nodeHasChildren = !!node.children?.length

  const [checkboxState, setCheckboxState] = useState<'indeterminate' | boolean>(
    false,
  )

  const selectionNode = node.selectable
    ? findSelectionNodeByName(node.name)
    : null

  useEffect(() => {
    if (!selectedNodes.size) {
      // selection was cleared
      setCheckboxState(false)
      return
    }
    if (!selectionNode) return
    if (selectionNode.children?.length) {
      const allChildrenSelected = !selectionNode.children.some(
        (child) => !selectedNodes.has(child.name),
      )
      const someChildrenSelected = selectionNode.children.some((child) =>
        selectedNodes.has(child.name),
      )

      if (allChildrenSelected) {
        setCheckboxState(true)
      } else if (someChildrenSelected) {
        setCheckboxState('indeterminate')
      } else {
        setCheckboxState(false)
      }
    } else {
      // Directly set the state for leaf nodes
      setCheckboxState(selectedNodes.has(selectionNode.name))
    }
  }, [selectedNodes, selectionNode, setCheckboxState])

  const toggleNode = () => {
    handleNodeSelectionChange(selectionNode)
  }

  const handleRowClick = () => {
    if (node.clickable) {
      setClickedRow(node)
    }
  }

  return (
    <div className={isRoot ? 'pl-0' : 'pl-7'}>
      <div
        className={cn(
          checkboxState === true && 'bg-sky-100',
          node.clickable && 'cursor-pointer',
          'w-full flex items-center justify-between gap-2 rounded-lg hover:bg-slate-200 my-1 text-sm',
        )}
        onClick={handleRowClick}
      >
        <div
          className="flex items-center w-full px-3 py-2 "
          aria-expanded={isOpen}
        >
          {selectionNode ? (
            <Checkbox
              className="mr-2 h-4 w-4"
              checked={checkboxState}
              onCheckedChange={toggleNode}
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            !isRoot && <div className="w-7"></div>
          )}
          <div
            className={cn(
              'w-4',
              nodeHasChildren ? 'cursor-pointer' : 'cursor-default',
            )}
            onClick={(e) => {
              setIsOpen(!isOpen)
              e.stopPropagation()
            }}
          >
            {nodeHasChildren &&
              (isOpen ? (
                <ChevronDown size={16} strokeWidth={1.5} />
              ) : (
                <ChevronRight size={16} strokeWidth={1.5} />
              ))}
          </div>
          <div className="mx-2">
            <node.icon size={16} strokeWidth={1.5} />
          </div>
          <span className="break-all">{node.name}</span>
        </div>
        <div className="min-w-fit">{node.slot}</div>
      </div>
      {isOpen && nodeHasChildren && (
        <div className="transition-all duration-300">
          {node.children?.map((childNode, idx) => (
            <TreeNodeComponent key={idx} node={childNode} />
          ))}
        </div>
      )}
    </div>
  )
}

interface TreeViewProps {
  rootNode: TreeNode
}

const TreeView: FC<TreeViewProps & HTMLAttributes<HTMLDivElement>> = ({
  rootNode,
  className,
  ...props
}) => {
  const { setRootNode } = useTree()
  useEffect(() => {
    setRootNode(rootNode)
  }, [rootNode, setRootNode])
  return (
    <div className={cn('flex flex-col gap-1', className)} {...props}>
      <TreeNodeComponent node={rootNode} isRoot />
    </div>
  )
}

export { TreeView }
