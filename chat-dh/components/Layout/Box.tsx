import { FC, ReactNode } from "react";

interface BoxProps {
  children: ReactNode;
}

export const Box: FC<BoxProps> = ({ children }) => {
  return (
    <div className="w-54 h-50 bg-white border rounded-2xl border-black border-opacity-40 p-5">
      {children}
    </div>
  );
};
