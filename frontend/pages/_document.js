import Document, { Html, Head, Main, NextScript } from 'next/document'

class MyDocument extends Document {
  render() {
    return (
      <Html lang="en">
        <Head>
          {/* Load runtime-config.js early so window.__RUNTIME_CONFIG is available to client scripts */}
          <script src="/runtime-config.js" />
          
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
          <meta name="theme-color" content="#3b82f6" />
          
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
