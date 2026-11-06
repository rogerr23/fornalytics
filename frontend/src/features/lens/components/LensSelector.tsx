import { LENSES } from '../../../shared/api/lens'
import { useLens } from '../hooks/useLens'

export function LensSelector() {
  const { lens, setLens } = useLens()

  return (
    <div role="radiogroup" aria-label="Lente" className="inline-flex rounded-lg bg-gray-100 p-1">
      {LENSES.map((item) => {
        const active = item.value === lens
        return (
          <button
            key={item.value}
            type="button"
            role="radio"
            aria-checked={active}
            title={item.hint}
            onClick={() => setLens(item.value)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              active ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {item.label}
          </button>
        )
      })}
    </div>
  )
}
