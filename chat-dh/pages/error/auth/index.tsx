import { AUTH0_CLIENT_ID, AUTH0_DOMAIN, HOSTNAME } from "@/env-variables";
import Image from "next/image";
import { useRouter } from "next/router";
import { useState } from "react";

function Auth0ErrorPage() {
  const router = useRouter();
  const { message: errorDescription } = router.query;
  const [showDetails, setShowDetails] = useState(false);

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  const logoutUser = async () => {
    window.location.href = `${AUTH0_DOMAIN}/v2/logout?client_id=${AUTH0_CLIENT_ID}&returnTo=${HOSTNAME}`;
  };

  return (
    <div className="flex items-center justify-center min-h-screen relative">
      <Image
        src="https://hi-george.s3.amazonaws.com/DataheraldAI/Dark+Background.png"
        alt="Background"
        fill
        style={{ objectFit: "cover", objectPosition: "center" }}
        quality={100}
      />
      <div className="absolute bg-white shadow-lg w-full max-w-none h-screen rounded-none sm:rounded-2xl sm:h-fit p-8 sm:max-w-sm">
        <h1 className="text-2xl font-bold mb-4 text-secondary-dark">
          Authentication Error
        </h1>
        <p className="mb-4 text-gray-800 break-words">
          An error occurred. Please try again or{" "}
          <a className="text-primary font-semibold" href="mailto:support@dataherald.com">
            contact us
          </a>{" "}
          if the issue persists.
        </p>
        {errorDescription && (
          <>
            <p
              className="text-primary font-semibold cursor-pointer mb-4"
              onClick={toggleDetails}
            >
              {showDetails ? "Hide details" : "Show details"}
            </p>
            {showDetails && (
              <p className="text-gray-400 mb-4">{errorDescription}</p>
            )}
          </>
        )}
        <button
          className="bg-secondary text-white font-semibold py-2 px-4 rounded-lg w-full"
          onClick={logoutUser}
        >
          Try again
        </button>
      </div>
    </div>
  );
}

export default Auth0ErrorPage;
