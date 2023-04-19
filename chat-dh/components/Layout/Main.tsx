import { FC, ReactNode } from "react";
import { Sidebar } from "./Sidebar";

interface MainLayoutProps {
  children: ReactNode;
}

export const MainLayout: FC<MainLayoutProps> = ({ children }) => (
  <div className="flex flex-row h-screen">
    <Sidebar />
    <div className="flex flex-1 overflow-auto sm:px-10 pb-4 sm:pb-10">
      {children}
    </div>
  </div>
);
