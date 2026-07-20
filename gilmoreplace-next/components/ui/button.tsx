/**
 * UI kit: button.
 */

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

/** Shared across all button types — matches legacy `a:hover { opacity: 0.8 }`. */
const opacityHover = "lg:hover:opacity-80";

/** Default / purple — legacy `.btn:hover` + `body.color-theme-white .btn:hover { background: #ccc }`. */
const fillHover = [
  "lg:hover:bg-transparent lg:hover:text-white",
  // specificity like body.color-theme-white .btn:hover — must beat hover:bg-transparent
  "lg:[.color-theme-white_&]:hover:!bg-[#ccc]",
].join(" ");

const buttonVariants = cva(
  [
    "inline-flex items-center justify-center whitespace-normal text-center border border-white",
    "font-[nunito-sans] text-sm font-normal uppercase tracking-[2px] leading-snug",
    "px-[30px] py-[15px] transition-[background,color,opacity] duration-300 ease-in-out",
    "focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
    "bg-white text-[#5B7587]",
    // Legacy: body.color-theme-white .btn { border-color: #000; } — wins over purple/gold borders
    "[.color-theme-white_&]:!border-black",
    opacityHover,
  ].join(" "),
  {
    variants: {
      variant: {
        default: fillHover,
        purple: cn("bg-[#3A3687] text-white border-[#3A3687]", fillHover),
        // Gold: opacity-only on default theme; white theme uses #ccc hover like .btn
        gold: [
          "bg-[#C1A340] text-white border-[#C1A340]",
          "lg:[.color-theme-white_&]:hover:!bg-[#ccc]",
        ].join(" "),
        // Legacy .btn.reverse:hover { background: #fff; color: #5B7587; }
        reverse: [
          "bg-transparent text-white border-white",
          "[.color-theme-white_&]:text-[#5B7587]",
          "lg:hover:!bg-white lg:hover:!text-[#5B7587]",
        ].join(" "),
        link: [
          "border-0 bg-transparent p-0 normal-case tracking-normal text-inherit text-left",
          "hover:bg-transparent hover:text-inherit lg:hover:bg-transparent lg:hover:text-inherit",
          "lg:[.color-theme-white_&]:hover:bg-transparent",
        ].join(" "),
      },
      size: {
        default: "",
        sm: "px-4 py-2 text-xs",
        lg: "px-8 py-4 text-base",
        icon: "h-10 w-10 p-0",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

/** Site button primitive (default / reverse / gold / purple / link). */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size }), className)}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
