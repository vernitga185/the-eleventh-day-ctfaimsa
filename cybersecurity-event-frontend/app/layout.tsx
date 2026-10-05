import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'The Eleventh Day — Kuru Battlefield Archive',
  description: 'A recovered battlefield witness from Kurukshetra. Investigate Record XI.',
  generator: 'v0.app',
  icons: {
    icon: '/logo.jpg',
    apple: '/logo.jpg',
  },
}

export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <script
          dangerouslySetInnerHTML={{
            __html: `document.addEventListener('contextmenu', event => event.preventDefault());
              document.addEventListener('keydown', event => {
                if (event.keyCode === 123 || 
                   (event.ctrlKey && event.shiftKey && (event.keyCode === 73 || event.keyCode === 74)) || 
                   (event.ctrlKey && event.keyCode === 85)) {
                  event.preventDefault();
                }
              });` 
          }}
        />
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}



