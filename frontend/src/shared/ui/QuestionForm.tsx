import { useState, type FormEvent } from 'react'
import { Button } from './Button'
import { FIELD } from './field'

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
      <form onSubmit={submit} className="flex flex-wrap gap-2">
        <input
          aria-label={placeholder}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          maxLength={2000}
          placeholder={placeholder}
          className={`${FIELD} min-w-0 flex-1 basis-64`}
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
            className="min-h-9 rounded-full border border-grey-300 px-3.5 py-1.5 text-[13px] font-medium text-ink transition-colors duration-150 hover:border-ink hover:bg-grey-50 disabled:opacity-50"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}
