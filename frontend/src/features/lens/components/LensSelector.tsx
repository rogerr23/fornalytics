import { LENSES } from '../../../shared/api/lens'
import { useLens } from '../hooks/useLens'

/** Segmented control, always visible: who the explanation is for. */
export function LensSelector({ inverse = false }: { inverse?: boolean }) {
  const { lens, setLens } = useLens()
  const edge = inverse ? 'border-white' : 'border-ink'

  return (
    <div className="flex flex-col gap-2 sm:items-start">
      <span id="lens-label" className={`eyebrow ${inverse ? 'text-grey-300' : 'text-grey-500'}`}>
        Explicar para
      </span>
      <div
        role="radiogroup"
        aria-labelledby="lens-label"
        className={`inline-flex w-full overflow-hidden rounded border sm:w-auto ${edge}`}
      >
        {LENSES.map((item) => {
          const active = item.value === lens
          const look = inverse
            ? active
              ? 'bg-white text-ink'
              : 'text-white hover:bg-ink-700'
            : active
              ? 'bg-ink text-white'
              : 'bg-white text-ink hover:bg-grey-100'
          return (
            <button
              key={item.value}
              type="button"
              role="radio"
              aria-checked={active}
              title={item.hint}
              onClick={() => setLens(item.value)}
              className={`min-h-11 flex-1 px-4 text-sm font-semibold whitespace-nowrap transition-colors duration-150 sm:flex-none sm:px-5 ${look}`}
            >
              {item.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
