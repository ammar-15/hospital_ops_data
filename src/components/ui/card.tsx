import * as React from "react";
import { cn } from "@/lib/utils";
export function Card({className,...props}:React.ComponentProps<"div">){return <div className={cn("rounded border border-slate-200 bg-white",className)} {...props}/>;}
export function CardHeader({className,...props}:React.ComponentProps<"div">){return <div className={cn("px-5 pt-5 pb-3",className)} {...props}/>;}
export function CardTitle({className,...props}:React.ComponentProps<"h2">){return <h2 className={cn("text-base font-semibold text-primary",className)} {...props}/>;}
export function CardDescription({className,...props}:React.ComponentProps<"p">){return <p className={cn("mt-1 text-sm text-slate-600",className)} {...props}/>;}
export function CardContent({className,...props}:React.ComponentProps<"div">){return <div className={cn("px-5 pb-5",className)} {...props}/>;}
export function CardFooter({className,...props}:React.ComponentProps<"div">){return <div className={cn("flex items-center px-5 pb-5",className)} {...props}/>;}
