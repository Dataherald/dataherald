import CustomMessageDialog from '@/components/query/custom-message-dialog'
import LoadingBox from '@/components/query/loading-box'
import {
  SectionHeader,
  SectionHeaderTitle,
} from '@/components/query/section-header'
import SendMessageDialog from '@/components/query/send-message-dialog'
import {
  MAIN_ACTION_BTN_CLASSES,
  SECONDARY_ACTION_BTN_CLASSES,
} from '@/components/query/workspace'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
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
import useQueryGenerateMessage from '@/hooks/api/query/useQueryGenerateMessage'
import { cn } from '@/lib/utils'
import { ErrorResponse, Query } from '@/models/api'
import { formatDistance } from 'date-fns'
import { Bot, Edit, Info, Loader } from 'lucide-react'
import Image from 'next/image'
import { FC, useState } from 'react'

interface MessageSectionProps {
  promptId: string
  initialMessage: string
  slack_message_last_sent_at?: string | null
  onPutQuery: (data: { message: string }) => Promise<Query | undefined>
  onMessageSent: () => Promise<void>
}

const MessageSection: FC<MessageSectionProps> = ({
  promptId,
  initialMessage,
  slack_message_last_sent_at = null,
  onPutQuery,
  onMessageSent,
}) => {
  const generateMessage = useQueryGenerateMessage()

  const [currentMessage, setCurrentMessage] = useState<string>(initialMessage)

  const [openEditMessageDialog, setOpenEditMessageDialog] = useState(false)
  const [editingMessage, setEditingMessage] = useState(false)
  const [generatingMessage, setGeneratingMessage] = useState(false)

  const disabledActions = editingMessage || generatingMessage

  const handleGenerateMessage = async () => {
    setGeneratingMessage(true)
    try {
      const { text } = await generateMessage(promptId)
      toast({
        variant: 'success',
        title: 'Message generated',
        description: 'The query message was generated using the AI platform.',
      })
      setCurrentMessage(text)
    } catch (error) {
      console.error(error)
    } finally {
      setGeneratingMessage(false)
    }
  }

  const handleCloseEditDialog = async (newCustomMessage?: string) => {
    setOpenEditMessageDialog(false)
    if (!newCustomMessage) return
    setEditingMessage(true)
    try {
      await onPutQuery({
        message: newCustomMessage,
      })
      setCurrentMessage(newCustomMessage)
      toast({
        variant: 'success',
        title: 'Message updated',
        description: 'The query message was updated successfully.',
      })
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
            onClick={() => handleCloseEditDialog(newCustomMessage)}
          >
            Try again
          </ToastAction>
        ),
      })
    } finally {
      setEditingMessage(false)
    }
  }

  return (
    <>
      <SectionHeader>
        <SectionHeaderTitle>
          <Image
            src="/images/slack-black.png"
            width={18}
            height={18}
            alt="Slack icon"
          />{' '}
          Slack message
        </SectionHeaderTitle>
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              type="button"
              disabled={disabledActions}
              className={cn(
                MAIN_ACTION_BTN_CLASSES,
                SECONDARY_ACTION_BTN_CLASSES,
              )}
              onClick={() => setOpenEditMessageDialog(true)}
            >
              <Edit size={14} strokeWidth={2}></Edit>
              Edit
            </Button>
            <CustomMessageDialog
              title={
                <div className="flex items-center gap-2">
                  <Image
                    src="/images/slack-color.png"
                    width={24}
                    height={24}
                    alt="Slack icon"
                  />{' '}
                  Slack message
                </div>
              }
              description="Compose the question's response message that will be sent to the Slack thread"
              isOpen={openEditMessageDialog}
              initialValue={currentMessage}
              onClose={handleCloseEditDialog}
            ></CustomMessageDialog>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  variant="ghost"
                  type="button"
                  disabled={disabledActions}
                  className={cn(
                    MAIN_ACTION_BTN_CLASSES,
                    SECONDARY_ACTION_BTN_CLASSES,
                  )}
                >
                  {generatingMessage ? (
                    <>
                      <Loader
                        className="mr-2 animate-spin"
                        size={16}
                        strokeWidth={2.5}
                      />{' '}
                      Generating
                    </>
                  ) : (
                    <>
                      <Bot size={16} strokeWidth={2} />
                      Generate
                    </>
                  )}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>
                    Generate natural language message
                  </AlertDialogTitle>
                </AlertDialogHeader>
                <AlertDialogDescription>
                  The AI will generate a response based on the last SQL query
                  run and results table. Make sure to run the correct SQL before
                  generating.
                </AlertDialogDescription>
                <AlertDialogDescription>
                  Do you wish to continue?
                </AlertDialogDescription>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleGenerateMessage}>
                    <Bot className="mr-2" size={16} strokeWidth={2.5} />
                    Generate
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <SendMessageDialog
              {...{
                promptId,
                disabled: disabledActions || !currentMessage,
                onMessageSent,
              }}
            />
          </div>
        </div>
      </SectionHeader>
      <div className="h-fit p-6 whitespace-pre-wrap text-sm">
        {editingMessage || generatingMessage ? (
          <LoadingBox className="h-24" />
        ) : (
          (
            <>
              {currentMessage}
              <div
                id="last_message_sent"
                className="pt-3 flex flex-row-reverse items-center gap-1 text-sm"
              >
                {slack_message_last_sent_at === null ? (
                  <span className="text-slate-500">No message sent yet</span>
                ) : (
                  <span className="text-green-600">
                    Last message sent{' '}
                    {formatDistance(
                      new Date(slack_message_last_sent_at),
                      new Date(),
                      {
                        addSuffix: true,
                      },
                    )}
                  </span>
                )}
              </div>
            </>
          ) || (
            <>
              <Alert variant="info">
                <AlertTitle className="flex items-center gap-2 font-bold">
                  <Info size={16} strokeWidth={2.5} />
                  No message yet
                </AlertTitle>
                <AlertDescription>
                  There is no message yet. You can edit the message or generate
                  a message using the AI platform.
                </AlertDescription>
              </Alert>
            </>
          )
        )}
      </div>
    </>
  )
}

export default MessageSection
