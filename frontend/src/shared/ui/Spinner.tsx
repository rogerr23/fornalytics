export function Spinner({ label, inverse = false }: { label?: string; inverse?: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-2.5 text-sm ${inverse ? 'text-grey-300' : 'text-grey-500'}`}
      role="status"
    >
      <span
        aria-hidden="true"
        className={`h-4 w-4 animate-spin rounded-full border-2 ${
          inverse ? 'border-ink-600 border-t-white' : 'border-grey-200 border-t-ink'
        }`}
      />
      {label}
    </span>
  )
}
