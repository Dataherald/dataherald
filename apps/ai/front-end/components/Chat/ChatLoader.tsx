import Image from 'next/image';
import { FC, useEffect, useState } from 'react';

const DEFAULT_MESSAGES = [
  {
    text: 'Loading...',
    image: '/images/loading/analyzing_data.svg',
    duration: 5000,
  },
  {
    text: 'Retrieving data sources...',
    image: '/images/loading/retrieving_data_sources.svg',
    duration: 8000,
  },
  {
    text: 'Analyzing data...',
    image: '/images/loading/analyzing_data.svg',
    duration: 8000,
  },
  {
    text: 'Generating visualization...',
    image: '/images/loading/generating_visualization.svg',
    duration: 8000,
  },
];

interface ChatLoaderMessage {
  text: string;
  image: string;
  duration: number;
}

interface ChatLoaderProps {
  messages?: ChatLoaderMessage[];
}

export const ChatLoader: FC<ChatLoaderProps> = ({
  messages = DEFAULT_MESSAGES,
}) => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (index === messages.length - 1) {
      return;
    }

    const timeout = setTimeout(() => {
      setIndex((prevIndex) => prevIndex + 1);
    }, messages[index].duration);

    return () => {
      clearTimeout(timeout);
    };
  }, [index, messages]);

  const { text, image } = messages[index];

  return (
    <div className="flex flex-col items-center gap-2 w-full">
      <Image src={image} alt="Loading image" width={500} height={200} />
      <p className="my-2 text-xl">{text}</p>
      <div className="bg-gray-200 w-full h-2 relative rounded overflow-hidden">
        <div className="h-full bg-progress-gradient animate-slide"></div>
      </div>
    </div>
  );
};
