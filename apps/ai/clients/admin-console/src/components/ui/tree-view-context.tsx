import { TreeNode } from '@/components/ui/tree-view'
import {
  buildSelectionTree,
  findLeafNodes,
  findNodeByName,
} from '@/components/ui/tree-view.helpers'
import React, {
  ReactNode,
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react'

interface SelectionTreeNode {
  id: string
  name: string
  children?: SelectionTreeNode[]
}

interface TreeContextProps {
  rootNode: TreeNode | null
  setRootNode: React.Dispatch<React.SetStateAction<TreeNode | null>>
  selectedNodes: Set<string>
  findSelectionNodeByName: (nodeName: string) => SelectionTreeNode | null
  resetSelection: () => void
  handleNodeSelectionChange: (node: SelectionTreeNode | null) => void
}

const TreeContext = createContext<TreeContextProps | undefined>(undefined)

export const TreeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [rootNode, setRootNode] = useState<TreeNode | null>(null)
  const [selectionRootNode, setSelectionRootNode] =
    useState<SelectionTreeNode | null>(null)
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set())

  const handleNodeSelectionChange = (node: SelectionTreeNode | null) => {
    if (!node) return
    if (!selectionRootNode) return

    const newSelectedNodes = new Set(selectedNodes)

    if (node.children?.length === 0) {
      if (newSelectedNodes.has(node.name)) {
        newSelectedNodes.delete(node.name)
      } else {
        newSelectedNodes.add(node.name)
      }
    } else {
      const leafNodes = findLeafNodes(node)
      const allSelected = !leafNodes.some(
        (leaf) => !newSelectedNodes.has(leaf.name),
      )

      if (allSelected) {
        leafNodes.forEach((leaf) => newSelectedNodes.delete(leaf.name))
      } else {
        leafNodes.forEach((leaf) => newSelectedNodes.add(leaf.name))
      }
    }

    setSelectedNodes(newSelectedNodes)
  }

  const resetSelection = () => setSelectedNodes(new Set())

  const findSelectionNodeByName = (nodeName: string) =>
    findNodeByName(nodeName, selectionRootNode)

  useEffect(() => {
    if (rootNode) {
      const newSelectableRootNode = buildSelectionTree(rootNode, null, true)
      setSelectionRootNode(newSelectableRootNode)
    }
  }, [rootNode])

  const value = {
    rootNode,
    setRootNode,
    selectedNodes,
    findSelectionNodeByName,
    resetSelection,
    handleNodeSelectionChange,
  }

  return <TreeContext.Provider value={value}>{children}</TreeContext.Provider>
}

export const useTree = () => {
  const context = useContext(TreeContext)
  if (!context) {
    throw new Error('useTree must be used within a TreeProvider')
  }
  return context
}
