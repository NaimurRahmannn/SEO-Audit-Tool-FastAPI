// Small inline icon set (no icon dependency). All inherit `currentColor`.

import type { ReactNode } from "react";

type IconProps = { className?: string };

export function BrandMark({ className = "" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="2" />
      <circle cx="12" cy="12" r="3" fill="currentColor" />
    </svg>
  );
}

export function GlobeIcon({ className = "" }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18" />
      <path d="M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18" />
    </svg>
  );
}

export function ArrowRightIcon({ className = "" }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.25"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </svg>
  );
}

export function ZapIcon({ className = "" }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z" />
    </svg>
  );
}

export function CheckCircleIcon({ className = "" }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" />
      <path d="m8.5 12 2.5 2.5 4.5-5" />
    </svg>
  );
}

export function BarChartIcon({ className = "" }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M6 20v-6" />
      <path d="M12 20V8" />
      <path d="M18 20v-10" />
    </svg>
  );
}

export function CheckTickIcon({ className = "" }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="m5 12.5 4.5 4.5L19 7" />
    </svg>
  );
}

function stroked(path: ReactNode, className: string, width = 1.75) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={width}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {path}
    </svg>
  );
}

export function PlusIcon({ className = "" }: IconProps) {
  return stroked(<path d="M12 5v14M5 12h14" />, className, 2.25);
}

export function RerunIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <path d="M3 12a9 9 0 0 1 15.5-6.3L21 8" />
      <path d="M21 3v5h-5" />
      <path d="M21 12a9 9 0 0 1-15.5 6.3L3 16" />
      <path d="M3 21v-5h5" />
    </>,
    className
  );
}

export function ClockIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>,
    className
  );
}

export function PhoneIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <rect x="7" y="3" width="10" height="18" rx="2" />
      <path d="M11 18h2" />
    </>,
    className
  );
}

export function ListIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <path d="M8 6h12M8 12h12M8 18h12" />
      <path d="M3.5 6h.01M3.5 12h.01M3.5 18h.01" />
    </>,
    className
  );
}

export function FlagIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <path d="M5 21V4" />
      <path d="M5 4h11l-1.5 4L16 12H5" fill="currentColor" stroke="none" />
    </>,
    className
  );
}

export function TriangleAlertIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <path d="M12 3.5 21 19H3l9-15.5Z" />
      <path d="M12 10v4" />
      <path d="M12 17h.01" />
    </>,
    className,
    2
  );
}

export function XIcon({ className = "" }: IconProps) {
  return stroked(<path d="M6 6l12 12M18 6 6 18" />, className, 2.5);
}

export function LightbulbIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <path d="M9 18h6" />
      <path d="M10 21h4" />
      <path d="M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3Z" />
    </>,
    className
  );
}

// --- Category icons ---

export function DocIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <path d="M7 3h7l4 4v14H7z" />
      <path d="M14 3v4h4" />
      <path d="M10 12h5M10 16h5" />
    </>,
    className
  );
}

export function HeadingIcon({ className = "" }: IconProps) {
  return stroked(<path d="M7 5v14M17 5v14M7 12h10" />, className, 2.25);
}

export function ImageIcon2({ className = "" }: IconProps) {
  return stroked(
    <>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="9" cy="10" r="1.6" />
      <path d="m4 18 5-4 4 3 3-2 4 3" />
    </>,
    className
  );
}

export function LinkIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <path d="M9 15 15 9" />
      <path d="M11 6.5 13 4.5a4 4 0 0 1 6 6l-2 2" />
      <path d="M13 17.5 11 19.5a4 4 0 0 1-6-6l2-2" />
    </>,
    className
  );
}

export function ShareIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <circle cx="6" cy="12" r="2.5" />
      <circle cx="18" cy="6" r="2.5" />
      <circle cx="18" cy="18" r="2.5" />
      <path d="m8.2 10.8 7.6-3.6M8.2 13.2l7.6 3.6" />
    </>,
    className
  );
}

export function CodeIcon({ className = "" }: IconProps) {
  return stroked(<path d="m9 8-4 4 4 4M15 8l4 4-4 4" />, className, 2);
}

export function GaugeIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <path d="M4 18a8 8 0 1 1 16 0" />
      <path d="m13 13-2.5 2.5" />
    </>,
    className
  );
}

export function PersonIcon({ className = "" }: IconProps) {
  return stroked(
    <>
      <circle cx="12" cy="5" r="2" />
      <path d="M5 9h14" />
      <path d="M12 7v7M9 21l3-7 3 7" />
    </>,
    className
  );
}
