import Image from 'next/image'
import { FC } from 'react'

const LoadingPage: FC = () => (
  <div className="flex items-center justify-center min-h-screen relative">
    <Image
      src="https://hi-george.s3.amazonaws.com/DataheraldAI/Dark+Background.png"
      alt="Background"
      fill
      style={{ objectFit: 'cover', objectPosition: 'center' }}
      quality={100}
    />
    <div className="absolute bg-white shadow-lg w-full max-w-none h-screen rounded-none sm:rounded-2xl sm:h-fit p-8 sm:max-w-lg">
      <div className="flex flex-col items-center gap-5">
        <Image
          className="my-2"
          src="/images/dh_ai_logo.svg"
          alt="Background"
          width={250}
          height={50}
        />
        <h1 className="text-xl text-secondary">Loading...</h1>
      </div>
    </div>
  </div>
)

export default LoadingPage
