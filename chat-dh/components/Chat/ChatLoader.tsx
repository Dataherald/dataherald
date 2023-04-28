import { IconDots } from "@tabler/icons-react";
import { FC } from "react";

interface ChatLoaderProps {}

export const ChatLoader: FC<ChatLoaderProps> = () => {
  return (
    <div className="flex flex-col flex-start">
      <div
        className={`flex items-center bg-primary text-white rounded-2xl px-4 py-2 w-fit`}
        style={{ overflowWrap: "anywhere" }}
      >
        <IconDots className="animate-pulse" />
      </div>
    </div>
  );
};
