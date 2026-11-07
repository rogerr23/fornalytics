import type { IconName } from './Icon'
import { Icon } from './Icon'

export interface TabItem<T extends string> {
  value: T
  label: string
  disabled?: boolean
  hint?: string
  icon?: IconName
}

interface TabsProps<T extends string> {
  items: TabItem<T>[]
  value: T
  onChange: (value: T) => void
  label?: string
  /** Wrap onto a second line on narrow screens instead of scrolling sideways. */
  wrap?: boolean
}

/** Underlined tabs; the row scrolls sideways on a phone instead of wrapping into a block. */
export function Tabs<T extends string>({
  items,
  value,
  onChange,
  label,
  wrap = false,
}: TabsProps<T>) {
  return (
    <div
      role="tablist"
      aria-label={label}
      className={`flex min-w-0 border-b border-grey-200 sm:gap-x-8 ${
        wrap ? 'flex-wrap gap-x-6' : 'gap-6 overflow-x-auto [scrollbar-width:none]'
      }`}
    >
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
            className={`-mb-px inline-flex min-h-11 shrink-0 items-center gap-2 border-b-2 text-sm whitespace-nowrap transition-colors duration-150 ${
              active
                ? 'border-ink font-bold text-ink'
                : 'border-transparent font-medium text-grey-500 hover:text-ink'
            } disabled:cursor-not-allowed disabled:text-grey-300`}
          >
            {item.icon && <Icon name={item.icon} size={16} />}
            {item.label}
          </button>
        )
      })}
    </div>
  )
}
