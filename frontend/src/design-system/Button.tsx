import type { ButtonHTMLAttributes, ReactNode } from 'react';
import './Button.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  loading?: boolean;
  fullWidth?: boolean;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  loading = false,
  fullWidth = false,
  disabled,
  className = '',
  onClick,
  ...props
}: ButtonProps) {
  const classNames = [
    'grace-button',
    `grace-button--${variant}`,
    `grace-button--${size}`,
    fullWidth && 'grace-button--full',
    loading && 'grace-button--loading',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      className={classNames}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading && <span className="grace-button__spinner" />}
      {!loading && icon && <span className="grace-button__icon">{icon}</span>}
      <span className="grace-button__text">{children}</span>
    </button>
  );
}
