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
      <body style={{ margin: 0, padding: 0 }}>{children}</body>
    </html>
  )
}
