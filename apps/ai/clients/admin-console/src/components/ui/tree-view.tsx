import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { useTree } from '@/components/ui/tree-view-context'
import { cn } from '@/lib/utils'
import { ChevronDown, ChevronRight, Edit } from 'lucide-react'
import { FC, HTMLAttributes, MouseEvent, useEffect, useState } from 'react'

export interface TreeNode {
  id: string
  name: string
  type: string
  icon: JSX.Element
  children?: TreeNode[]
  defaultOpen?: boolean
  selectable?: boolean
  clickable?: boolean
  slot?: JSX.Element
  showId?: boolean
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
    findSelectionNodeById,
    handleNodeSelectionChange,
    setClickedRow,
  } = useTree()
  const [isOpen, setIsOpen] = useState(node.defaultOpen || false)
  const nodeHasChildren = !!node.children?.length

  const [checkboxState, setCheckboxState] = useState<'indeterminate' | boolean>(
    false,
  )

  const selectionNode = node.selectable ? findSelectionNodeById(node.id) : null

  useEffect(() => {
    if (!selectedNodes.size) {
      // selection was cleared
      setCheckboxState(false)
      return
    }
    if (!selectionNode) return
    if (selectionNode.children?.length) {
      const allChildrenSelected = !selectionNode.children.some(
        (child) => !selectedNodes.has(child.id),
      )
      const someChildrenSelected = selectionNode.children.some((child) =>
        selectedNodes.has(child.id),
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
      setCheckboxState(selectedNodes.has(selectionNode.id))
    }
  }, [selectedNodes, selectionNode, setCheckboxState])

  const toggleNode = () => {
    handleNodeSelectionChange(selectionNode)
  }

  const handleRowClick = (e: MouseEvent) => {
    e.stopPropagation()
    if (node.clickable) {
      setClickedRow(node)
    }
  }

  return (
    <div className={cn('flex flex-col gap-1', isRoot ? 'pl-0 my-0.5' : 'pl-7')}>
      <Button
        variant="ghost"
        className={cn(
          !nodeHasChildren &&
            !node.clickable &&
            !node.selectable &&
            'pointer-events-none',
          !nodeHasChildren && 'cursor-default',
          checkboxState !== false
            ? 'bg-sky-100 hover:bg-sky-100'
            : 'hover:bg-slate-200',
          'h-fit px-3 py-0 grow flex items-center justify-between gap-2 rounded-lg text-sm ',
        )}
        onClick={(e) => {
          setIsOpen(!isOpen)
          e.stopPropagation()
        }}
      >
        <div className="grow flex items-center" aria-expanded={isOpen}>
          {selectionNode ? (
            <Checkbox
              className="mr-2 h-4 w-4"
              checked={checkboxState}
              onCheckedChange={toggleNode}
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            !isRoot && <div className="w-6"></div>
          )}
          <div className="w-6 flex justify-center">
            {nodeHasChildren &&
              (isOpen ? (
                <ChevronDown size={16} strokeWidth={1.8} />
              ) : (
                <ChevronRight size={16} strokeWidth={1.8} />
              ))}
          </div>
          <div className="mx-1.5">{node.icon}</div>
          <Button
            variant="icon"
            className={cn(
              'flex items-center gap-5 group pl-2 py-0',
              !node.clickable && 'pointer-events-none',
            )}
            onClick={handleRowClick}
          >
            <div className={cn('flex items-end gap-2')}>
              <span className="break-all">{node.name}</span>
              {node.showId && (
                <span className="break-all text-2xs text-slate-500">
                  {node.id}
                </span>
              )}
            </div>
            {node.clickable && (
              <Edit
                className="invisible group-hover:visible"
                size={14}
                strokeWidth={2}
              />
            )}
          </Button>
        </div>
        <div className="min-w-fit">{node.slot}</div>
      </Button>
      {isOpen &&
        nodeHasChildren &&
        node.children?.map((childNode, idx) => (
          <TreeNodeComponent key={idx} node={childNode} />
        ))}
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
