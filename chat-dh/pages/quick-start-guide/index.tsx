import Button from "@/components/Layout/Button";
import { Header } from "@/components/Layout/Header";
import { MainLayout } from "@/components/Layout/Main";
import { usePrompt } from "@/context/prompt";
import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { FC } from "react";

const QuickStartGuide: FC = () => {
  const { setPrompt } = usePrompt();
  const router = useRouter();
  const EXAMPLE_PROMPTS = [
    "Home prices in Los Angeles",
    "What was the most expensive ZIP in CA in January 2023?",
    "Total homes sold in Los Angeles in 2023 broken down by building type",
    "Rents in Berkeley 2021-2022",
    "How many homes were sold in Harris County in Jan 2023, broken down by building type?",
    "How does the price per square foot for condos in Seattle compare to Portland, Oregon?",
    "What are the most expensive zip codes in Dekalb County, GA?",
  ];

  const handlePromptClick = (prompt: string) => {
    setPrompt(prompt);
    router.push("/chat");
  };

  return (
    <>
      <Head>
        <title>Dataherald AI | Quick Start Guide</title>
        <meta
          name="description"
          content="A chatbot powered by OpenAPI that can generate text and visualizations with the latest data"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <MainLayout>
        <div className="flex-1 flex flex-col gap-2 py-6">
          <Header title="Dataherald AI - Quick Start Guide"></Header>
          <div className="flex flex-col gap-4 sm:gap-8">
            <section>
              <h2 className="mb-2 font-semibold">Welcome to Dataherald AI!</h2>
              <p>
                This is a technical preview of our AI platform that automates
                real-estate data content creation. The tool currently creates a
                one paragraph summary and a data visualization around real
                estate market trends.
              </p>
            </section>
            <section>
              <h2 className="mb-2 font-semibold">
                Here are some prompts to try
              </h2>
              <ul className="pl-2 list list-disc">
                {EXAMPLE_PROMPTS.map((prompt, idx) => (
                  <li className="ml-4" key={idx}>
                    <button
                      className="w-full bg-transparent border-none text-start text-blue-600 cursor-pointer hover:text-blue-800 focus:outline-none focus:ring-0 flex items-center justify-between gap-2"
                      onClick={() => handlePromptClick(prompt)}
                    >
                      <span>{prompt}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </section>
            <section>
              <h2 className="mb-2 font-semibold">Limitations</h2>
              <ul className="pl-2 list list-disc">
                {[
                  "Data timeframe: Only January 1 2020 onward is supported",
                  "Geographies: Only United States states, counties, cities, and zip codes. All other geographies, for example neighborhoods, are NOT supported.",
                ].map((listItem, idx) => (
                  <li className="ml-4" key={idx}>
                    {listItem}
                  </li>
                ))}
              </ul>
            </section>
            <section>
              <h2 className="mb-2 font-semibold">
                Is there any usage based charge or metering?
              </h2>
              <p>No. This technical preview is free to use.</p>
            </section>
            <section className="justify-self-end">
              <div className="flex items-center justify-center gap-5">
                <Button>
                  <Link href="/chat">Go to chat</Link>
                </Button>
                <Button color="secondary">
                  <Link
                    href="https://dataherald.com/contact-us"
                    target="_blank"
                    referrerPolicy="no-referrer"
                  >
                    Contact us
                  </Link>
                </Button>
              </div>
            </section>
          </div>
        </div>
      </MainLayout>
    </>
  );
};
export default QuickStartGuide;
