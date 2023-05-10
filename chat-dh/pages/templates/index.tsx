import { Header } from "@/components/Layout/Header";
import { IconType, IconValue } from "@/components/Layout/Icon";
import { MainLayout } from "@/components/Layout/Main";
import { Tile } from "@/components/Templates/Tile";
import Head from "next/head";
import { FC } from "react";

interface TemplateTiles {
  icon: IconValue;
  title: string;
  description: string;
  iconType?: IconType;
  href?: string;
  disabled?: boolean;
}

const TILES: TemplateTiles[] = [
  {
    icon: "handshake",
    title: "Offer Memorandum",
    description:
      "Quickly create an offering memorandum with investment data and property photos",
    disabled: true,
  },
  {
    icon: "rss_feed",
    title: "Blog Post",
    description:
      "Start a blog post using your own data or supplement with Dataherald sources",
    disabled: true,
  },
  {
    icon: "smartphone",
    title: "Social Media Post",
    description: "Create clear, concise data content for social media",
    disabled: true,
  },
  {
    icon: "description",
    title: "Newsletter",
    description:
      "Link a dataset and let Dataherald summarize key metrics and visualize trends",
    disabled: true,
  },
  {
    icon: "email",
    title: "Marketing Email",
    description:
      "Marketing emails with data visualizations have a 22% clickrate than those without",
    disabled: true,
  },
];

const Templates: FC = () => {
  return (
    <>
      <Head>
        <title>Dataherald AI | Templates</title>
        <meta
          name="description"
          content="Options for generating templated content with Dataherald AI"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <MainLayout>
        <div className="flex-1 flex flex-col gap-2 py-6 px-4">
          <Header title="Coming soon - create templated content with a single prompt "></Header>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-8 py-2 px-8">
            {TILES.map((tile, idx) => (
              <Tile key={idx} {...tile} />
            ))}
          </div>
        </div>
      </MainLayout>
    </>
  );
};
export default Templates;
