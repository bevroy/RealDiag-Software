import '../styles/globals.css'

export const metadata = {
  title: 'RealDiag - Clinical Decision Support',
  description: 'Real-time diagnostic decision support system with Epic/EHR integration',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        {/* Brand teal — mirrors realdiag.org */}
        <meta name="theme-color" content="#0f766e" />
        {/* Brand typography — Poppins (mirrors elionyx.com) */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap"
        />
      </head>
      <body style={{ margin: 0, padding: 0, fontFamily: "'Poppins', system-ui, -apple-system, sans-serif" }}>
        {children}
      </body>
    </html>
  )
}
