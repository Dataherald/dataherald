import { useMonaco } from '@monaco-editor/react'
import dynamic from 'next/dynamic'
import { FC, useEffect } from 'react'
import { format } from 'sql-formatter'
const Editor = dynamic(() => import('@monaco-editor/react'), {
  ssr: false,
})

export interface SqlEditorProps {
  query: string
  className?: string
  disabled?: boolean
  onValueChange?: (value: string) => void
}

const SqlEditor: FC<SqlEditorProps> = ({
  query,
  className,
  onValueChange,
  disabled = false,
}) => {
  const monaco = useMonaco()

  useEffect(() => {
    if (!monaco) return
    monaco.languages.registerDocumentFormattingEditProvider('sql', {
      provideDocumentFormattingEdits(model, options) {
        const formatted = format(model.getValue(), {
          language: 'sql',
          tabWidth: options.tabSize,
        })
        return [
          {
            range: model.getFullModelRange(),
            text: formatted,
          },
        ]
      },
    })

    monaco.languages.registerDocumentRangeFormattingEditProvider('sql', {
      provideDocumentRangeFormattingEdits(model, range, options) {
        const formatted = format(model.getValue(), {
          language: 'sql',
          tabWidth: options.tabSize,
        })
        return [
          {
            range: range,
            text: formatted,
          },
        ]
      },
    })
  }, [monaco])

  return (
    <Editor
      className={className}
      defaultLanguage="sql"
      value={query}
      language="sql"
      options={{
        readOnly: disabled,
        lineHeight: 1.5,
        scrollBeyondLastLine: false,
        lineNumbersMinChars: 0,
        renderLineHighlight: disabled ? 'none' : 'gutter',
        scrollbar: {
          useShadows: true,
          arrowSize: 0,
          verticalSliderSize: 8,
          horizontalSliderSize: 8,
        },
        fontSize: 14,
        minimap: { enabled: false },
      }}
      // onChange={handleEditorChange}
      {...(onValueChange && {
        onChange: (value) => onValueChange(value || ''),
      })}
    />
  )
}

export default SqlEditor
