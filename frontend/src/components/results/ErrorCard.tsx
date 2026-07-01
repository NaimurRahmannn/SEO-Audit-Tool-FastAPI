import { TriangleAlertIcon } from "@/components/icons";
import { toReadableErrorMessage } from "@/lib/error-copy";

export default function ErrorCard({
  message,
  onReset,
}: {
  message: string;
  onReset: () => void;
}) {
  const readableMessage = toReadableErrorMessage(
    message,
    "The audit could not be completed. Please try another URL."
  );

  return (
    <div className="flex min-h-[360px] items-center">
      <div className="w-full rounded-2xl border border-line bg-surface p-6 text-center shadow-xl shadow-black/[0.04] sm:p-10">
        <div className="mx-auto max-w-lg">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-fail-bg text-fail">
            <TriangleAlertIcon className="h-6 w-6" />
          </div>
          <h2 className="mt-5 text-xl font-extrabold tracking-tight text-ink">
            {"Audit couldn't be completed"}
          </h2>
          <p className="mt-3 break-words text-sm leading-relaxed text-ink-2 [overflow-wrap:anywhere]">
            {readableMessage}
          </p>
          <button
            type="button"
            onClick={onReset}
            className="mt-6 inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2.5 text-sm font-bold text-white transition-colors hover:bg-primary-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          >
            Try another URL
          </button>
        </div>
      </div>
    </div>
  );
}
