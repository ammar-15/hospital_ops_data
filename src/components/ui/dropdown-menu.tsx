"use client";
import * as React from "react";
import {DropdownMenu as Primitive} from "radix-ui";
import {Check} from "lucide-react";
import {cn} from "@/lib/utils";
export const DropdownMenu=Primitive.Root;
export const DropdownMenuTrigger=Primitive.Trigger;
export function DropdownMenuContent({className,sideOffset=4,...props}:React.ComponentProps<typeof Primitive.Content>){return <Primitive.Portal><Primitive.Content sideOffset={sideOffset} className={cn("z-50 min-w-48 rounded border border-slate-200 bg-white p-1 text-sm",className)} {...props}/></Primitive.Portal>;}
export function DropdownMenuCheckboxItem({className,children,checked,...props}:React.ComponentProps<typeof Primitive.CheckboxItem>){return <Primitive.CheckboxItem checked={checked} className={cn("relative flex cursor-pointer items-center rounded py-2 pr-3 pl-8 outline-none focus:bg-slate-100",className)} {...props}><span className="absolute left-2"><Primitive.ItemIndicator><Check size={16}/></Primitive.ItemIndicator></span>{children}</Primitive.CheckboxItem>;}
export function DropdownMenuLabel({className,...props}:React.ComponentProps<typeof Primitive.Label>){return <Primitive.Label className={cn("px-2 py-2 font-semibold",className)} {...props}/>;}
export function DropdownMenuSeparator(props:React.ComponentProps<typeof Primitive.Separator>){return <Primitive.Separator className="my-1 h-px bg-slate-200" {...props}/>;}
