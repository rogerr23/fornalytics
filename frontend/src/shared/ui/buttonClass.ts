export type ButtonVariant =
  'primary' | 'secondary' | 'ghost' | 'ghostInverse' | 'danger' | 'inverse'
export type ButtonSize = 'sm' | 'md'

const VARIANTS: Record<ButtonVariant, string> = {
  primary: 'bg-ink text-white hover:bg-ink-700 disabled:bg-grey-300',
  secondary:
    'border border-ink bg-white text-ink hover:bg-grey-100 disabled:border-grey-300 disabled:text-grey-400',
  ghost: 'text-ink hover:bg-grey-100 disabled:text-grey-400',
  ghostInverse: 'text-white hover:bg-ink-700 disabled:text-grey-500',
  danger: 'text-danger hover:bg-danger-tint disabled:text-grey-400',
  inverse: 'bg-white text-ink hover:bg-grey-200 disabled:bg-grey-500 disabled:text-grey-300',
}

const SIZES: Record<ButtonSize, string> = {
  sm: 'min-h-9 px-3 py-1.5 text-[13px]',
  md: 'min-h-11 px-5 py-2.5 text-sm',
}

/** Shared classes, so a router link can look exactly like a button. */
export function buttonClass(
  variant: ButtonVariant = 'primary',
  size: ButtonSize = 'md',
  extra = '',
): string {
  return `inline-flex items-center justify-center gap-2 rounded font-semibold transition-colors duration-150 ease-out disabled:cursor-not-allowed ${SIZES[size]} ${VARIANTS[variant]} ${extra}`
}
