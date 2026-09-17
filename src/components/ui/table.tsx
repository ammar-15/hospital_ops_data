import * as React from "react";
import {cn} from "@/lib/utils";
export function Table({className,...props}:React.ComponentProps<"table">){return <div tabIndex={0} role="region" aria-label="Scrollable data table" className="relative w-full overflow-x-auto"><table className={cn("w-full text-left text-sm",className)} {...props}/></div>;}
export function TableHeader({className,...props}:React.ComponentProps<"thead">){return <thead className={cn("border-b bg-slate-50",className)} {...props}/>;}
export function TableBody({className,...props}:React.ComponentProps<"tbody">){return <tbody className={cn("[&_tr:last-child]:border-0",className)} {...props}/>;}
export function TableRow({className,...props}:React.ComponentProps<"tr">){return <tr className={cn("border-b border-slate-200 hover:bg-slate-50",className)} {...props}/>;}
export function TableHead({className,...props}:React.ComponentProps<"th">){return <th className={cn("px-4 py-3 font-semibold text-slate-700",className)} {...props}/>;}
export function TableCell({className,...props}:React.ComponentProps<"td">){return <td className={cn("px-4 py-3 align-top",className)} {...props}/>;}
export function TableCaption({className,...props}:React.ComponentProps<"caption">){return <caption className={cn("mt-3 text-sm text-slate-600",className)} {...props}/>;}
