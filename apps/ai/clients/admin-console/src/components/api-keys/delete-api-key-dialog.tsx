import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { ToastAction } from '@/components/ui/toast'
import { toast } from '@/components/ui/use-toast'
import { Loader, Trash2 } from 'lucide-react'
import { FC, useState } from 'react'

interface DeleteApiKeyDialogProps {
  deleteFnc: () => void | Promise<void>
}

const DeleteApiKeyDialog: FC<DeleteApiKeyDialogProps> = ({ deleteFnc }) => {
  const [open, setOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const handleDeleteConfirm = async () => {
    setDeleting(true)
    try {
      await deleteFnc()
      toast({
        variant: 'success',
        title: 'API Key revoked',
      })
      setOpen(false)
    } catch (e) {
      console.error(e)
      toast({
        variant: 'destructive',
        title: 'Oops! Something went wrong.',
        description: 'There was a problem with revoking your API Key.',
        action: (
          <ToastAction altText="Try again" onClick={handleDeleteConfirm}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setDeleting(false)
    }
  }
  return (
    <AlertDialog open={open}>
      <Button
        variant="ghost"
        className="rounded-xl hover:bg-gray-200 hover:text-black/90"
        onClick={() => setOpen(true)}
      >
        <Trash2 strokeWidth={1.5} size={18} />
      </Button>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Revoke secret key</AlertDialogTitle>
          <AlertDialogDescription>
            This API key will immediately be disabled. API requests made using
            this key will be rejected, which could cause any systems still
            depending on it to break.
          </AlertDialogDescription>
          <AlertDialogDescription>
            Do you wish to continue?
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={handleDeleteConfirm}>
            {deleting ? (
              <>
                <Loader className="mr-2 animate-spin" size={18} />
                Revoking
              </>
            ) : (
              'Revoke key'
            )}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

export default DeleteApiKeyDialog
