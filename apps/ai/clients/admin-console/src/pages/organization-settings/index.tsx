import PageLayout from '@/components/layout/page-layout'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import AddUserDialog from '@/components/user/add-user-dialog'
import { useAppContext } from '@/contexts/app-context'
import useUsers from '@/hooks/api/user/useUsers'
import { ERole } from '@/models/api'
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client'
import { ArrowLeftRight, Building2, UserPlus2, Users2 } from 'lucide-react'
import Link from 'next/link'
import { FC, useState } from 'react'

const OrganizationSettingsPage: FC = () => {
  const [openAddUserDialog, setOpenAddUserDialog] = useState(false)

  const { user, organization } = useAppContext()
  const { isLoading, users, mutate } = useUsers()

  if (!organization) return null

  const isAdmin = user?.role === ERole.ADMIN

  const handleUserAdded = () => {
    mutate()
    setOpenAddUserDialog(false)
  }

  return (
    <>
      <PageLayout>
        <div className="flex flex-col gap-5">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <Building2 size={18} />
              <h1 className="text-lg font-semibold">{organization.name}</h1>
            </div>
            {isAdmin && (
              <Link href="/select-organization">
                <Button variant="ghost" size="sm">
                  <ArrowLeftRight className="mr-2" size={14} />
                  Change Organization
                </Button>
              </Link>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4 min-h-[30vh] max-h-[30vh]">
            <ContentBox className="grow">
              <div className="flex items-center gap-2">
                <Users2 size={20} />
                <h1 className="font-semibold">Users</h1>
              </div>
              <div className="grow">
                {isLoading
                  ? 'Loading...'
                  : users && (
                      <ul className="overflow-auto">
                        {users.map(({ id, name, email }) => (
                          <li key={id} className="p-1">
                            {name ? (
                              <div className="flex items-center gap-2">
                                <span>{name}</span>
                                <span className="text-xs text-slate-500">
                                  {email}
                                </span>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2">
                                <span className="text-slate-500">{email}</span>
                                <span className="text-xs text-orange-500">
                                  Pending sign up
                                </span>
                              </div>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
              </div>
              <Button
                className="self-end"
                onClick={() => setOpenAddUserDialog(true)}
              >
                <UserPlus2 className="mr-2" />
                Add User
              </Button>
            </ContentBox>
          </div>
        </div>
      </PageLayout>
      <AddUserDialog
        open={openAddUserDialog}
        onCancel={() => setOpenAddUserDialog(false)}
        onAddUser={handleUserAdded}
      />
    </>
  )
}

export default withPageAuthRequired(OrganizationSettingsPage)
