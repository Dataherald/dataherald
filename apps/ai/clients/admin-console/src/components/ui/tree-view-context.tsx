import {
  SelectableTreeNode,
  TreeNode,
  createSelectableTree,
  findLeafNodes,
  findNodeByName,
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
  handleCheckboxChange: (nodeName: string) => void
}

const TreeContext = createContext<TreeContextProps | undefined>(undefined)

export const TreeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [rootNode, setRootNode] = useState<TreeNode | null>(null)
  const [selectableRootNode, setSelectableRootNode] =
    useState<SelectableTreeNode | null>(null)
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set())

  const handleCheckboxChange = (nodeName: string) => {
    if (!selectableRootNode) return
    const node = findNodeByName(nodeName, selectableRootNode)

    if (!node) return

    const newSelectedNodes = new Set(selectedNodes)

    if (node.children?.length === 0) {
      if (newSelectedNodes.has(nodeName)) {
        newSelectedNodes.delete(nodeName)
      } else {
        newSelectedNodes.add(nodeName)
      }
    } else {
      const leafNodes = findLeafNodes(node)
      const allSelected = leafNodes.every((leaf) =>
        newSelectedNodes.has(leaf.name),
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
      const newSelectableRootNode = createSelectableTree(rootNode, null, true)
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
