import {
  SelectableTreeNode,
  TreeNode,
  buildSelectableTree,
  findLeafNodes,
} from '@/components/ui/tree-view'
import React, {
  ReactNode,
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react'

interface TreeContextProps {
  rootNode: TreeNode | null
  setRootNode: React.Dispatch<React.SetStateAction<TreeNode | null>>
  selectableRootNode: SelectableTreeNode | null
  selectedNodes: Set<string>
  setSelectedNodes: React.Dispatch<React.SetStateAction<Set<string>>>
  handleCheckboxChange: (node: SelectableTreeNode | null) => void
}

const TreeContext = createContext<TreeContextProps | undefined>(undefined)

export const TreeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [rootNode, setRootNode] = useState<TreeNode | null>(null)
  const [selectableRootNode, setSelectableRootNode] =
    useState<SelectableTreeNode | null>(null)
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set())

  const handleCheckboxChange = (node: SelectableTreeNode | null) => {
    if (!node) return
    if (!selectableRootNode) return

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

  useEffect(() => {
    if (rootNode) {
      const newSelectableRootNode = buildSelectableTree(rootNode, null, true)
      setSelectableRootNode(newSelectableRootNode)
    }
  }, [rootNode])

  const value = {
    rootNode,
    setRootNode,
    selectableRootNode,
    selectedNodes,
    setSelectedNodes,
    handleCheckboxChange,
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
