"use client";
import * as React from "react";
import {Tooltip as Primitive} from "radix-ui";
export const TooltipProvider=Primitive.Provider;
export const Tooltip=Primitive.Root;
export const TooltipTrigger=Primitive.Trigger;
export function TooltipContent(props:React.ComponentProps<typeof Primitive.Content>){return <Primitive.Portal><Primitive.Content sideOffset={5} className="z-50 max-w-72 rounded bg-primary px-3 py-2 text-xs leading-relaxed text-white" {...props}/></Primitive.Portal>;}
