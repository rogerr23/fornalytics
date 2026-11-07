/** Stroke-only icons in currentColor (1.5px, square ends), per the design system. Never emoji. */

const PATHS = {
  check: 'M20 6 9 17l-5-5',
  alert:
    'M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z',
  info: 'M12 16v-4M12 8h.01M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z',
  close: 'M18 6 6 18M6 6l12 12',
  search: 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14ZM20 20l-3.5-3.5',
  minus: 'M5 12h14',
  plus: 'M12 5v14M5 12h14',
  upload: 'M12 16V4M7 9l5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3',
  file: 'M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8ZM14 3v5h5M9 13h6M9 17h6',
  folder: 'M3 6a1 1 0 0 1 1-1h5l2 2h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z',
  link: 'M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1',
  text: 'M4 6h16M4 10h16M4 14h10M4 18h7',
  refresh: 'M20 12a8 8 0 1 1-2.3-5.7L20 8.6M20 4v4.6h-4.6',
  arrow: 'M5 12h14M13 6l6 6-6 6',
  layers: 'M12 3 3 8l9 5 9-5ZM3 13l9 5 9-5',
  chat: 'M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.4A8 8 0 1 1 21 12Z',
  flow: 'M5 3h4v4H5ZM15 17h4v4h-4ZM7 7v5a2 2 0 0 0 2 2h6a2 2 0 0 1 2 2v1',
} as const

export type IconName = keyof typeof PATHS

interface IconProps {
  name: IconName
  size?: number
  className?: string
  /** Gives the icon a meaning for screen readers; without it the icon is decorative. */
  label?: string
}

export function Icon({ name, size = 18, className = '', label }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="square"
      strokeLinejoin="miter"
      className={className}
      role={label ? 'img' : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
    >
      <path d={PATHS[name]} />
    </svg>
  )
}
