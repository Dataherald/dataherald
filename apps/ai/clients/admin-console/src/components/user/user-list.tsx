import PageErrorMessage from '@/components/error/page-error-message'
import LoadingList from '@/components/layout/loading-list'
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
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ToastAction } from '@/components/ui/toast'
import { toast } from '@/components/ui/use-toast'
import InviteMemberDialog from '@/components/user/invite-member-dialog'
import UserPicture from '@/components/user/user-picture'
import { useAppContext } from '@/contexts/app-context'
import { useDeleteUser } from '@/hooks/api/user/useDeleteUser'
import useUsers from '@/hooks/api/user/useUsers'
import { ErrorResponse, User } from '@/models/api'
import { Trash2, UserPlus2 } from 'lucide-react'
import { useState } from 'react'

const UserList = () => {
  const [openInviteMemberDialog, setOpenInviteMemberDialog] = useState(false)
  const { user: currentUser } = useAppContext()
  const { isLoading, error, users, mutate } = useUsers()
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
    } catch (e) {
      console.error(e)
      const { message: title, trace_id: description } = e as ErrorResponse
      toast({
        variant: 'destructive',
        title,
        description,
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
      <div className="grow overflow-auto py-5">
        {isLoading ? (
          <LoadingList length={3} />
        ) : error ? (
          <PageErrorMessage
            error={error}
            message="Something went wrong while fetching the team members."
          />
        ) : (
          users && (
            <ul className="flex flex-col gap-3">
              {users
                .sort((a, b) =>
                  b.id === currentUser?.id
                    ? 1
                    : a.id === currentUser?.id
                    ? -1
                    : 0,
                )
                .map((user: User) => {
                  const { id, name, email } = user
                  return (
                    <li key={id}>
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <UserPicture pictureUrl={user.picture} size={30} />
                          {name ? (
                            <div
                              className="flex gap-2"
                              style={{ alignItems: 'baseline' }}
                            >
                              <span>{name}</span>
                              <span className="text-xs text-slate-500">
                                {email}
                              </span>
                              {user.id === currentUser?.id && (
                                <Badge
                                  className="px-2 py-0.5 text-xs"
                                  variant="success"
                                >
                                  You
                                </Badge>
                              )}
                            </div>
                          ) : (
                            <div
                              className="flex gap-2"
                              style={{ alignItems: 'baseline' }}
                            >
                              <span className="text-slate-500">{email}</span>
                              <span className="text-xs text-orange-400 font-semibold">
                                Pending sign up
                              </span>
                            </div>
                          )}
                        </div>
                        {user.id !== currentUser?.id && (
                          <AlertDialog>
                            <AlertDialogTrigger className="rounded-lg p-2 hover:bg-slate-200 hover:text-black/90">
                              <Trash2 size={16} strokeWidth={1.5} />
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
          <UserPlus2 className="mr-2" size={16} />
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
