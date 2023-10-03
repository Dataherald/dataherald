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

export const findNodeByName = (
  nodeName: string,
  node: TreeNode | SelectionTreeNode | null,
): SelectionTreeNode | null => {
  if (!node) return null
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
