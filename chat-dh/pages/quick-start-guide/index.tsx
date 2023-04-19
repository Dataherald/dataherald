import { Header } from "@/components/Layout/Header";
import { MainLayout } from "@/components/Layout/Main";
import { FC } from "react";

const QuickStartGuide: FC = () => (
  <MainLayout>
    <div className="max-w-[800px] mx-auto mt-4 sm:mt-12">
      <Header title="Dataherald AI Quick Start Guide"></Header>
    </div>
  </MainLayout>
);

export default QuickStartGuide;
