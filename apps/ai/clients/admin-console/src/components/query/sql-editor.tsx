import { useMonaco } from '@monaco-editor/react'
import dynamic from 'next/dynamic'
import { FC, useEffect } from 'react'
import { format } from 'sql-formatter'
const Editor = dynamic(() => import('@monaco-editor/react'), {
  ssr: false,
})

export interface SqlEditorProps {
  initialQuery: string
  onValueChange: (value: string) => void
}

const SqlEditor: FC<SqlEditorProps> = ({ initialQuery, onValueChange }) => {
  const handleEditorChange = (value: string | undefined): void => {
    onValueChange(value || '')
  }

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
      defaultLanguage="sql"
      defaultValue={initialQuery}
      language="sql"
      options={{
        lineHeight: 1.5,
        scrollBeyondLastLine: false,
        lineNumbersMinChars: 0,
        renderLineHighlight: 'gutter',
        scrollbar: {
          useShadows: true,
          arrowSize: 0,
          verticalSliderSize: 8,
          horizontalSliderSize: 8,
        },
        fontSize: 14,
        minimap: { enabled: false },
      }}
      onChange={handleEditorChange}
    />
  )
}

export default SqlEditor
