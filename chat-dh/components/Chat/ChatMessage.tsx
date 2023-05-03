import { Message } from "@/types/chat";
import { UserProfile, useUser } from "@auth0/nextjs-auth0/client";
import Image from "next/image";
import { FC } from "react";
import { Icon } from "../Layout/Icon";
import { ChatLoader } from "./ChatLoader";

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: FC<ChatMessageProps> = ({
  message: { role, content },
}) => {
  const { user } = useUser();
  const { picture: userPicture } = user as UserProfile;

  const regularParagraph = (text: string) => (
    <p className="self-center">{text}</p>
  );

  return (
    <div className={`w-full ${role === 'user' && 'bg-gray-100'}`}>
      <div className="w-full max-w-[1000px] mx-auto">
        <div
          className="flex flex-row items-start gap-3 p-8"
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
            regularParagraph(content)
          ) : content.status === "successful" ? (
            <div className="flex flex-col gap-5 pr-8 overflow-auto">
              <p className="self-center">{content.generated_text}</p>
              {content.viz_id && (
                <iframe
                  className="min-h-[600px] mb-4 w-full min-w-[300px]"
                  src={`https://dev.bariloche.dataherald.com/v4/viz/${content.viz_id}?hideDemoLink=true`}
                ></iframe>
              )}
            </div>
          ) : content.status === "failed" ? (
            <div className="flex flex-col gap-5 pr-8">
              <p className="self-center">{content.generated_text}</p>
              <Image
                className="mx-auto"
                src="/images/error/data_not_found.svg"
                alt="Chat error image"
                width={600}
                height={300}
              />
            </div>
          ) : content.status === "loading" ? (
            <div className="flex-1 flex items-center">
              <ChatLoader />
            </div>
          ) : (
            regularParagraph(content.generated_text as string)
          )}
        </div>
      </div>
    </div>
  );
};
