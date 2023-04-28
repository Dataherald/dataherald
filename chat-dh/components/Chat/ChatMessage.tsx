import { Message } from "@/types/chat";
import { FC } from "react";
import { Icon } from "../Layout/Icon";
import Image from "next/image";
import { UserProfile, useUser } from "@auth0/nextjs-auth0/client";

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: FC<ChatMessageProps> = ({
  message: { role, content },
}) => {
  const { user } = useUser();
  const { picture: userPicture } = user as UserProfile;
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
      ) : userPicture ? (
        <Image
          src={userPicture}
          alt="User Profile Picture"
          width={35}
          height={35}
          className="rounded-full"
        />
      ) : (
        <Icon
          value="person_outline"
          className="rounded-full bg-gray-200 p-2"
        ></Icon>
      )}
      {typeof content === "string" ? (
        <p className="self-center pr-8">{content}</p>
      ) : (
        <div className="flex flex-col gap-5 pr-8">
          <p className="self-center">{content.generated_text}</p>
          <iframe
            className="min-h-[600px] mb-4"
            src={`https://dev.bariloche.dataherald.com/v4/viz/${content.viz_id}`}
          ></iframe>
        </div>
      )}
    </div>
  );
};
