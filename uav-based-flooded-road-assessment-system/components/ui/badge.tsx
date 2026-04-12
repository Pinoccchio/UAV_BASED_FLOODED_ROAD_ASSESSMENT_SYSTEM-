import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center text-xs font-medium transition-colors px-2.5 py-0.5 rounded-md",
  {
    variants: {
      variant: {
        default:
          "bg-primary/15 text-primary border border-primary/30",
        passable:
          "bg-[var(--status-passable)]/15 text-[var(--status-passable)] border border-[var(--status-passable)]/35",
        limited:
          "bg-[var(--status-limited)]/15 text-[var(--status-limited)] border border-[var(--status-limited)]/35",
        impassable:
          "bg-[var(--status-impassable)]/15 text-[var(--status-impassable)] border border-[var(--status-impassable)]/35",
        cyan:
          "bg-primary/10 text-primary border border-primary/25",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
