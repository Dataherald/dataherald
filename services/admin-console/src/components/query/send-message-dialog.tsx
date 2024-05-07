import { MAIN_ACTION_BTN_CLASSES } from '@/components/query/workspace'
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
import useQuerySendMessage from '@/hooks/api/query/useQuerySendMessage'
import { cn } from '@/lib/utils'
import { ErrorResponse } from '@/models/api'
import { Loader, Send } from 'lucide-react'
import { FC, useState } from 'react'

interface SendMessageDialogProps {
  promptId: string
  disabled: boolean
  onMessageSent: () => Promise<void>
}

const SendMessageDialog: FC<SendMessageDialogProps> = ({
  promptId,
  disabled = false,
  onMessageSent,
}) => {
  const sendMessage = useQuerySendMessage()
  const [sendingMessage, setSendingMessage] = useState(false)
  const handleSendMessage = async () => {
    try {
      setSendingMessage(true)
      await sendMessage(promptId)
      toast({
        variant: 'success',
        title: 'Message sent',
        description: 'The query message was sent to the Slack thread.',
      })
      await onMessageSent()
    } catch (e) {
      console.error(e)
      const { message: title, trace_id: description } = e as ErrorResponse
      toast({
        variant: 'destructive',
        title,
        description,
        action: (
          <ToastAction altText="Try again" onClick={handleSendMessage}>
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setSendingMessage(false)
    }
  }
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button
          disabled={disabled || sendingMessage}
          className={cn(
            MAIN_ACTION_BTN_CLASSES,
            'bg-green-600 hover:bg-green-500',
          )}
        >
          {sendingMessage ? (
            <>
              <Loader
                className="mr-2 animate-spin"
                size={14}
                strokeWidth={2.5}
              />{' '}
              Sending
            </>
          ) : (
            <>
              <Send className="mr-2" size={14} strokeWidth={2.5} />
              Send
            </>
          )}
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Send Slack message?</AlertDialogTitle>
        </AlertDialogHeader>
        <AlertDialogDescription>
          This will send the current message to the original question’s slack
          thread and cannot be undone.
        </AlertDialogDescription>
        <AlertDialogDescription>
          Do you wish to continue?
        </AlertDialogDescription>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            className="bg-green-600 hover:bg-green-500"
            onClick={handleSendMessage}
          >
            <Send className="mr-2" size={16} strokeWidth={2.5} />
            Send
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

export default SendMessageDialog
