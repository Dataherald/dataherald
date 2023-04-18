import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { Lato } from "next/font/google";

const inter = Lato({ weight: "400", subsets: ["latin"] });

export default function App({ Component, pageProps }: AppProps<{}>) {
  return (
    <main className={inter.className}>
      <Component {...pageProps} />
    </main>
  );
}
