import { TreeNode } from '@/components/ui/tree-view'

export const buildSelectionTree = (
  originalNode: TreeNode,
  parentNode: SelectionTreeNode | null = null,
  isRoot = false,
): SelectionTreeNode | null => {
  let newSelectableNode: SelectionTreeNode | null = null

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
    buildSelectionTree(child, newSelectableNode || parentNode)
  })

  return isRoot ? newSelectableNode : newSelectableNode || parentNode
}

export const findNodeById = (
  nodeId: string,
  rootSearch: TreeNode | SelectionTreeNode | null,
): SelectionTreeNode | null => {
  if (!rootSearch) return null
  if (rootSearch.id === nodeId) {
    return rootSearch
  }

  for (const child of rootSearch.children || []) {
    const found = findNodeById(nodeId, child)
    if (found) {
      return found
    }
  }

  return null
}

export const findLeafNodes = (
  node: TreeNode | SelectionTreeNode,
  leaves: SelectionTreeNode[] = [],
): SelectionTreeNode[] => {
  if (!node.children || node.children.length === 0) {
    leaves.push(node)
    return leaves
  }

  for (const child of node.children) {
    findLeafNodes(child, leaves)
  }

  return leaves
}

export interface SelectionTreeNode {
  id: string
  name: string
  children?: SelectionTreeNode[]
}
