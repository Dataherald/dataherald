import { Message } from "@/types";
import { FC } from "react";
import { Icon } from "../Layout/Icon";
import Image from "next/image";

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: FC<ChatMessageProps> = ({
  message: { role, content },
}) => {
  return (
    <div
      className="flex flex-row items-start gap-3 rounded-xl border border-black p-4"
      style={{ overflowWrap: "anywhere" }}
    >
      {role === "assistant" ? (
        <Image
          src="/images/dh-logo-symbol-color.svg"
          alt="Dataherald company logo narrow"
          width={40}
          height={40}
          className="pl-1"
        />
      ) : (
        <Icon value="person_outline" className="rounded-full bg-primary bg-opacity-5 text-primary p-2"></Icon>
      )}
      <p className="self-center">{content}</p>
    </div>
  );
};
