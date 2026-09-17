import * as React from "react";
import {cn} from "@/lib/utils";
export function Input({className,type,...props}:React.ComponentProps<"input">){return <input type={type} className={cn("h-10 w-full min-w-0 rounded border border-slate-300 bg-white px-3 text-sm focus-visible:outline-2 focus-visible:outline-teal-700",className)} {...props}/>;}
