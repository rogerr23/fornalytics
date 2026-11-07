/** Grey placeholder blocks shown while content loads (instead of a lone spinner). */
export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <span aria-hidden="true" className={`block animate-pulse rounded bg-grey-100 ${className}`} />
  )
}

/** A paragraph-shaped placeholder with a screen-reader label. */
export function SkeletonText({ lines = 4, label }: { lines?: number; label: string }) {
  return (
    <div role="status" aria-label={label} className="flex flex-col gap-2.5">
      {Array.from({ length: lines }, (_, index) => (
        <Skeleton key={index} className={`h-3.5 ${index === lines - 1 ? 'w-2/3' : 'w-full'}`} />
      ))}
      <span className="sr-only">{label}</span>
    </div>
  )
}
