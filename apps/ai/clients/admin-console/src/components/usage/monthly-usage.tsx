import PageErrorMessage from '@/components/error/page-error-message'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import CreditsChart from '@/components/usage/credits-chart'
import EditSpendingLimitDialog from '@/components/usage/edit-spending-limit-dialog'
import UsageChart from '@/components/usage/usage-chart'
import useSpendingLimits from '@/hooks/api/billing/useSpendingLimits'
import useUsage from '@/hooks/api/billing/useUsage'
import { cn, toDateCycle, toDollars } from '@/lib/utils'
import { BarChart2, RefreshCcw } from 'lucide-react'
import { FC, HTMLAttributes } from 'react'

const MonthlyUsage: FC<HTMLAttributes<HTMLDivElement>> = ({ className }) => {
  const {
    isLoading,
    isValidating,
    error,
    usage,
    mutate: mutateUsage,
  } = useUsage()
  const { limits, mutate: mutateLimits } = useSpendingLimits()

  const handleUpdateSpendingLimit = () => {
    mutateLimits()
    mutateUsage()
  }

  let pageContent = <></>
  let billingCycle = ''

  if (isLoading) {
    pageContent = (
      <div className="h-full flex flex-col gap-5">
        <Skeleton className="h-4/5" />
        <Skeleton className="h-1/5" />
      </div>
    )
  } else if (error) {
    pageContent = (
      <PageErrorMessage
        message="Something went wrong while retrieving your monthly usage."
        error={error}
      />
    )
  } else if (usage) {
    if (usage.current_period_start && usage.current_period_end) {
      billingCycle = toDateCycle(
        usage.current_period_start,
        usage.current_period_end,
      )
    }
    const {
      available_credits,
      total_credits,
      finetuning_gpt_35_cost,
      finetuning_gpt_4_cost,
      sql_generation_cost,
    } = usage
    const total_usage =
      finetuning_gpt_35_cost + finetuning_gpt_4_cost + sql_generation_cost
    const used_credits = total_credits - available_credits
    pageContent = (
      <div className="flex flex-col gap-5">
        <div className="flex items-center gap-3">
          <div className="grow max-w-[60%]">
            <UsageChart usage={usage} />
          </div>
          <div className="flex flex-col gap-3 pb-12">
            <div className="text-3xl font-bold">{`$${toDollars(
              total_usage,
            )}`}</div>
            {limits ? (
              <>
                <div className="text-slate-500">
                  {`/ $${toDollars(limits.spending_limit)} limit`}
                </div>
                <EditSpendingLimitDialog
                  spendingLimits={limits}
                  onUpdated={handleUpdateSpendingLimit}
                />
              </>
            ) : (
              <Skeleton className="w-32 h-8" />
            )}
          </div>
        </div>
        <div className="flex flex-col gap-3">
          <div className="flex gap-2 items-center">
            <h1 className="font-bold">Credit Usage</h1>
            <div className="text-slate-500 text-sm">USD</div>
          </div>

          <div className="w-100 flex gap-3 items-end">
            <div className="h-16 grow">
              <CreditsChart
                availableCredits={available_credits}
                totalCredits={total_credits}
              />
            </div>
            <TooltipProvider>
              <Tooltip delayDuration={0}>
                <TooltipTrigger asChild>
                  <div className="flex gap-2 pb-1">
                    ${toDollars(used_credits)} <span>/</span> $
                    {toDollars(total_credits)}
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <span className="text-slate-700">
                    {`You've`} used <strong>${toDollars(used_credits)}</strong>{' '}
                    out of the $ <strong>{toDollars(total_credits)}</strong>{' '}
                    total credit granted to you.
                  </span>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </div>
    )
  }
  return (
    <>
      <div className={cn('w-full flex justify-between gap-2', className)}>
        <div className="flex items-center gap-2">
          <BarChart2 size={20} strokeWidth={2.5} />
          <h1 className="font-semibold">Monthly Usage</h1>
          <div className="text-slate-500 text-sm">{billingCycle}</div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          disabled={isLoading || isValidating}
          onClick={() => mutateUsage()}
        >
          <RefreshCcw
            size={16}
            className={isLoading || isValidating ? 'animate-spin' : ''}
          />
        </Button>
      </div>
      <div className="grow">{pageContent}</div>
    </>
  )
}

export default MonthlyUsage
