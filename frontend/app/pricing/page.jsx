"use client"

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getStoredUser } from '../../utils/clientAuth'

export default function PricingPage() {
  const router = useRouter()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedInterval, setSelectedInterval] = useState('monthly')

  useEffect(() => {
    const storedUser = getStoredUser()
    setUser(storedUser)
    setLoading(false)
  }, [])

  const plans = [
    {
      id: 'individual_starter',
      name: 'Starter',
      price: { monthly: 29, yearly: 290 },
      description: 'Perfect for solo clinicians getting started',
      features: [
        'Unlimited diagnostic searches',
        '1 clinical module of your choice',
        'Save favorites',
        'Search history',
        'Custom lists',
        'PDF exports',
        'Email support'
      ],
      recommended: false
    },
    {
      id: 'individual_professional',
      name: 'Professional',
      price: { monthly: 49, yearly: 490 },
      description: 'All clinical modules included',
      features: [
        'Everything in Starter, plus:',
        'All clinical modules',
        'FHIR integration',
        'Advanced search filters',
        'Priority email support',
        'Teaching mode',
        'Simulated cases'
      ],
      recommended: true
    },
    {
      id: 'individual_professional_plus',
      name: 'Professional Plus',
      price: { monthly: 69, yearly: 690 },
      description: 'For advanced users with API needs',
      features: [
        'Everything in Professional, plus:',
        'API access',
        'Analytics dashboard',
        'Usage insights',
        'Webhook integrations',
        'Phone support',
        'Priority feature requests'
      ],
      recommended: false
    }
  ]

  const handleSelectPlan = (planId) => {
    if (!user) {
      router.push('/register')
      return
    }

    // For MVP, show message that payment is coming soon
    alert('Payment processing coming soon! For now, please contact support@realdiag.org to upgrade your account.')
  }

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #667eea',
          borderRadius: '50%',
          margin: '0 auto',
          animation: 'spin 1s linear infinite'
        }} />
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Choose Your Plan</h1>
        <p style={styles.subtitle}>
          Unlock the full power of RealDiag Clinical Decision Support
        </p>

        {/* Billing interval toggle */}
        <div style={styles.toggleContainer}>
          <button
            onClick={() => setSelectedInterval('monthly')}
            style={{
              ...styles.toggleButton,
              ...(selectedInterval === 'monthly' ? styles.toggleButtonActive : {})
            }}
          >
            Monthly
          </button>
          <button
            onClick={() => setSelectedInterval('yearly')}
            style={{
              ...styles.toggleButton,
              ...(selectedInterval === 'yearly' ? styles.toggleButtonActive : {})
            }}
          >
            Yearly
            <span style={styles.saveBadge}>Save 17%</span>
          </button>
        </div>
      </div>

      <div style={styles.plansGrid}>
        {plans.map((plan) => (
          <div
            key={plan.id}
            style={{
              ...styles.planCard,
              ...(plan.recommended ? styles.planCardRecommended : {})
            }}
          >
            {plan.recommended && (
              <div style={styles.recommendedBadge}>MOST POPULAR</div>
            )}

            <h3 style={styles.planName}>{plan.name}</h3>
            <p style={styles.planDescription}>{plan.description}</p>

            <div style={styles.priceContainer}>
              <span style={styles.priceAmount}>
                ${plan.price[selectedInterval]}
              </span>
              <span style={styles.pricePeriod}>
                {selectedInterval === 'monthly' ? '/month' : '/year'}
              </span>
            </div>

            {selectedInterval === 'yearly' && (
              <p style={styles.yearlyNote}>
                ${Math.round(plan.price.yearly / 12)}/month billed annually
              </p>
            )}

            <button
              onClick={() => handleSelectPlan(plan.id)}
              style={{
                ...styles.selectButton,
                ...(plan.recommended ? styles.selectButtonRecommended : {})
              }}
            >
              {user ? 'Upgrade Now' : 'Get Started'}
            </button>

            <div style={styles.featuresContainer}>
              {plan.features.map((feature, index) => (
                <div key={index} style={styles.feature}>
                  <span style={styles.checkmark}>✓</span>
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Enterprise section */}
      <div style={styles.enterpriseSection}>
        <h2 style={styles.enterpriseTitle}>Need more?</h2>
        <p style={styles.enterpriseDescription}>
          Organization and Enterprise plans available with volume pricing,
          EHR integration, SSO, white-label options, and dedicated support.
        </p>
        <a
          href="mailto:sales@realdiag.org"
          style={styles.enterpriseButton}
        >
          Contact Sales
        </a>
      </div>

      {/* Employee note */}
      <div style={styles.employeeNote}>
        <p style={{ margin: 0 }}>
          <strong>RealDiag Employees:</strong> Use your @realdiag.org email to register for a free account with full access.
        </p>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '40px 20px'
  },
  header: {
    textAlign: 'center',
    marginBottom: '60px'
  },
  title: {
    fontSize: '42px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '10px'
  },
  subtitle: {
    fontSize: '18px',
    color: 'rgba(255,255,255,0.9)',
    marginBottom: '30px'
  },
  toggleContainer: {
    display: 'inline-flex',
    background: 'rgba(255,255,255,0.2)',
    borderRadius: '12px',
    padding: '4px',
    gap: '4px'
  },
  toggleButton: {
    padding: '12px 24px',
    background: 'transparent',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  toggleButtonActive: {
    background: 'white',
    color: '#667eea'
  },
  saveBadge: {
    background: '#10b981',
    color: 'white',
    padding: '2px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: 'bold'
  },
  plansGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '30px',
    maxWidth: '1200px',
    margin: '0 auto 60px'
  },
  planCard: {
    background: 'white',
    borderRadius: '16px',
    padding: '40px 30px',
    position: 'relative',
    boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
    transition: 'transform 0.3s',
  },
  planCardRecommended: {
    transform: 'scale(1.05)',
    border: '3px solid #10b981',
    boxShadow: '0 20px 60px rgba(0,0,0,0.2)'
  },
  recommendedBadge: {
    position: 'absolute',
    top: '-12px',
    left: '50%',
    transform: 'translateX(-50%)',
    background: '#10b981',
    color: 'white',
    padding: '6px 16px',
    borderRadius: '20px',
    fontSize: '11px',
    fontWeight: 'bold',
    letterSpacing: '0.5px'
  },
  planName: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#1f2937'
  },
  planDescription: {
    fontSize: '14px',
    color: '#6b7280',
    marginBottom: '20px',
    minHeight: '40px'
  },
  priceContainer: {
    marginBottom: '8px'
  },
  priceAmount: {
    fontSize: '48px',
    fontWeight: 'bold',
    color: '#667eea'
  },
  pricePeriod: {
    fontSize: '18px',
    color: '#6b7280'
  },
  yearlyNote: {
    fontSize: '13px',
    color: '#10b981',
    marginBottom: '20px'
  },
  selectButton: {
    width: '100%',
    padding: '14px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    marginBottom: '30px',
    transition: 'background 0.3s'
  },
  selectButtonRecommended: {
    background: '#10b981'
  },
  featuresContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  feature: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '10px',
    fontSize: '14px',
    color: '#4b5563'
  },
  checkmark: {
    color: '#10b981',
    fontWeight: 'bold',
    fontSize: '16px'
  },
  enterpriseSection: {
    textAlign: 'center',
    maxWidth: '600px',
    margin: '0 auto 40px',
    padding: '40px',
    background: 'rgba(255,255,255,0.1)',
    borderRadius: '16px',
    backdropFilter: 'blur(10px)'
  },
  enterpriseTitle: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '16px'
  },
  enterpriseDescription: {
    fontSize: '16px',
    color: 'rgba(255,255,255,0.9)',
    marginBottom: '24px'
  },
  enterpriseButton: {
    display: 'inline-block',
    padding: '14px 32px',
    background: 'white',
    color: '#667eea',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    textDecoration: 'none',
    transition: 'transform 0.3s'
  },
  employeeNote: {
    textAlign: 'center',
    maxWidth: '600px',
    margin: '0 auto',
    padding: '20px',
    background: 'rgba(255,255,255,0.95)',
    borderRadius: '12px',
    fontSize: '14px',
    color: '#1f2937'
  }
}
