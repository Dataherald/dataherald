import { CSSProperties, FC } from 'react';
import sanitizeHtml from 'sanitize-html';

interface ChatTextProps {
  className?: string;
  style?: CSSProperties;
  text: string;
}

export const ChatText: FC<ChatTextProps> = ({
  text,
  className = '',
  style = {},
}) => {
  const sanitizedText = sanitizeHtml(text, {
    allowedTags: ['p'],
    allowedAttributes: {},
  });

  const paragraphs = sanitizedText
    .split('\n')
    .map((paragraph, index) => <p key={index}>{paragraph}</p>);

  return (
    <div className={`prose ${className}`} style={style}>
      {paragraphs}
    </div>
  );
};
