import React, {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'

type GlobalTreeSelectionState = {
  [treeId: string]: Set<string>
}

interface GlobalTreeSelectionContextProps {
  globalSelection: GlobalTreeSelectionState
  globalSelectionSize: number
  updateTreeSelection: (treeId: string, selectedNodeIds: Set<string>) => void
  getTreeSelection: (treeId: string) => Set<string>
  subscribeToReset: (resetCallback: () => void) => () => void
  triggerReset: () => void
}

export const GlobalTreeSelectionContext =
  createContext<GlobalTreeSelectionContextProps | null>(null)

interface GlobalTreeSelectionProviderProps {
  children: ReactNode
}

export const GlobalTreeSelectionProvider: React.FC<
  GlobalTreeSelectionProviderProps
> = ({ children }) => {
  const [globalSelection, setGlobalSelection] =
    useState<GlobalTreeSelectionState>({})
  const [resetSubscribers, setResetSubscribers] = useState<(() => void)[]>([])

  const globalSelectionSize = useMemo(() => {
    return Object.values(globalSelection).reduce((acc, curr) => {
      return acc + curr.size
    }, 0)
  }, [globalSelection])

  const updateTreeSelection = useCallback(
    (treeId: string, selectedNodeIds: Set<string>) => {
      setGlobalSelection((prevState) => {
        return {
          ...prevState,
          [treeId]: new Set(selectedNodeIds),
        }
      })
    },
    [],
  )

  const getTreeSelection = useCallback(
    (treeId: string) => {
      return globalSelection[treeId] || new Set<string>()
    },
    [globalSelection],
  )

  const subscribeToReset = useCallback((callback: () => void) => {
    setResetSubscribers((prev) => [...prev, callback])
    return () =>
      setResetSubscribers((prev) => prev.filter((cb) => cb !== callback))
  }, [])

  const triggerReset = useCallback(() => {
    resetSubscribers.forEach((reset) => reset())
    setGlobalSelection({})
  }, [resetSubscribers])

  const contextValue = useMemo(
    () => ({
      globalSelection,
      globalSelectionSize,
      updateTreeSelection,
      getTreeSelection,
      subscribeToReset,
      triggerReset,
    }),
    [
      globalSelection,
      globalSelectionSize,
      updateTreeSelection,
      getTreeSelection,
      subscribeToReset,
      triggerReset,
    ],
  )

  return (
    <GlobalTreeSelectionContext.Provider value={contextValue}>
      {children}
    </GlobalTreeSelectionContext.Provider>
  )
}

export const useGlobalTreeSelection = () => {
  const context = useContext(GlobalTreeSelectionContext)
  if (!context) {
    throw new Error(
      'useGlobalTreeSelection must be used within a GlobalTreeSelectionProvider',
    )
  }
  return context
}
