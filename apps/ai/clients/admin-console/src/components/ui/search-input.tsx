import { Button } from '@/components/ui/button'
import { Eraser, Search } from 'lucide-react'
import { FC, InputHTMLAttributes } from 'react'

type SearchInputProps = InputHTMLAttributes<HTMLInputElement> & {
  value: string
  onClear?: () => void
}

const SearchInput: FC<SearchInputProps> = ({
  className,
  value = '',
  onClear,
  ...props
}) => {
  const handleClear = () => {
    onClear?.()
  }

  return (
    <div
      className={`relative flex items-center w-full rounded-lg border border-input bg-background text-sm ${className}`}
    >
      <Search className="absolute left-3 p-0 text-slate-400" size={14} />
      <input
        type="text"
        value={value}
        className="flex-1 w-full rounded-lg px-10 py-1 ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-50"
        {...props}
      />
      {value && (
        <Button
          variant="icon"
          className="absolute right-3 h-fit p-0"
          onClick={handleClear}
        >
          <Eraser size={14} />
        </Button>
      )}
    </div>
  )
}

export default SearchInput
