import { EMBED_URL } from "@/env-variables";
import apiService from "@/services/api";
import { MessageContent } from "@/types/chat";
import { FC, useEffect, useRef, useState } from "react";
import Button from "../Layout/Button";
import ButtonGroup from "../Layout/ButtonGroup";

const getEmbedCode = (viz_id: string) =>
  `<iframe style="display:block;" width="100%" height="600px" src="${EMBED_URL}${viz_id}" class="hg-data-interactive" frameborder="0" scrolling="no"></iframe>`;

interface ChatAssistantMessageActionsProps {
  message: MessageContent;
}

const ChatAssistantMessageActions: FC<ChatAssistantMessageActionsProps> = ({
  message: { generated_text, viz_id, status, id: chatResponseId },
}) => {
  const [textCopied, setTextCopied] = useState(false);
  const [embedCopied, setEmbedCopied] = useState(false);
  const [thumbsUpClicked, setThumbsUpClicked] = useState(false);
  const [thumbsDownClicked, setThumbsDownClicked] = useState(false);
  const textTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const embedTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (textTimeoutRef.current) clearTimeout(textTimeoutRef.current);
      if (embedTimeoutRef.current) clearTimeout(embedTimeoutRef.current);
    };
  }, []);

  const copy = async (valueToCopy: string) => {
    await navigator.clipboard.writeText(valueToCopy);
  };

  const handleCopyText = async () => {
    await copy(generated_text as string);
    setTextCopied(true);
    if (textTimeoutRef.current) clearTimeout(textTimeoutRef.current);
    textTimeoutRef.current = setTimeout(() => setTextCopied(false), 1500);
  };

  const handleCopyEmbed = async () => {
    if (!viz_id) return;
    await copy(getEmbedCode(viz_id));
    setEmbedCopied(true);
    if (embedTimeoutRef.current) clearTimeout(embedTimeoutRef.current);
    embedTimeoutRef.current = setTimeout(() => setEmbedCopied(false), 1500);
  };

  const handleThumbsUpClick = async () => {
    try {
      apiService.feedback(chatResponseId as string, true);
      setThumbsUpClicked(true);
      setThumbsDownClicked(false);
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  const handleThumbsDownClick = async () => {
    try {
      apiService.feedback(chatResponseId as string, false);
      setThumbsUpClicked(false);
      setThumbsDownClicked(true);
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  return (
    <>
      {status === "successful" && (
        <>
          <ButtonGroup>
            {!thumbsDownClicked && (
              <Button
                icon="thumb_up"
                color="primary-light"
                className={`hover:bg-gray-200 ${
                  thumbsUpClicked
                    ? "text-green-700 pointer-events-none"
                    : "text-secondary-dark"
                }`}
                onClick={handleThumbsUpClick}
              />
            )}
            {!thumbsUpClicked && (
              <Button
                icon="thumb_down"
                color="primary-light"
                className={`hover:bg-gray-200 ${
                  thumbsDownClicked
                    ? "text-red-600 pointer-events-none"
                    : "text-secondary-dark"
                }`}
                onClick={handleThumbsDownClick}
              />
            )}
          </ButtonGroup>
          <ButtonGroup>
            <Button
              color="primary-light"
              icon={textCopied ? "check" : "content_copy"}
              className={`hover:bg-gray-200 ${
                textCopied
                  ? "text-green-700 pointer-events-none"
                  : "text-secondary-dark"
              }`}
              onClick={handleCopyText}
            >
              Copy Text
            </Button>
            {viz_id && (
              <Button
                color="primary-light"
                icon={embedCopied ? "check" : "code"}
                className={`hover:bg-gray-200 ${
                  embedCopied
                    ? "text-green-700 pointer-events-none"
                    : "text-secondary-dark"
                }`}
                onClick={handleCopyEmbed}
              >
                Copy Visualization Embed
              </Button>
            )}
          </ButtonGroup>
        </>
      )}
    </>
  );
};

export default ChatAssistantMessageActions;
