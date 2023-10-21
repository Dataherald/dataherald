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
import { User } from '@/models/api'
import { LogOut, Settings, X } from 'lucide-react'
import { FC } from 'react'

export interface UserSettingsPopoverProps {
  user: User
}

const UserSettingsPopover: FC<UserSettingsPopoverProps> = ({ user }) => {
  const { name, email, picture } = user
  const { logout } = useAppContext()

  const handleLogout = () => {
    logout()
  }

  return (
    <Popover>
      <PopoverTrigger className="rounded-xl p-2 hover:bg-gray-100 hover:text-black/90">
        <Settings strokeWidth={1.5} />
      </PopoverTrigger>
      <PopoverContent align="end" className="flex flex-col gap-3 ml-3 mb-3">
        <div className="grid grid-cols-[auto,1fr,auto] items-center gap-3">
          <div className="w-7"></div>{' '}
          {/* This is a placeholder for the left side, you can remove if it's not needed */}
          <span className="text-xs text-center">{email}</span>
          <PopoverClose className="rounded-xl p-1 hover:bg-gray-100 hover:text-black/90">
            <X strokeWidth={1.5} size={20} />
          </PopoverClose>
        </div>
        <div className="flex flex-col items-center justify-center gap-3 p-6">
          <h1>Hi, {name}!</h1>
          <UserPicture pictureUrl={picture} size={75} />
        </div>
        <Separator />
        <div className="px-6 py-4 flex items-center justify-center">
          <Button
            variant="outline"
            size="sm"
            className="font-normal"
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
