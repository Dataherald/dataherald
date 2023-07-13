import { useChat } from '@/contexts/chat';
import { EMBED_URL } from '@/env-variables';
import { Message } from '@/types/chat';
import { UserProfile, useUser } from '@auth0/nextjs-auth0/client';
import Image from 'next/image';
import { FC, useEffect, useState } from 'react';
import { Icon } from '../Layout/Icon';
import ChatAssistantMessageActions from './ChatAssistantMessageActions';
import { ChatLoader } from './ChatLoader';
import { ChatText } from './ChatText';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: FC<ChatMessageProps> = ({ message }) => {
  const { role, content } = message;
  const { user } = useUser();
  const { picture: userPicture } = user as UserProfile;
  const [currentIframeLoading, setCurrentIframeLoading] = useState(false);
  const { loadingIframe, setLoadingIframe } = useChat();

  useEffect(() => {
    setLoadingIframe(currentIframeLoading);
  }, [currentIframeLoading, setLoadingIframe]);

  // some external flow needs to cancel the iframe loading.
  useEffect(() => {
    if (loadingIframe === false) setCurrentIframeLoading(loadingIframe);
  }, [loadingIframe, setCurrentIframeLoading]);

  useEffect(() => {
    if (!(typeof content === 'string')) {
      if (content.status === 'successful' && content.viz_id) {
        setCurrentIframeLoading(true);
      }
    }
  }, [content]);

  const handleIframeLoaded = () => setCurrentIframeLoading(false);

  return (
    <div className={`${role === 'user' && 'bg-gray-100'}`}>
      <div className=" max-w-[1000px] mx-auto">
        <div className="flex flex-col gap-3 p-8">
          <div
            className="flex flex-row items-center gap-3"
            style={{ overflowWrap: 'anywhere' }}
          >
            {role === 'assistant' ? (
              <Image
                src="/images/dh-logo-symbol-color.svg"
                alt="Dataherald company logo narrow"
                width={40}
                height={40}
                className="pl-1 self-start"
              />
            ) : userPicture ? (
              <Image
                src={userPicture}
                alt="User Profile Picture"
                width={35}
                height={35}
                className="rounded-full self-start"
              />
            ) : (
              <Icon
                value="person_outline"
                className="rounded-full bg-gray-200 p-2 self-start"
              ></Icon>
            )}
            {typeof content === 'string' ? (
              <ChatText text={content} />
            ) : content.status === 'successful' ? (
              <div className="flex-1 flex flex-col gap-5 pr-8 overflow-auto">
                {(!content.viz_id || !currentIframeLoading) && (
                  <ChatText text={content.generated_text as string} />
                )}
                {content.viz_id && (
                  <iframe
                    style={{ display: currentIframeLoading ? 'none' : 'flex' }}
                    className="min-h-[600px] mb-4 w-full min-w-[300px]"
                    src={`${EMBED_URL}${content.viz_id}?hideDemoLink=true`}
                    onLoad={handleIframeLoaded}
                  ></iframe>
                )}
              </div>
            ) : content.status === 'failed' ? (
              <div className="flex-1 flex flex-col gap-5 pr-8">
                <ChatText text={content.generated_text as string} />
                <Image
                  className="mx-auto"
                  src="/images/error/data_not_found.svg"
                  alt="Chat error image"
                  width={600}
                  height={300}
                />
              </div>
            ) : (
              <ChatText text={content.generated_text as string} />
            )}
          </div>
          {role === 'assistant' &&
            typeof content !== 'string' &&
            !currentIframeLoading && (
              <div className="self-center">
                <ChatAssistantMessageActions message={content} />
              </div>
            )}
        </div>
      </div>
    </div>
  );
};
