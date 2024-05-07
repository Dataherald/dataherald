import DatabaseConnectionFormDialog from '@/components/databases/database-connection-form-dialog'
import SampleDatabaseConnectionDialog from '@/components/databases/sample-database-connection-dialog'
import { Button } from '@/components/ui/button'
import { ContentBox } from '@/components/ui/content-box'
import { Separator } from '@/components/ui/separator'
import DATABASE_PROVIDERS from '@/constants/database-providers'
import { Plug } from 'lucide-react'
import Image from 'next/image'
import { FC } from 'react'

const DB_LOGO_SIZE = 28

const FirstDatabaseConnection: FC<{
  onConnected: () => void
  onFinish: () => void
}> = ({ onConnected, onFinish }) => (
  <ContentBox className="px-8 py-12 m-6 flex flex-col items-center justify-between gap-8">
    <h1 className="text-xl font-semibold mb-5">
      Connect a Database to get started
    </h1>
    <div className="flex flex-col items-center justify-center gap-8">
      <div className="max-w-[250px]">
        <SampleDatabaseConnectionDialog
          onConnected={onConnected}
          onFinish={onFinish}
        />
      </div>
      <p className="text-xs font-semibold text-slate-500">
        Use a sample database to explore the platform features. You can connect
        your own database later.
      </p>
    </div>
    <div className="w-full max-w-2xl flex items-center justify-evenly gap-2">
      <Separator className="bg-slate-400 h-[0.5px]" rounded />
      <div className="w-fit text-xs text-slate-500 font-semibold">OR</div>
      <Separator className="bg-slate-400 h-[0.5px]" rounded />
    </div>
    <div className="flex flex-col items-center justify-center gap-8">
      <div className="max-w-[250px]">
        <DatabaseConnectionFormDialog
          isFirstConnection
          onConnected={onConnected}
          onFinish={onFinish}
          renderTrigger={() => (
            <Button className={'px-4 py-1.5 h-fit w-full'}>
              <Plug className="mr-2" size={20} strokeWidth={1.5} />
              Connect your Database
            </Button>
          )}
        />
      </div>
      <p className="text-xs font-semibold text-slate-500">
        Supported database providers
      </p>
      <div className="flex flex-wrap max-w-lg items-center justify-center gap-6">
        {DATABASE_PROVIDERS.map(({ logoUrl, name }, idx) => (
          <div key={idx} className="w-18 mx-2 flex flex-col items-center gap-3">
            <Image
              className="grow"
              priority
              src={logoUrl}
              alt={`${name} Logo`}
              width={DB_LOGO_SIZE}
              height={DB_LOGO_SIZE}
            />
            <span className="tracking-wide text-slate-800 text-2xs text-center">
              {name}
            </span>
          </div>
        ))}
      </div>
    </div>
  </ContentBox>
)

export default FirstDatabaseConnection
