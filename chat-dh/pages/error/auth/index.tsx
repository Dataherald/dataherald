import { Icon } from "@/components/Layout/Icon";
import { AUTH0_CLIENT_ID, AUTH0_DOMAIN, HOSTNAME } from "@/env-variables";
import Image from "next/image";
import { useRouter } from "next/router";
import { FC, useState } from "react";

enum ERROR_CODES {
  EMAIL_NOT_VERIFIED = "Email Not Verified",
}

/**
 * Auth0 wraps several errors like unverified emails into a CallbackError
 * We implemented this to catch different callback scenarios and catch the errors for UX
 * @param errorDescription
 * @returns
 */
const getErrorCause = (errorDescription: string): string => {
  const error = (errorDescription.match(/---(.*?)\)/) || "")[1];
  console.log(error);
  switch (error) {
    case ERROR_CODES.EMAIL_NOT_VERIFIED:
      return "Email Not Verified";
    default:
      return "Authentication Error";
  }
};

const AuthErrorPage: FC = () => {
  const router = useRouter();
  const [showDetails, setShowDetails] = useState(false);
  const { message = "" } = router.query;
  const errorDescription = message as string;
  const isEmailNotVerified = errorDescription?.includes("Email Not Verified");
  const errorCause = getErrorCause(errorDescription);

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
        <h1 className="text-2xl font-bold mb-4 text-secondary-dark flex items-center gap-3">
          {isEmailNotVerified && <Icon value="email" />}
          {errorCause}
        </h1>
        <div className="mb-8">
          {isEmailNotVerified ? (
            <p className="text-gray-800 break-words">
              Your email address has not been verified. Please check your inbox
              and follow the instructions in the verification email. If you
              can&apos;t find the email,{" "}
              <a
                className="text-primary font-semibold"
                href="mailto:support@dataherald.com"
              >
                contact us
              </a>{" "}
              for assistance.
            </p>
          ) : (
            <div className="flex flex-col gap-2">
              <p className="text-gray-800 break-words">
                An error occurred. Please try again or{" "}
                <a
                  className="text-primary font-semibold"
                  href="mailto:support@dataherald.com"
                >
                  contact us
                </a>{" "}
                if the issue persists.
              </p>
              <p
                className="text-primary font-semibold cursor-pointer"
                onClick={toggleDetails}
              >
                {showDetails ? "Hide details" : "Show details"}
              </p>
              {showDetails && (
                <p className="text-gray-400">{errorDescription}</p>
              )}
            </div>
          )}
        </div>
        <button
          className="bg-secondary text-white font-semibold py-2 px-4 rounded-lg w-full"
          onClick={logoutUser}
        >
          Try again
        </button>
      </div>
    </div>
  );
};

export default AuthErrorPage;
