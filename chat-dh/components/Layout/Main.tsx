import { FC, ReactNode } from "react";
import { Sidebar } from "./Sidebar";

interface MainLayoutProps {
  children: ReactNode;
}

export const MainLayout: FC<MainLayoutProps> = ({ children }) => (
  <div className="flex flex-row h-screen">
    <Sidebar className="h-full overflow-none" />
    <div className="flex-grow flex flex-col overflow-auto px-4">
      <div className="flex-grow flex flex-col w-full max-w-[1000px] mx-auto">
        {children}
      </div>
    </div>
  </div>
);
