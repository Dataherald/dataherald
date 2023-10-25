import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverClose,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Separator } from '@/components/ui/separator'
import UserPicture from '@/components/user/user-picture'
import { useAppContext } from '@/contexts/app-context'
import { Organization, User } from '@/models/api'
import { LogOut, Settings, Settings2, User2, X } from 'lucide-react'
import Link from 'next/link'
import { FC } from 'react'

export interface UserSettingsPopoverProps {
  user: User
  organization: Organization
}

const UserSettingsPopover: FC<UserSettingsPopoverProps> = ({
  user,
  organization,
}) => {
  const { name: username, email, picture } = user
  const { name: orgName } = organization
  const { logout } = useAppContext()

  const handleLogout = logout

  return (
    <Popover>
      <PopoverTrigger className="rounded-xl p-2 hover:bg-gray-100 hover:text-black/90">
        <Settings strokeWidth={1.5} />
      </PopoverTrigger>
      <PopoverContent
        align="end"
        className="flex flex-col gap-3 ml-3 mb-3 w-[420px] p-3"
      >
        <div className="grid grid-cols-[auto,1fr,auto] items-start gap-3">
          <div className="w-7"></div>{' '}
          {/* This is a placeholder for the left side, you can remove if it's not needed */}
          <div className="flex flex-col items-center gap-2 mt-1.5">
            <span className="text-xs">{email}</span>
            <span className="text-sm">{orgName}</span>
          </div>
          <PopoverClose className="rounded-xl p-1 hover:bg-gray-100 hover:text-black/90">
            <X strokeWidth={1.5} size={20} />
          </PopoverClose>
        </div>
        <div className="flex flex-col items-center justify-center gap-3 p-2">
          <h1>Hi, {username}!</h1>
          <UserPicture pictureUrl={picture} size={75} />
        </div>
        <div className="grid grid-cols-2">
          <Link href="/my-account">
            <Button variant="ghost" size="sm" className="w-full">
              <User2 className="mr-2" size={18} /> My account
            </Button>
          </Link>
          <Link href="/organization-settings">
            <Button variant="ghost" size="sm" className="w-full">
              <Settings2 className="mr-2" size={18} />
              Organization settings
            </Button>
          </Link>
        </div>
        <Separator />
        <div className="w-full flex items-center justify-center">
          <Button
            variant="destructive-outline"
            size="sm"
            onClick={handleLogout}
          >
            <LogOut className="mr-2" size={18} />
            Sign out
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  )
}

export default UserSettingsPopover
