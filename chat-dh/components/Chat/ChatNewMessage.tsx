import { useChat } from '@/contexts/chat';
import { EMBED_URL } from '@/env-variables';
import { Message, MessageContent } from '@/types/chat';
import { UserProfile, useUser } from '@auth0/nextjs-auth0/client';
import Image from 'next/image';
import { FC, useEffect, useCallback, useLayoutEffect, useState } from 'react';
import { Icon } from '../Layout/Icon';
import ChatAssistantMessageActions from './ChatAssistantMessageActions';
import { ChatLoader } from './ChatLoader';
import { ChatText } from './ChatText';

interface ChatNewMessageProps {
  content: MessageContent;
}

export const ChatNewMessage: FC<ChatNewMessageProps> = ({ content }) => {
  const { setLoadingIframe } = useChat();
  const [currentIframeLoading, setCurrentIframeLoading] = useState(false);

  useEffect(() => {
    setLoadingIframe(currentIframeLoading);
  }, [currentIframeLoading, setLoadingIframe]);

  useEffect(() => {
    if (content.status === 'successful' && content.viz_id) {
      setCurrentIframeLoading(true);
    }
  }, [content]);

  const handleIframeLoaded = () => setCurrentIframeLoading(false);
  return (
    <div className=" max-w-[1000px] mx-auto">
      <div className="flex flex-col gap-3 p-8">
        <div
          className="flex flex-row items-center gap-3"
          style={{ overflowWrap: 'anywhere' }}
        >
          <Image
            src="/images/dh-logo-symbol-color.svg"
            alt="Dataherald company logo narrow"
            width={40}
            height={40}
            className="pl-1 self-start"
          />
          <div
            className="flex flex-col items-center gap-3"
            style={{ overflowWrap: 'anywhere' }}
          >
            {content.generated_text && (
              <ChatText text={content.generated_text} />
            )}
          </div>
        </div>
        <div className="flex-1 flex items-center">
          {currentIframeLoading && (
            <ChatLoader
              key="iframe-loading"
              messages={[
                {
                  text: 'Generating visualization...',
                  image: '/images/loading/generating_visualization.svg',
                  duration: 2000,
                },
              ]}
            />
          )}
          {content.status === 'successful' && content.viz_id ? (
            <iframe
              style={{ display: currentIframeLoading ? 'none' : 'flex' }}
              className="min-h-[600px] mb-4 w-full min-w-[300px]"
              src={`${EMBED_URL}${content.viz_id}?hideDemoLink=true`}
              onLoad={handleIframeLoaded}
            ></iframe>
          ) : content.status === 'failed' ? (
            <Image
              className="mx-auto"
              src="/images/error/data_not_found.svg"
              alt="Chat error image"
              width={600}
              height={300}
            />
          ) : (
            <ChatLoader key="regular-loading" />
          )}
        </div>
        {!currentIframeLoading && (
          <div className="self-center">
            <ChatAssistantMessageActions message={content} />
          </div>
        )}
      </div>
    </div>
  );
};
