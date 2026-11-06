import { useState, type FormEvent } from 'react'
import { Button } from './Button'

interface QuestionFormProps {
  placeholder: string
  suggestions: string[]
  busy: boolean
  busyLabel: string
  onAsk: (question: string) => void
}

/** A one-line question with suggestion chips (side by side and "Isso faz?"). */
export function QuestionForm({
  placeholder,
  suggestions,
  busy,
  busyLabel,
  onAsk,
}: QuestionFormProps) {
  const [question, setQuestion] = useState('')

  function ask(text: string) {
    const trimmed = text.trim()
    if (!trimmed || busy) return
    onAsk(trimmed)
    setQuestion('')
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    ask(question)
  }

  return (
    <div className="flex flex-col gap-3">
      <form onSubmit={submit} className="flex gap-2">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          maxLength={2000}
          placeholder={placeholder}
          className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        />
        <Button type="submit" disabled={!question.trim() || busy}>
          {busy ? busyLabel : 'Perguntar'}
        </Button>
      </form>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            disabled={busy}
            onClick={() => ask(suggestion)}
            className="rounded-full border border-gray-200 px-3 py-1.5 text-sm text-gray-700 hover:border-indigo-300 hover:text-indigo-700 disabled:opacity-50"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}
