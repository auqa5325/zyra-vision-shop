import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { Badge } from "./badge";

const discountPriceVariants = cva(
  "flex items-center gap-2 transition-all duration-300",
  {
    variants: {
      size: {
        sm: "text-sm",
        md: "text-base",
        lg: "text-lg",
        xl: "text-xl",
        "2xl": "text-2xl",
        "3xl": "text-3xl",
        "4xl": "text-4xl",
      },
      layout: {
        horizontal: "flex-row items-center",
        vertical: "flex-col items-start",
        compact: "flex-row items-center gap-1",
      },
      alignment: {
        left: "justify-start",
        center: "justify-center",
        right: "justify-end",
      },
    },
    defaultVariants: {
      size: "md",
      layout: "horizontal",
      alignment: "left",
    },
  }
);

const discountBadgeVariants = cva(
  "inline-flex items-center rounded-full font-semibold transition-all duration-300 hover:scale-105",
  {
    variants: {
      size: {
        sm: "px-1.5 py-0.5 text-xs",
        md: "px-2 py-1 text-xs",
        lg: "px-2.5 py-1 text-sm",
        xl: "px-3 py-1.5 text-sm",
      },
      variant: {
        default: "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/25",
        destructive: "bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-lg shadow-red-500/25",
        secondary: "bg-gradient-to-r from-violet-500 to-purple-500 text-white shadow-lg shadow-violet-500/25",
        outline: "border-2 border-emerald-500 text-emerald-600 bg-emerald-50 dark:bg-emerald-950/20 dark:text-emerald-400",
      },
    },
    defaultVariants: {
      size: "md",
      variant: "default",
    },
  }
);

export interface DiscountPriceProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof discountPriceVariants> {
  price: number;
  discountPercent?: number;
  currency?: string;
  showOriginalPrice?: boolean;
  badgeVariant?: VariantProps<typeof discountBadgeVariants>["variant"];
  badgeSize?: VariantProps<typeof discountBadgeVariants>["size"];
  className?: string;
}

function DiscountPrice({
  price,
  discountPercent = 0,
  currency = "₹",
  showOriginalPrice = true,
  size,
  layout,
  alignment,
  badgeVariant = "default",
  badgeSize,
  className,
  ...props
}: DiscountPriceProps) {
  const discountedPrice = discountPercent > 0 ? price * (1 - discountPercent / 100) : price;
  const hasDiscount = discountPercent > 0;

  // Auto-adjust badge size based on price size if not specified
  const finalBadgeSize = badgeSize || (size === "sm" ? "sm" : size === "lg" || size === "xl" ? "lg" : "md");

  if (!hasDiscount) {
    return (
      <div className={cn(discountPriceVariants({ size, layout, alignment }), className)} {...props}>
        <span className="font-bold text-foreground">
          {currency}{price.toLocaleString()}
        </span>
      </div>
    );
  }

  return (
    <div className={cn(discountPriceVariants({ size, layout, alignment }), className)} {...props}>
      {layout === "vertical" ? (
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="font-bold text-emerald-600 dark:text-emerald-400">
              {currency}{Math.round(discountedPrice).toLocaleString()}
            </span>
            <span className={cn(discountBadgeVariants({ size: finalBadgeSize, variant: badgeVariant }))}>
              {discountPercent}% OFF
            </span>
          </div>
          {showOriginalPrice && (
            <span className="text-muted-foreground line-through text-sm">
              {currency}{price.toLocaleString()}
            </span>
          )}
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <span className="font-bold text-emerald-600 dark:text-emerald-400">
            {currency}{Math.round(discountedPrice).toLocaleString()}
          </span>
          <span className={cn(discountBadgeVariants({ size: finalBadgeSize, variant: badgeVariant }))}>
            {discountPercent}% OFF
          </span>
          {showOriginalPrice && (
            <span className="text-muted-foreground line-through text-sm">
              {currency}{price.toLocaleString()}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export { DiscountPrice };
