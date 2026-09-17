"use client";
import * as React from "react";
import {Dialog as SheetPrimitive} from "radix-ui";
import {X} from "lucide-react";
import {cn} from "@/lib/utils";
export const Sheet=SheetPrimitive.Root;
export const SheetTrigger=SheetPrimitive.Trigger;
export const SheetClose=SheetPrimitive.Close;
export function SheetContent({className,children,side="right",...props}:React.ComponentProps<typeof SheetPrimitive.Content>&{side?:"right"|"left"}){return <SheetPrimitive.Portal><SheetPrimitive.Overlay className="fixed inset-0 z-40 bg-slate-950/35"/><SheetPrimitive.Content className={cn("fixed inset-y-0 z-50 w-full overflow-y-auto bg-white p-6 sm:max-w-2xl",side==="right"?"right-0 border-l":"left-0 border-r",className)} {...props}>{children}<SheetPrimitive.Close className="absolute right-4 top-4 rounded p-2 text-slate-600 hover:bg-slate-100" aria-label="Close details"><X size={18}/></SheetPrimitive.Close></SheetPrimitive.Content></SheetPrimitive.Portal>;}
export function SheetHeader({className,...props}:React.ComponentProps<"div">){return <div className={cn("mb-6 space-y-2 pr-9",className)} {...props}/>;}
export function SheetTitle({className,...props}:React.ComponentProps<typeof SheetPrimitive.Title>){return <SheetPrimitive.Title className={cn("text-xl font-semibold text-primary",className)} {...props}/>;}
export function SheetDescription({className,...props}:React.ComponentProps<typeof SheetPrimitive.Description>){return <SheetPrimitive.Description className={cn("text-sm text-slate-600",className)} {...props}/>;}
