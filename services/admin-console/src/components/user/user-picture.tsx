import { UserCircle2 } from 'lucide-react'
import Image from 'next/image'
import { FC } from 'react'

export interface UserPictureProps {
  pictureUrl?: string | null
  size?: number
}

const UserPicture: FC<UserPictureProps> = ({
  pictureUrl,
  size = 35,
}: UserPictureProps) =>
  pictureUrl ? (
    <Image
      className="rounded-full"
      src={pictureUrl}
      alt="User Profile Picture"
      width={size}
      height={size}
    />
  ) : (
    <UserCircle2 size={size} strokeWidth={1.5} className="text-slate-500" />
  )

export default UserPicture
