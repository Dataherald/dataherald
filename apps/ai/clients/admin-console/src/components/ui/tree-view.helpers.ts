import { TreeNode } from '@/components/ui/tree-view'

export const buildSelectableTree = (
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
    buildSelectableTree(child, newSelectableNode || parentNode)
  })

  return isRoot ? newSelectableNode : newSelectableNode || parentNode
}

export const findNodeByName = (
  nodeName: string,
  node: SelectableTreeNode | null,
): SelectableTreeNode | null => {
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
