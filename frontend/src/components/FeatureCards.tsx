import type { ComponentType } from "react";

import { BarChartIcon, CheckCircleIcon, ZapIcon } from "@/components/icons";

type Feature = {
  icon: ComponentType<{ className?: string }>;
  title: string;
  description: string;
};

const FEATURES: Feature[] = [
  {
    icon: ZapIcon,
    title: "Instant results",
    description: "A full report in under 30 seconds. No signup needed.",
  },
  {
    icon: CheckCircleIcon,
    title: "Actionable fixes",
    description: "Every issue comes with exactly how to resolve it.",
  },
  {
    icon: BarChartIcon,
    title: "Prioritized",
    description: "Findings ranked by severity, fix what matters first.",
  },
];

export default function FeatureCards() {
  return (
    <section className="grid grid-cols-1 gap-5 sm:grid-cols-3">
      {FEATURES.map(({ icon: Icon, title, description }) => (
        <div
          key={title}
          className="rounded-2xl border border-line bg-surface p-6"
        >
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-soft text-primary">
            <Icon className="h-6 w-6" />
          </span>
          <h3 className="mt-5 text-center text-lg font-bold tracking-tight text-ink">
            {title}
          </h3>
          <p className="mt-2 text-center text-sm leading-relaxed text-ink-2">
            {description}
          </p>
        </div>
      ))}
    </section>
  );
}
