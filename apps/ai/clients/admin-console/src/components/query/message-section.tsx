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
import { Bot, Edit, Loader } from 'lucide-react'
import Image from 'next/image'
import { FC, useState } from 'react'

interface MessageSectionProps {
  queryId: string
  initialMessage: string
  onPatchQuery: (data: { message: string }) => Promise<void>
}

const MessageSection: FC<MessageSectionProps> = ({
  queryId,
  initialMessage,
  onPatchQuery,
}) => {
  const generateMessage = useQueryGenerateMessage()

  const [currentMessage, setCurrentMessage] = useState<string>(initialMessage)

  const [openEditMessageDialog, setOpenEditMessageDialog] = useState(false)
  const [editingMessage, setEditingMessage] = useState(false)
  const [generatingMessage, setGeneratingMessage] = useState(false)
  const handleGenerateMessage = async () => {
    setGeneratingMessage(true)
    try {
      const { message } = await generateMessage(queryId)
      toast({
        title: 'Message generated',
        description: 'The query message was generated using the AI platform.',
      })
      setCurrentMessage(message)
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
      await onPatchQuery({
        message: newCustomMessage,
      })
      setCurrentMessage(newCustomMessage)
      toast({
        title: 'Message updated',
        description: 'The query message was updated successfully.',
      })
    } catch (error) {
      console.error(error)
      toast({
        variant: 'destructive',
        title: 'Ups! Something went wrong.',
        description: 'There was a problem with updating the message.',
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
            width={24}
            height={24}
            alt="Slack icon"
          />{' '}
          Slack message
        </SectionHeaderTitle>
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              type="button"
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
            <SendMessageDialog {...{ queryId }} />
          </div>
        </div>
      </SectionHeader>
      <div className="h-fit p-6 whitespace-pre-wrap">
        {editingMessage || generatingMessage ? (
          <LoadingBox className="h-24" />
        ) : (
          currentMessage
        )}
      </div>
    </>
  )
}

export default MessageSection
