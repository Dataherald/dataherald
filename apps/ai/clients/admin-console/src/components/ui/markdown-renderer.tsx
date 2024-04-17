import { FC, ReactNode } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { dracula } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import remarkGfm from 'remark-gfm'

interface MarkdownRendererProps {
  children: ReactNode
}

const MarkdownRenderer: FC<MarkdownRendererProps> = ({
  children: markdownText,
}) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    components={{
      code({ className, children, ...props }) {
        const match = /language-(\w+)/.exec(className || '')
        if (match) {
          return (
            <SyntaxHighlighter style={dracula} language={match[1]} PreTag="div">
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          )
        } else {
          // Render inline code or code blocks without specified language
          return (
            <code
              style={{
                backgroundColor: '#44475a',
                color: '#f8f8f2',
                padding: '4px',
                margin: '0 1px',
                borderRadius: '0.3em',
                tabSize: 4,
                fontSize: '90%',
                fontFamily:
                  'Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace',
                lineHeight: '2',
                textShadow: 'rgba(0, 0, 0, 0.3) 0px 1px',
              }}
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </code>
          )
        }
      },
    }}
  >
    {String(markdownText)}
  </ReactMarkdown>
)

export default MarkdownRenderer
