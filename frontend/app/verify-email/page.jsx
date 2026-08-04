"use client"

import React, { Suspense, useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { storeAuthData } from '../../utils/clientAuth'

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div style={{ color: 'white', fontSize: '18px' }}>Loading...</div>
      </div>
    }>
      <VerifyEmail />
    </Suspense>
  )
}

function VerifyEmail() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState('verifying') // verifying, success, error
  const [message, setMessage] = useState('Verifying your email...')
  const [user, setUser] = useState(null)

  useEffect(() => {
    const token = searchParams.get('token')
    
    if (!token) {
      setStatus('error')
      setMessage('Invalid verification link. Please check your email for the correct link.')
      return
    }

    verifyEmail(token)
  }, [searchParams])

  const verifyEmail = async (token) => {
    try {
      const response = await fetch(
        `https://realdiag-backend.onrender.com/users/verify-email?token=${token}`,
        {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      const data = await response.json()

      if (response.ok) {
        setStatus('success')
        setMessage(data.message || 'Email verified successfully!')
        setUser(data.user)
        
        // Store user data
        if (data.user) {
          storeAuthData(data.user, data.csrf_token || null)
        }

        // Redirect to main site after 3 seconds
        setTimeout(() => {
          window.location.href = 'https://realdiag.netlify.app/'
        }, 3000)
      } else {
        setStatus('error')
        setMessage(data.detail || 'Email verification failed. Please try again.')
      }
    } catch (error) {
      setStatus('error')
      setMessage('Network error. Please check your connection and try again.')
      console.error('Verification error:', error)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        maxWidth: '500px',
        width: '100%',
        padding: '40px',
        textAlign: 'center'
      }}>
        {status === 'verifying' && (
          <>
            <div style={{
              width: '80px',
              height: '80px',
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #667eea',
              borderRadius: '50%',
              margin: '0 auto 20px',
              animation: 'spin 1s linear infinite'
            }} />
            <h1 style={{ fontSize: '24px', marginBottom: '10px', color: '#333' }}>
              Verifying Email
            </h1>
            <p style={{ color: '#666' }}>Please wait while we verify your email address...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div style={{
              width: '80px',
              height: '80px',
              background: '#10b981',
              borderRadius: '50%',
              margin: '0 auto 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '48px',
              color: 'white'
            }}>
              ✓
            </div>
            <h1 style={{ fontSize: '24px', marginBottom: '10px', color: '#333' }}>
              Email Verified!
            </h1>
            <p style={{ color: '#666', marginBottom: '20px' }}>{message}</p>
            {user && (
              <div style={{
                background: '#f9fafb',
                padding: '20px',
                borderRadius: '8px',
                marginBottom: '20px',
                textAlign: 'left'
              }}>
                <h3 style={{ fontSize: '16px', marginBottom: '10px', color: '#333' }}>
                  Your Employee Account
                </h3>
                <p style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>
                  <strong>Name:</strong> {user.full_name}
                </p>
                <p style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>
                  <strong>Email:</strong> {user.email}
                </p>
                <p style={{ fontSize: '14px', color: '#10b981', marginTop: '10px' }}>
                  ✓ Full access to all RealDiag features
                </p>
              </div>
            )}
            <p style={{ color: '#999', fontSize: '14px' }}>
              Redirecting to RealDiag in a few seconds...
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <div style={{
              width: '80px',
              height: '80px',
              background: '#ef4444',
              borderRadius: '50%',
              margin: '0 auto 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '48px',
              color: 'white'
            }}>
              ✕
            </div>
            <h1 style={{ fontSize: '24px', marginBottom: '10px', color: '#333' }}>
              Verification Failed
            </h1>
            <p style={{ color: '#666', marginBottom: '20px' }}>{message}</p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              <button
                onClick={() => router.push('/login')}
                style={{
                  padding: '12px 24px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                Go to Login
              </button>
              <button
                onClick={() => window.location.reload()}
                style={{
                  padding: '12px 24px',
                  background: 'white',
                  color: '#667eea',
                  border: '2px solid #667eea',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                Try Again
              </button>
            </div>
          </>
        )}

        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  )
}
