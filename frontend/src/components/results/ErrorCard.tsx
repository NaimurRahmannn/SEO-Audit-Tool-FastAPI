import { TriangleAlertIcon } from "@/components/icons";

export default function ErrorCard({
  message,
  onReset,
}: {
  message: string;
  onReset: () => void;
}) {
  return (
    <div className="mx-auto max-w-md rounded-2xl border border-line bg-surface p-10 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-fail-bg text-fail">
        <TriangleAlertIcon className="h-6 w-6" />
      </div>
      <h2 className="mt-5 text-lg font-bold text-ink">Audit failed</h2>
      <p className="mt-2 text-sm text-ink-2">{message}</p>
      <button
        type="button"
        onClick={onReset}
        className="mt-6 inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-primary-ink"
      >
        Try another URL
      </button>
    </div>
  );
}
