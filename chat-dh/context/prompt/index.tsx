import { FC, ReactNode, createContext, useContext, useState } from "react";

const PromptContext = createContext<{
  prompt: string | null;
  setPrompt: (prompt: string | null) => void;
}>({
  prompt: null,
  setPrompt: () => {},
});

export const usePrompt = () => useContext(PromptContext);

interface PromptProviderProps {
  children: ReactNode;
}

export const PromptProvider: FC<PromptProviderProps> = ({ children }) => {
  const [prompt, setPrompt] = useState<string | null>(null);

  return (
    <PromptContext.Provider value={{ prompt, setPrompt }}>
      {children}
    </PromptContext.Provider>
  );
};
