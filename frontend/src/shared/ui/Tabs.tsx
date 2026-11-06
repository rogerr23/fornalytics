export interface TabItem<T extends string> {
  value: T
  label: string
  disabled?: boolean
  hint?: string
}

interface TabsProps<T extends string> {
  items: TabItem<T>[]
  value: T
  onChange: (value: T) => void
}

export function Tabs<T extends string>({ items, value, onChange }: TabsProps<T>) {
  return (
    <div role="tablist" className="flex flex-wrap gap-1 border-b border-gray-200">
      {items.map((item) => {
        const active = item.value === value
        return (
          <button
            key={item.value}
            type="button"
            role="tab"
            aria-selected={active}
            disabled={item.disabled}
            title={item.hint}
            onClick={() => onChange(item.value)}
            className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
              active
                ? 'border-indigo-600 text-indigo-700'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            } disabled:cursor-not-allowed disabled:text-gray-300`}
          >
            {item.label}
          </button>
        )
      })}
    </div>
  )
}
