import { Button } from "./Button";

export function Pagination({
  hasNext,
  hasPrevious,
  onNext,
  onPrevious,
  count,
}: {
  hasNext: boolean;
  hasPrevious: boolean;
  onNext: () => void;
  onPrevious: () => void;
  count: number;
}) {
  return (
    <div className="flex items-center justify-between border-t border-ink-100 px-1 py-3">
      <span className="text-sm text-ink-500">{count} total</span>
      <div className="flex gap-2">
        <Button variant="secondary" size="sm" onClick={onPrevious} disabled={!hasPrevious}>
          Previous
        </Button>
        <Button variant="secondary" size="sm" onClick={onNext} disabled={!hasNext}>
          Next
        </Button>
      </div>
    </div>
  );
}
