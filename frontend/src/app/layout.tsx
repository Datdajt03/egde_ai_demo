import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Smart Classroom Analytics - Edge AI Edition',
  description: 'Real-time student detection, attendance tracking, and AI-generated classroom reports.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-[#070A0F] text-[#E2E8F0]">
        {children}
      </body>
    </html>
  )
}
