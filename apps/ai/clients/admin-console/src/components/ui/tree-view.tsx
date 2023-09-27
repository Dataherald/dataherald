import { Checkbox } from '@/components/ui/checkbox'
import { useTree } from '@/components/ui/tree-view-context'
import { cn } from '@/lib/utils'
import { ChevronDown, ChevronRight, LucideIcon } from 'lucide-react'
import { FC, HTMLAttributes, useEffect, useState } from 'react'

export const findSelectableNodeByName = (
  nodeName: string,
  rootTree: SelectableTreeNode | null,
): SelectableTreeNode | null => {
  if (!rootTree) return null
  if (rootTree.name === nodeName) {
    return rootTree
  }
  for (const child of rootTree.children || []) {
    const found = findSelectableNodeByName(nodeName, child)
    if (found) {
      return found
    }
  }
  return null
}

export const createSelectableTree = (
  originalNode: TreeNode,
  parentNode: SelectableTreeNode | null = null,
  isRoot = false,
): SelectableTreeNode | null => {
  let newSelectableNode: SelectableTreeNode | null = null

  if (originalNode.selectable || isRoot) {
    newSelectableNode = {
      id: originalNode.id,
      name: originalNode.name,
      children: [],
    }

    if (parentNode?.children) {
      parentNode.children.push(newSelectableNode)
    }
  }

  originalNode.children?.forEach((child) => {
    createSelectableTree(child, newSelectableNode || parentNode)
  })

  return isRoot ? newSelectableNode : newSelectableNode || parentNode
}

export const findNodeByName = (
  nodeName: string,
  node: SelectableTreeNode,
): SelectableTreeNode | null => {
  if (node.name === nodeName) {
    return node
  }

  for (const child of node.children || []) {
    const found = findNodeByName(nodeName, child)
    if (found) {
      return found
    }
  }

  return null
}

export const findLeafNodes = (
  node: SelectableTreeNode,
  leaves: SelectableTreeNode[] = [],
): SelectableTreeNode[] => {
  if (!node.children || node.children.length === 0) {
    leaves.push(node)
    return leaves
  }

  for (const child of node.children) {
    findLeafNodes(child, leaves)
  }

  return leaves
}

export interface SelectableTreeNode {
  id: string
  name: string
  children?: SelectableTreeNode[]
}
export interface TreeNode {
  id: string
  name: string
  icon: LucideIcon
  children?: TreeNode[]
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
  const { selectedNodes, selectableRootNode, handleCheckboxChange } = useTree()
  const [isOpen, setIsOpen] = useState(false)
  const nodeHasChildren = !!node.children?.length

  const [checkboxState, setCheckboxState] = useState<'indeterminate' | boolean>(
    false,
  )

  const selectionNode = node.selectable
    ? findSelectableNodeByName(node.name, selectableRootNode)
    : null

  useEffect(() => {
    if (selectionNode) {
      if (selectionNode.children?.length) {
        const allChildrenSelected = selectionNode.children.every((child) =>
          selectedNodes.has(child.name),
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
    }
  }, [selectedNodes, selectionNode, selectableRootNode, setCheckboxState])

  const toggleNode = () => {
    handleCheckboxChange(node.name)
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
            !isRoot && <div className="w-5"></div>
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
          <span>{node.name}</span>
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
