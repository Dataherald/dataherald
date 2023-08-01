import dynamic from 'next/dynamic'
import { FC } from 'react'

const Editor = dynamic(() => import('@monaco-editor/react'), {
  ssr: false,
})

export interface SqlEditorProps {
  initialQuery: string
  onValueChange: (value: string) => void
}

const SqlEditor: FC<SqlEditorProps> = ({ initialQuery, onValueChange }) => {
  function handleEditorChange(value: string | undefined) {
    onValueChange(value || '')
  }

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
