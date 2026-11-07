import type { ButtonHTMLAttributes } from 'react'
import { Link, type LinkProps } from 'react-router-dom'
import { buttonClass, type ButtonSize as Size, type ButtonVariant as Variant } from './buttonClass'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
}

export function Button({
  variant = 'primary',
  size = 'md',
  className = '',
  ...props
}: ButtonProps) {
  return <button type="button" className={buttonClass(variant, size, className)} {...props} />
}

interface ButtonLinkProps extends LinkProps {
  variant?: Variant
  size?: Size
}

/** A navigation link styled as a button (never a button inside a link). */
export function ButtonLink({
  variant = 'primary',
  size = 'md',
  className = '',
  ...props
}: ButtonLinkProps) {
  return <Link className={buttonClass(variant, size, className)} {...props} />
}
