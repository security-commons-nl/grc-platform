import clsx from 'clsx';

interface LoadingSkeletonProps {
  className?: string;
  lines?: number;
}

function SkeletonLine({ className }: { className?: string }) {
  return (
    <div
      className={clsx(
        'animate-pulse rounded bg-neutral-200',
        className || 'h-4 w-full',
      )}
    />
  );
}

export function LoadingSkeleton({ className, lines = 3 }: LoadingSkeletonProps) {
  return (
    <div className={clsx('space-y-3', className)}>
      {Array.from({ length: lines }, (_, i) => (
        <SkeletonLine
          key={i}
          className={i === lines - 1 ? 'h-4 w-2/3' : 'h-4 w-full'}
        />
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-white border border-neutral-200 rounded-lg shadow-sm p-6 space-y-4 animate-pulse">
      <div className="h-5 w-1/3 rounded bg-neutral-200" />
      <div className="space-y-2">
        <div className="h-4 w-full rounded bg-neutral-200" />
        <div className="h-4 w-5/6 rounded bg-neutral-200" />
        <div className="h-4 w-2/3 rounded bg-neutral-200" />
      </div>
    </div>
  );
}
