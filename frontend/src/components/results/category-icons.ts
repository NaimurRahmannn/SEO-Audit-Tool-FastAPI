import type { ComponentType } from "react";

import {
  CodeIcon,
  DocIcon,
  GaugeIcon,
  HeadingIcon,
  ImageIcon2,
  LinkIcon,
  PersonIcon,
  ShareIcon,
} from "@/components/icons";
import type { CheckCategory } from "@/lib/types";

type IconComponent = ComponentType<{ className?: string }>;

const CATEGORY_ICON: Record<CheckCategory, IconComponent> = {
  meta: DocIcon,
  headings: HeadingIcon,
  images: ImageIcon2,
  links: LinkIcon,
  social: ShareIcon,
  structured_data: CodeIcon,
  performance: GaugeIcon,
  accessibility: PersonIcon,
};

export function categoryIcon(category: CheckCategory): IconComponent {
  return CATEGORY_ICON[category] ?? DocIcon;
}
