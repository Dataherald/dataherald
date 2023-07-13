import { useChat } from '@/contexts/chat';
import { EMBED_URL } from '@/env-variables';
import { MessageContent } from '@/types/chat';
import Image from 'next/image';
import { FC, useEffect, useState } from 'react';
import ChatAssistantMessageActions from './ChatAssistantMessageActions';
import { ChatLoader } from './ChatLoader';
import { ChatText } from './ChatText';

interface ChatNewMessageProps {
  content: MessageContent;
}

export const ChatNewMessage: FC<ChatNewMessageProps> = ({ content }) => {
  const { setLoadingIframe, fetchingNewMessage, currentLoadingStage } =
    useChat();
  const [currentIframeLoading, setCurrentIframeLoading] = useState(true);

  useEffect(() => {
    setLoadingIframe(currentIframeLoading);
  }, [currentIframeLoading, setLoadingIframe]);

  useEffect(() => {
    if (content.status === 'failed') {
      setCurrentIframeLoading(false);
    }
  }, [content]);

  const handleIframeLoaded = () => setCurrentIframeLoading(false);
  return (
    <div className=" max-w-[1000px] mx-auto">
      <div className="flex flex-col gap-3 p-8">
        <div
          className="flex flex-row flex-start gap-3"
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
            className="flex flex-col flex-grow gap-3"
            style={{ overflowWrap: 'anywhere' }}
          >
            {content.generated_text && (
              <ChatText text={content.generated_text} />
            )}

            <div className="flex flex-grow items-center">
              {content.status === 'failed' ? (
                <Image
                  className="mx-auto"
                  src="/images/error/data_not_found.svg"
                  alt="Chat error image"
                  width={600}
                  height={300}
                />
              ) : (
                <div className="flex flex-grow item-center">
                  {content.viz_id && (
                    <iframe
                      style={{
                        display:
                          currentIframeLoading || fetchingNewMessage
                            ? 'none'
                            : 'flex',
                      }}
                      className="min-h-[600px] mb-4 w-full min-w-[300px]"
                      src={`${EMBED_URL}${content.viz_id}?hideDemoLink=true`}
                      onLoad={handleIframeLoaded}
                    ></iframe>
                  )}

                  {currentLoadingStage === 'viz_id' ? (
                    <ChatLoader key="regular-loading" />
                  ) : currentIframeLoading &&
                    currentLoadingStage === 'json_object' ? (
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
                  ) : (
                    <></>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {!fetchingNewMessage && (
          <div className="self-center">
            <ChatAssistantMessageActions message={content} />
          </div>
        )}
      </div>
    </div>
  );
};
