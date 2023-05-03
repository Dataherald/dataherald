import Image from "next/image";
import { FC } from "react";

interface HeaderProps {
  title: string;
}

export const Header: FC<HeaderProps> = ({ title }) => {
  return (
    <div className="flex flex-col items-center">
      <Image
        src={"images/dh-logo-symbol-color.svg"}
        alt="Dataherald Company Logo"
        width={50}
        height={50}
        style={{ filter: "drop-shadow(0px 4px 25px rgba(0, 0, 0, 0.25))" }}
      />
      <h1 className="text-2xl font-bold mt-2 mb-4 text-center text-secondary-dark">
        {title}
      </h1>
    </div>
  );
};
