import * as React from "react";
import { Slot } from "radix-ui";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
export const buttonVariants = cva("inline-flex items-center justify-center gap-2 rounded border text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 disabled:opacity-50 disabled:pointer-events-none", { variants: { variant: { default: "border-primary bg-primary text-white hover:bg-[#234e74]", outline: "border-slate-300 bg-white text-slate-800 hover:bg-slate-100", ghost: "border-transparent hover:bg-slate-100 text-slate-700", secondary: "border-slate-200 bg-slate-100 text-slate-800" }, size: { default: "min-h-10 px-4 py-2", sm: "min-h-9 px-3 py-1.5", icon: "size-10" } }, defaultVariants: { variant: "default", size: "default" } });
export function Button({ className, variant, size, asChild = false, ...props }: React.ComponentProps<"button"> & VariantProps<typeof buttonVariants> & { asChild?: boolean }) { const Comp = asChild ? Slot.Root : "button"; return <Comp className={cn(buttonVariants({ variant, size }), className)} {...props} />; }
