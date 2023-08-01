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
        fontSize: 14,
        minimap: { enabled: false },
      }}
      onChange={handleEditorChange}
    />
  )
}

export default SqlEditor
