import { FC, ReactNode } from "react";
import { Sidebar } from "./Sidebar";

interface MainLayoutProps {
  mode?: "narrow" | "full";
  children: ReactNode;
}

export const MainLayout: FC<MainLayoutProps> = ({
  children,
  mode = "narrow",
}) => (
  <div className="flex flex-row h-screen">
    <Sidebar className="h-full overflow-none" />
    {mode === "narrow" ? (
      <div className="flex-grow flex flex-col overflow-auto">
        <div className="flex-grow flex flex-col w-full max-w-[1000px] mx-auto">
          {children}
        </div>
      </div>
    ) : (
      <div className="flex-grow flex flex-col overflow-auto">{children}</div>
    )}
  </div>
);
