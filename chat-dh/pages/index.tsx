import { useUser } from "@auth0/nextjs-auth0/client";
import { useRouter } from "next/router";
import { FC, useEffect } from "react";

const RootPage: FC = () => {
  const router = useRouter();
  const { user, isLoading } = useUser();
  useEffect(() => {
    if (!isLoading) {
      if (user) {
        router.push("/chat");
      } else {
        router.push("/api/auth/login");
      }
    }
  });
  return <></>;
};

export default RootPage;
