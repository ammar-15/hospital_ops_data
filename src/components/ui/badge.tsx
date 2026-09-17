import * as React from "react";
import {cn} from "@/lib/utils";
export function Badge({className,variant="default",...props}:React.ComponentProps<"span"> & {variant?:"default"|"secondary"|"outline"|"destructive"}){return <span className={cn("inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium",variant==="destructive"?"border-amber-200 bg-amber-50 text-amber-900":"border-slate-200 bg-slate-50 text-slate-700",className)} {...props}/>;}
