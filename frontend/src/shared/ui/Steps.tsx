const STEPS = ['Nome', 'Material', 'Processamento', 'Explicações'] as const

/** Where the person is in the journey: name → material → processing → lenses. */
export function JourneySteps({ current }: { current: number }) {
  return (
    <ol aria-label="Etapas" className="flex flex-wrap gap-x-6 gap-y-2">
      {STEPS.map((label, index) => {
        const state = index < current ? 'done' : index === current ? 'current' : 'next'
        return (
          <li
            key={label}
            aria-current={state === 'current' ? 'step' : undefined}
            className={`flex items-center gap-2 text-[13px] ${
              state === 'next' ? 'text-grey-500' : 'text-ink'
            } ${state === 'current' ? 'font-bold' : 'font-medium'}`}
          >
            <span
              className={`inline-flex h-6 w-6 items-center justify-center rounded text-[11px] font-bold ${
                state === 'current'
                  ? 'bg-ink text-white'
                  : state === 'done'
                    ? 'border border-ink'
                    : 'border border-grey-300'
              }`}
            >
              {String(index + 1).padStart(2, '0')}
            </span>
            {label}
          </li>
        )
      })}
    </ol>
  )
}
