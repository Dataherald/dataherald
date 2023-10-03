import { Checkbox } from '@/components/ui/checkbox'
import { useTree } from '@/components/ui/tree-view-context'
import { findNodeByName } from '@/components/ui/tree-view.helpers'
import { cn } from '@/lib/utils'
import { ChevronDown, ChevronRight, LucideIcon } from 'lucide-react'
import { FC, HTMLAttributes, useEffect, useState } from 'react'

export interface TreeNode {
  id: string
  name: string
  icon: LucideIcon
  children?: TreeNode[]
  defaultOpen?: boolean
  selectable?: boolean
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
  const { selectedNodes, selectionRootNode, handleNodeSelectionChange } =
    useTree()
  const [isOpen, setIsOpen] = useState(node.defaultOpen || false)
  const nodeHasChildren = !!node.children?.length

  const [checkboxState, setCheckboxState] = useState<'indeterminate' | boolean>(
    false,
  )

  const selectionNode = node.selectable
    ? findNodeByName(node.name, selectionRootNode)
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
  }, [selectedNodes, selectionNode, selectionRootNode, setCheckboxState])

  const toggleNode = () => {
    handleNodeSelectionChange(selectionNode)
  }

  return (
    <div className={isRoot ? 'pl-0' : 'pl-7'}>
      <div
        className={cn(
          checkboxState === true && 'bg-blue-100',
          'w-full flex items-center justify-between gap-2 rounded-lg hover:bg-gray-200 my-1',
        )}
      >
        <div
          className={cn(
            'flex items-center w-full px-3 py-2',
            nodeHasChildren ? 'cursor-pointer' : 'cursor-default',
          )}
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
        >
          {selectionNode ? (
            <Checkbox
              className="mr-2"
              checked={checkboxState}
              onCheckedChange={toggleNode}
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            !isRoot && <div className="w-7"></div>
          )}
          <div className="w-4">
            {nodeHasChildren &&
              (isOpen ? (
                <ChevronDown size={20} strokeWidth={1.5} />
              ) : (
                <ChevronRight size={20} strokeWidth={1.5} />
              ))}
          </div>
          <node.icon size={22} strokeWidth={1.5} className="mx-2" />
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
