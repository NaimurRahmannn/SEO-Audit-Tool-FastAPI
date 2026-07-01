// Tailwind class maps for severity/band styling. Kept as full literal strings
// (never constructed dynamically) so Tailwind's JIT can detect them.

import type { Severity } from "./types";
import type { Band } from "./audit-format";

export const BAND_BAR: Record<Band, string> = {
  green: "bg-pass",
  amber: "bg-warn",
  red: "bg-fail",
};

export const BAND_TEXT: Record<Band, string> = {
  green: "text-pass",
  amber: "text-warn",
  red: "text-fail",
};

export const SEV_BADGE: Record<Severity, string> = {
  pass: "bg-pass-bg text-pass-ink",
  warning: "bg-warn-bg text-warn-ink",
  fail: "bg-fail-bg text-fail-ink",
};

export const SEV_BAR: Record<Severity, string> = {
  pass: "bg-pass",
  warning: "bg-warn",
  fail: "bg-fail",
};

export const SEV_RECO: Record<Severity, string> = {
  pass: "bg-pass-bg text-pass-ink",
  warning: "bg-warn-bg text-warn-ink",
  fail: "bg-fail-bg text-fail-ink",
};

export const SEV_RANK: Record<Severity, string> = {
  pass: "bg-pass-bg text-pass-ink",
  warning: "bg-warn-bg text-warn-ink",
  fail: "bg-fail-bg text-fail-ink",
};
