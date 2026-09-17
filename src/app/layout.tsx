import type {Metadata} from 'next';
import './globals.css';
import {ExplorerProvider} from '@/components/explorer-provider';
import {AppShell} from '@/components/app-shell';
import {GuidedTour} from '@/components/guided-tour';
import {ProjectAssistant} from '@/components/project-assistant';
export const metadata:Metadata={title:'Ontario Hospital Quality Improvement Explorer',description:'Explore Ontario hospital emergency department improvement planning, implementation and reporting quality.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><ExplorerProvider><AppShell>{children}</AppShell><GuidedTour/><ProjectAssistant/></ExplorerProvider></body></html>;}
