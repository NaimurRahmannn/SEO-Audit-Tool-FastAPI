import { CheckTickIcon } from "@/components/icons";

const CHECKS = [
  "Page title",
  "Meta description",
  "Headings H1–H6",
  "Image alt text",
  "Canonical URL",
  "Robots meta",
  "Open Graph",
  "Twitter Cards",
  "Structured data",
  "Internal links",
  "Broken links",
  "Performance",
  "Accessibility",
  "Lighthouse SEO",
  "Core Web Vitals",
  "Mobile-friendly",
];

export default function ChecklistGrid() {
  return (
    <section
      id="what-we-check"
      className="rounded-2xl border border-line bg-surface p-6 sm:p-8"
    >
      <h2 className="text-xs font-semibold uppercase tracking-wider text-ink-3">
        Everything we check
      </h2>

      <ul className="mt-5 grid grid-cols-2 gap-x-6 gap-y-3.5 md:grid-cols-4">
        {CHECKS.map((check) => (
          <li key={check} className="flex items-center gap-2.5">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary">
              <CheckTickIcon className="h-3 w-3" />
            </span>
            <span className="text-sm text-ink-2">{check}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
