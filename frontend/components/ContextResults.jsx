import React, { useState } from 'react'
import styles from './ContextResults.module.css'

/**
 * ContextResults Component
 * 
 * Displays context-based modifications to diagnostic results:
 * - Additional differential diagnoses
 * - Additional questions to ask
 * - Additional workup suggestions
 * - Red flags and urgency adjustments
 * - Referral notes
 * - Detailed reasoning with evidence levels and citations
 */
export default function ContextResults({ contextData }) {
  const [showRationale, setShowRationale] = useState(false)

  if (!contextData || !contextData.has_context) {
    return null
  }

  const {
    context_applied,
    context_differential,
    context_questions,
    context_workup,
    context_red_flags,
    context_referral_notes,
    urgency_adjustment,
    reasoning,
    disclaimer
  } = contextData

  return (
    <div className={styles.contextResults}>
      {/* Header */}
      <div className={styles.header}>
        <h3 className={styles.title}>
          <svg className={styles.icon} width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Context-Based Considerations
        </h3>
        <button
          className={styles.rationaleToggle}
          onClick={() => setShowRationale(!showRationale)}
        >
          {showRationale ? 'Hide' : 'Show'} Rationale & References
        </button>
      </div>

      {/* Disclaimer */}
      <div className={styles.disclaimer}>
        <strong>⚠️ Information Only:</strong> {disclaimer}
      </div>

      {/* Applied rules summary */}
      {context_applied && context_applied.length > 0 && (
        <div className={styles.appliedRules}>
          <h4 className={styles.sectionTitle}>
            Applied Rules ({context_applied.length})
          </h4>
          {context_applied.map((rule, idx) => (
            <div key={idx} className={styles.ruleCard}>
              <div className={styles.ruleName}>
                {rule.rule_name}
                {rule.evidence_level && (
                  <span className={`${styles.evidenceBadge} ${styles[`evidence${rule.evidence_level}`]}`}>
                    Evidence: {rule.evidence_level}
                  </span>
                )}
              </div>
              <div className={styles.ruleMatches}>
                Triggered by: {rule.matched_triggers.join(', ')}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Urgency adjustment */}
      {urgency_adjustment && (
        <div className={styles.urgencyAlert}>
          <svg className={styles.alertIcon} width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div>
            <strong>Urgency Adjustment:</strong> {urgency_adjustment.replace(/_/g, ' ')}
          </div>
        </div>
      )}

      {/* Additional differential */}
      {context_differential && context_differential.length > 0 && (
        <div className={styles.section}>
          <h4 className={styles.sectionTitle}>
            <svg className={styles.sectionIcon} width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M9 2a1 1 0 000 2h2.586L7 8.586 4.707 6.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0L12 6.414V9a1 1 0 102 0V3a1 1 0 00-1-1H9z" />
            </svg>
            Additional Differential Diagnoses to Consider
          </h4>
          <ul className={styles.list}>
            {context_differential.map((dx, idx) => (
              <li key={idx} className={styles.listItem}>
                <span className={styles.considerPrefix}>Consider:</span> {dx}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Additional questions */}
      {context_questions && context_questions.length > 0 && (
        <div className={styles.section}>
          <h4 className={styles.sectionTitle}>
            <svg className={styles.sectionIcon} width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            Additional History Questions to Ask
          </h4>
          <ul className={styles.list}>
            {context_questions.map((question, idx) => (
              <li key={idx} className={styles.listItem}>
                <span className={styles.askPrefix}>Ask about:</span> {question}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Additional workup */}
      {context_workup && context_workup.length > 0 && (
        <div className={styles.section}>
          <h4 className={styles.sectionTitle}>
            <svg className={styles.sectionIcon} width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path fillRule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V3zm2 0v12h10V3H5z" clipRule="evenodd" />
            </svg>
            Additional Workup Suggestions
          </h4>
          <ul className={styles.list}>
            {context_workup.map((test, idx) => (
              <li key={idx} className={styles.listItem}>
                <span className={styles.considerPrefix}>Consider:</span> {test}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Red flags */}
      {context_red_flags && context_red_flags.length > 0 && (
        <div className={`${styles.section} ${styles.redFlagsSection}`}>
          <h4 className={styles.sectionTitle}>
            <svg className={styles.sectionIcon} width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Additional Red Flags / Warning Signs
          </h4>
          <ul className={styles.list}>
            {context_red_flags.map((flag, idx) => (
              <li key={idx} className={styles.redFlagItem}>
                🚩 {flag}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Referral notes */}
      {context_referral_notes && context_referral_notes.length > 0 && (
        <div className={styles.section}>
          <h4 className={styles.sectionTitle}>
            <svg className={styles.sectionIcon} width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6z" />
            </svg>
            Referral & Consultation Guidance
          </h4>
          <ul className={styles.list}>
            {context_referral_notes.map((note, idx) => (
              <li key={idx} className={styles.listItem}>
                {note}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Detailed reasoning */}
      {showRationale && reasoning && reasoning.length > 0 && (
        <div className={styles.rationaleSection}>
          <h4 className={styles.sectionTitle}>
            <svg className={styles.sectionIcon} width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
            </svg>
            Clinical Rationale & Evidence
          </h4>
          {reasoning.map((item, idx) => (
            <div key={idx} className={styles.rationaleCard}>
              <div className={styles.rationaleHeader}>
                <strong>{item.rule}</strong>
                {item.evidence_level && (
                  <span className={`${styles.evidenceBadge} ${styles[`evidence${item.evidence_level}`]}`}>
                    {item.evidence_level} Evidence
                  </span>
                )}
              </div>
              <div className={styles.rationaleText}>{item.explanation}</div>
              
              {/* Clinical pearls */}
              {item.clinical_pearls && item.clinical_pearls.length > 0 && (
                <div className={styles.pearls}>
                  <div className={styles.pearlsTitle}>💎 Clinical Pearls:</div>
                  <ul className={styles.pearlsList}>
                    {item.clinical_pearls.map((pearl, pIdx) => (
                      <li key={pIdx}>{pearl}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* References */}
              {item.references && item.references.length > 0 && (
                <div className={styles.references}>
                  <div className={styles.referencesTitle}>📚 References:</div>
                  <ul className={styles.referencesList}>
                    {item.references.map((ref, rIdx) => (
                      <li key={rIdx}>
                        <strong>{ref.title}</strong> ({ref.organization}, {ref.year})
                        {ref.url_or_citation && (
                          <div className={styles.citation}>{ref.url_or_citation}</div>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
