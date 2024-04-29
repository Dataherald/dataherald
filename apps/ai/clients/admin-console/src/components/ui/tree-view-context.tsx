import { TreeNode } from '@/components/ui/tree-view'
import { useGlobalTreeSelection } from '@/components/ui/tree-view-global-context'
import {
  buildSelectionTree,
  findLeafNodes,
  findNodeById,
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
  clickedRow: TreeNode | null
  setClickedRow: React.Dispatch<React.SetStateAction<TreeNode | null>>
  selectedNodes: Set<string>
  findSelectionNodeById: (nodeName: string) => SelectionTreeNode | null
  resetSelection: () => void
  handleNodeSelectionChange: (node: SelectionTreeNode | null) => void
}

const TreeContext = createContext<TreeContextProps | undefined>(undefined)

export const TreeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const { subscribeToReset, updateTreeSelection } = useGlobalTreeSelection()
  const [rootNode, setRootNode] = useState<TreeNode | null>(null)
  const [clickedRow, setClickedRow] = useState<TreeNode | null>(null)
  const [selectionRootNode, setSelectionRootNode] =
    useState<SelectionTreeNode | null>(null)
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set())

  const handleNodeSelectionChange = (node: SelectionTreeNode | null) => {
    if (!node) return
    if (!selectionRootNode) return

    const newSelectedNodes = new Set(selectedNodes)

    if (node.children?.length === 0) {
      if (newSelectedNodes.has(node.id)) {
        newSelectedNodes.delete(node.id)
      } else {
        newSelectedNodes.add(node.id)
      }
    } else {
      const leafNodes = findLeafNodes(node)
      const allSelected = !leafNodes.some(
        (leaf) => !newSelectedNodes.has(leaf.id),
      )

      if (allSelected) {
        leafNodes.forEach((leaf) => newSelectedNodes.delete(leaf.id))
      } else {
        leafNodes.forEach((leaf) => newSelectedNodes.add(leaf.id))
      }
    }

    setSelectedNodes(newSelectedNodes)
    updateTreeSelection(selectionRootNode.id, newSelectedNodes)
  }

  const resetSelection = () => setSelectedNodes(new Set())

  const findSelectionNodeById = (nodeId: string) =>
    findNodeById(nodeId, selectionRootNode)

  useEffect(() => {
    if (rootNode) {
      const newSelectableRootNode = buildSelectionTree(rootNode, null, true)
      setSelectionRootNode(newSelectableRootNode)
      subscribeToReset(resetSelection)
    }
  }, [rootNode, subscribeToReset])

  const value = {
    rootNode,
    setRootNode,
    selectedNodes,
    clickedRow,
    setClickedRow,
    findSelectionNodeById,
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
