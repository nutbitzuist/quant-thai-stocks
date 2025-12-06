import './globals.css'

export const metadata = {
  title: 'Quant Stock Analysis',
  description: 'Quantitative analysis platform for US and Thai stocks',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
