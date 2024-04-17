import React, { ReactNode, createContext, useContext, useState } from 'react'

interface SelfServePlaygroundContextType {
  dbConnectionId: string | null
  examplePrompt: string | null
  setSelfServePlaygroundData: (
    dbConnectionId: string,
    examplePrompt: string,
  ) => void
  clearSelfServePlaygroundData: () => void
}

const SelfServePlaygroundContext = createContext<
  SelfServePlaygroundContextType | undefined
>(undefined)

export const SelfServeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [dbConnectionId, setDbConnectionId] = useState<string | null>(null)
  const [examplePrompt, setExamplePrompt] = useState<string | null>(null)

  const setSelfServePlaygroundData = (
    newDbConnectionId: string,
    newExamplePrompt: string,
  ) => {
    setDbConnectionId(newDbConnectionId)
    setExamplePrompt(newExamplePrompt)
  }

  const clearSelfServePlaygroundData = () => {
    setDbConnectionId(null)
    setExamplePrompt(null)
  }

  return (
    <SelfServePlaygroundContext.Provider
      value={{
        dbConnectionId,
        examplePrompt,
        setSelfServePlaygroundData,
        clearSelfServePlaygroundData,
      }}
    >
      {children}
    </SelfServePlaygroundContext.Provider>
  )
}

export const useSelfServePlayground = () => {
  const context = useContext(SelfServePlaygroundContext)
  if (context === undefined) {
    throw new Error(
      'useSelfServePlayground must be used within a SubscriptionProvider',
    )
  }
  return context
}
