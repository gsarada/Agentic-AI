import type { Category } from "@/lib/types";
import { CATEGORY_BADGE } from "@/lib/format";

export function CategoryBadge({ category }: { category: Category }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${CATEGORY_BADGE[category]}`}
    >
      {category}
    </span>
  );
}
