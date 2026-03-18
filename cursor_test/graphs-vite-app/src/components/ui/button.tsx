import { forwardRef, type ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'primary', size = 'md', children, disabled, ...props }, ref) => {
    const base =
      'inline-flex items-center justify-center font-medium rounded-xl transition focus:outline-none focus:ring-2 focus-visible:ring-primary-500/50 disabled:opacity-50 disabled:cursor-not-allowed'
    const variants = {
      primary:
        'bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 shadow-lg shadow-primary-500/25',
      secondary:
        'bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] hover:border-primary-500/50',
    }
    const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-6 py-3' }
    return (
      <button
        ref={ref}
        type="button"
        className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    )
  },
)
Button.displayName = 'Button'
