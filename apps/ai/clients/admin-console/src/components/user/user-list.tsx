import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { ToastAction } from '@/components/ui/toast'
import { toast } from '@/components/ui/use-toast'
import InviteMemberDialog from '@/components/user/invite-member-dialog'
import LoadingUserList from '@/components/user/loading-user-list'
import { useAppContext } from '@/contexts/app-context'
import { useDeleteUser } from '@/hooks/api/user/useDeleteUser'
import useUsers from '@/hooks/api/user/useUsers'
import { User } from '@/models/api'
import { Trash2, UserPlus2, UsersRound } from 'lucide-react'
import { useState } from 'react'

const UserList = () => {
  const [openInviteMemberDialog, setOpenInviteMemberDialog] = useState(false)
  const { user: currentUser } = useAppContext()
  const { isLoading, users, mutate } = useUsers()
  const deleteUser = useDeleteUser()

  const handleMemberInvited = () => {
    mutate()
    setOpenInviteMemberDialog(false)
  }

  const handleDeleteUser = async (user: User) => {
    try {
      await deleteUser(user.id)
      toast({
        variant: 'success',
        title: 'Team member Removed',
        description: `The user ${
          user.name || user.email
        } was removed from the Organization.`,
      })
      mutate()
    } catch (error) {
      console.error(error)
      toast({
        variant: 'destructive',
        title: 'Oops! Something went wrong.',
        description:
          'There was a problem removing the user from the Organization.',
        action: (
          <ToastAction
            altText="Try again"
            onClick={() => handleDeleteUser(user)}
          >
            Try again
          </ToastAction>
        ),
      })
    }
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <UsersRound size={20} strokeWidth={2.5} />
        <h1 className="font-semibold">Team</h1>
      </div>
      <div className="grow overflow-auto">
        {isLoading ? (
          <LoadingUserList />
        ) : (
          users && (
            <ul>
              {users.map((user: User) => {
                const { id, name, email } = user
                return (
                  <li key={id} className="p-1">
                    <div className="flex items-center justify-between gap-2">
                      {name ? (
                        <div
                          className="flex gap-2"
                          style={{ alignItems: 'baseline' }}
                        >
                          <span>{name}</span>
                          <span className="text-xs text-slate-500">
                            {email}
                          </span>
                        </div>
                      ) : (
                        <div
                          className="flex gap-2"
                          style={{ alignItems: 'baseline' }}
                        >
                          <span className="text-slate-500">{email}</span>
                          <span className="text-xs text-orange-500">
                            Pending sign up
                          </span>
                        </div>
                      )}
                      {user.id !== currentUser?.id && (
                        <AlertDialog>
                          <AlertDialogTrigger className="rounded-lg p-2 hover:bg-gray-200 hover:text-black/90">
                            <Trash2 size={18} strokeWidth={1.5} />
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>
                                {`Remove "${user.name || user.email}" from the
                                Organization?`}
                              </AlertDialogTitle>
                              <AlertDialogDescription>
                                Do you wish to continue?
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                variant="destructive"
                                onClick={() => handleDeleteUser(user)}
                              >
                                Remove Member
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      )}
                    </div>
                  </li>
                )
              })}
            </ul>
          )
        )}
      </div>
      <div className="self-end">
        <Button onClick={() => setOpenInviteMemberDialog(true)}>
          <UserPlus2 className="mr-2" size={18} />
          Invite
        </Button>
        <InviteMemberDialog
          open={openInviteMemberDialog}
          onCancel={() => setOpenInviteMemberDialog(false)}
          onInviteMember={handleMemberInvited}
        />
      </div>
    </>
  )
}

export default UserList
