import { FC, useState, useEffect } from "react";
import Image from "next/image";

const messages = [
  { text: "Loading...", image: "/images/loading/analyzing_data.svg" },
  {
    text: "Retrieving data sources...",
    image: "/images/loading/retrieving_data_sources.svg",
  },
  { text: "Analyzing data...", image: "/images/loading/analyzing_data.svg" },
  {
    text: "Generating visualization...",
    image: "/images/loading/generating_visualization.svg",
  },
];

export const ChatLoader: FC = () => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % messages.length);
    }, 7500);

    return () => {
      clearInterval(interval);
    };
  }, []);

  const { text, image } = messages[index];

  return (
    <div className="flex flex-col items-center w-full">
      <Image
        src={image}
        alt="Loading image"
        width={500}
        height={200}
      />
      <p className="my-2 text-xl">{text}</p>
      <div className="bg-gray-200 w-full h-2 relative rounded overflow-hidden">
        <div className="h-full bg-progress-gradient animate-slide"></div>
      </div>
    </div>
  );
};
