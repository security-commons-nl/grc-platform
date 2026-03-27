import { type ReactNode, type ElementType } from 'react';
import { Button } from './button';

interface EmptyStateProps {
  icon?: ElementType;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  children?: ReactNode;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  children,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      {Icon && (
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-neutral-100">
          <Icon className="h-7 w-7 text-neutral-400" />
        </div>
      )}
      <h3 className="text-base font-semibold text-neutral-800">{title}</h3>
      {description && (
        <p className="mt-1.5 max-w-sm text-sm text-neutral-600">
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <div className="mt-5">
          <Button size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
      {children && <div className="mt-5">{children}</div>}
    </div>
  );
}
