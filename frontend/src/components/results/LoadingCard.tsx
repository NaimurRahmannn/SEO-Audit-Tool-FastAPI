import Spinner from "@/components/Spinner";
import { displayUrl } from "@/lib/audit-format";
import type { JobStatus } from "@/lib/types";

export default function LoadingCard({
  url,
  status,
}: {
  url: string;
  status: JobStatus;
}) {
  const label = status === "running" ? "Running audit…" : "Starting audit…";

  return (
    <div className="mx-auto max-w-md rounded-2xl border border-line bg-surface p-10 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary-soft text-primary">
        <Spinner className="h-6 w-6" />
      </div>
      <h2 className="mt-5 text-lg font-bold text-ink">{label}</h2>
      <p className="mt-1 break-all text-sm text-ink-2">{displayUrl(url)}</p>
      <p className="mt-4 text-xs text-ink-3">This can take up to 30 seconds.</p>
    </div>
  );
}
