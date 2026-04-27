import Document, { Html, Head, Main, NextScript } from 'next/document'

class MyDocument extends Document {
  render() {
    return (
      <Html lang="en">
        <Head>
          {/* Load runtime-config.js early so window.__RUNTIME_CONFIG is available to client scripts */}
          <script src="/runtime-config.js" />

          {/* Brand typography — Poppins (mirrors elionyx.com) */}
          <link rel="preconnect" href="https://fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
          <link
            rel="stylesheet"
            href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap"
          />

          {/* PWA Manifest */}
          <link rel="manifest" href="/manifest.json" />
          
          {/* PWA Meta Tags */}
          <meta name="application-name" content="RealDiag" />
          <meta name="apple-mobile-web-app-capable" content="yes" />
          <meta name="apple-mobile-web-app-status-bar-style" content="default" />
          <meta name="apple-mobile-web-app-title" content="RealDiag" />
          <meta name="description" content="Evidence-based diagnostic decision trees and symptom-based search for medical professionals" />
          <meta name="format-detection" content="telephone=no" />
          <meta name="mobile-web-app-capable" content="yes" />
          {/* Brand teal — mirrors realdiag.org */}
          <meta name="theme-color" content="#0f766e" />
          
          {/* Apple Touch Icons */}
          <link rel="apple-touch-icon" href="/logo.png" />
          
          {/* Favicon */}
          <link rel="icon" type="image/png" href="/logo.png" />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    )
  }
}

export default MyDocument
