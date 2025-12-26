import './globals.css'
import { ClerkProvider } from '@clerk/nextjs'
import { Toaster } from 'sonner'
import ErrorBoundary from './components/ErrorBoundary'

export const metadata = {
  title: 'QuantStack - Professional Stock Screening',
  description: 'Screen stocks like hedge funds using CANSLIM, Minervini, Darvas Box, and 7 more institutional-grade quantitative models. Free forever.',
  keywords: 'stock screening, quantitative analysis, CANSLIM, Minervini, trading, investment',
}

// Check if Clerk keys are configured
const hasClerkKeys = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.CLERK_SECRET_KEY;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body>
        <ErrorBoundary>
          {hasClerkKeys ? (
            <ClerkProvider>{children}</ClerkProvider>
          ) : (
            children
          )}
          <Toaster richColors position="top-right" />
        </ErrorBoundary>
      </body>
    </html>
  )
}
