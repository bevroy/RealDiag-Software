import React, { useState, useEffect } from 'react'
import styles from './PatientContext.module.css'

/**
 * PatientContext Component
 * 
 * Collapsible panel for collecting patient context modifiers:
 * - Diet, supplements, travel, exposures, etc.
 * - All inputs are optional (opt-in)
 * - No inference from demographics
 * - Context summary chips displayed when active
 */
export default function PatientContext({ value, onChange, apiBase }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [variables, setVariables] = useState([])
  const [categories, setCategories] = useState([])
  const [contextData, setContextData] = useState(value || {})
  const [summary, setSummary] = useState([])
  const [loading, setLoading] = useState(false)

  // Load context variables from API
  useEffect(() => {
    if (!apiBase) return

    const loadVariables = async () => {
      try {
        const response = await fetch(`${apiBase}/context/variables`)
        const data = await response.json()
        setVariables(data.variables || [])
        setCategories(data.categories || [])
      } catch (err) {
        console.error('Failed to load context variables:', err)
      }
    }

    loadVariables()
  }, [apiBase])

  // Update summary when context data changes
  useEffect(() => {
    if (!apiBase || Object.keys(contextData).length === 0) {
      setSummary([])
      return
    }

    const updateSummary = async () => {
      try {
        const response = await fetch(`${apiBase}/context/summary`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(contextData)
        })
        const data = await response.json()
        setSummary(data.summary || [])
      } catch (err) {
        console.error('Failed to generate context summary:', err)
      }
    }

    updateSummary()
  }, [contextData, apiBase])

  const handleChange = (variableId, newValue) => {
    const updated = { ...contextData, [variableId]: newValue }
    setContextData(updated)
    if (onChange) {
      onChange(updated)
    }
  }

  const handleClear = () => {
    setContextData({})
    setSummary([])
    if (onChange) {
      onChange({})
    }
  }

  const renderInput = (variable) => {
    const currentValue = contextData[variable.id]

    switch (variable.type) {
      case 'boolean':
        return (
          <div className={styles.checkboxWrapper}>
            <input
              type="checkbox"
              id={variable.id}
              checked={currentValue || false}
              onChange={(e) => handleChange(variable.id, e.target.checked)}
              className={styles.checkbox}
            />
            <label htmlFor={variable.id} className={styles.checkboxLabel}>
              {variable.label}
            </label>
          </div>
        )

      case 'numeric':
        return (
          <div className={styles.inputWrapper}>
            <label htmlFor={variable.id} className={styles.label}>
              {variable.label}
            </label>
            <div className={styles.numericInput}>
              <input
                type="number"
                id={variable.id}
                value={currentValue || ''}
                onChange={(e) => handleChange(variable.id, parseFloat(e.target.value) || 0)}
                className={styles.input}
                min="0"
                step="1"
              />
              {variable.units && <span className={styles.units}>{variable.units}</span>}
            </div>
          </div>
        )

      case 'single_select':
        return (
          <div className={styles.inputWrapper}>
            <label htmlFor={variable.id} className={styles.label}>
              {variable.label}
            </label>
            <select
              id={variable.id}
              value={currentValue || ''}
              onChange={(e) => handleChange(variable.id, e.target.value)}
              className={styles.select}
            >
              <option value="">-- Select --</option>
              {variable.options?.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        )

      case 'multi_select':
        const selectedValues = currentValue || []
        return (
          <div className={styles.inputWrapper}>
            <label className={styles.label}>{variable.label}</label>
            <div className={styles.multiSelectWrapper}>
              {variable.options?.map((opt) => (
                <div key={opt.value} className={styles.checkboxWrapper}>
                  <input
                    type="checkbox"
                    id={`${variable.id}_${opt.value}`}
                    checked={selectedValues.includes(opt.value)}
                    onChange={(e) => {
                      const newValues = e.target.checked
                        ? [...selectedValues, opt.value]
                        : selectedValues.filter((v) => v !== opt.value)
                      handleChange(variable.id, newValues)
                    }}
                    className={styles.checkbox}
                  />
                  <label htmlFor={`${variable.id}_${opt.value}`} className={styles.checkboxLabel}>
                    {opt.label}
                  </label>
                </div>
              ))}
            </div>
          </div>
        )

      case 'text':
        return (
          <div className={styles.inputWrapper}>
            <label htmlFor={variable.id} className={styles.label}>
              {variable.label}
            </label>
            <input
              type="text"
              id={variable.id}
              value={currentValue || ''}
              onChange={(e) => handleChange(variable.id, e.target.value)}
              className={styles.input}
              placeholder="Optional"
            />
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className={styles.contextPanel}>
      {/* Header with toggle */}
      <div className={styles.header} onClick={() => setIsExpanded(!isExpanded)}>
        <div className={styles.headerLeft}>
          <svg className={`${styles.icon} ${isExpanded ? styles.iconExpanded : ''}`} width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="2" fill="none" />
          </svg>
          <h3 className={styles.title}>Patient Context</h3>
          <span className={styles.badge}>Optional</span>
        </div>
        <div className={styles.headerRight}>
          {summary.length > 0 && (
            <span className={styles.activeCount}>{summary.length} active</span>
          )}
        </div>
      </div>

      {/* Context summary chips */}
      {summary.length > 0 && !isExpanded && (
        <div className={styles.summaryChips}>
          {summary.map((item, idx) => (
            <span key={idx} className={styles.chip}>
              {item}
            </span>
          ))}
        </div>
      )}

      {/* Expanded form */}
      {isExpanded && (
        <div className={styles.content}>
          {/* Disclaimer banner */}
          <div className={styles.disclaimer}>
            <svg className={styles.disclaimerIcon} width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <strong>Informational Tool:</strong> This tool provides information based on patient-reported 
              exposures and lifestyle factors. It does not replace clinical judgment. All suggestions are 
              guideline-based considerations, not prescriptive recommendations.
            </div>
          </div>

          {/* Instructions */}
          <p className={styles.instructions}>
            Enter exposure and lifestyle information below. These optional details help identify relevant 
            considerations for diagnosis and management. All information is based solely on what you enter 
            — no assumptions are made from demographics or other data.
          </p>

          {/* Variables grouped by category */}
          {categories.map((category) => {
            const categoryVars = variables.filter((v) => v.category === category)
            if (categoryVars.length === 0) return null

            return (
              <div key={category} className={styles.category}>
                <h4 className={styles.categoryTitle}>{category}</h4>
                <div className={styles.variablesGrid}>
                  {categoryVars.map((variable) => (
                    <div key={variable.id} className={styles.variableItem}>
                      {renderInput(variable)}
                      {variable.help_text && (
                        <p className={styles.helpText}>{variable.help_text}</p>
                      )}
                      {variable.evidence_level && (
                        <span className={styles.evidenceLevel}>
                          Evidence: {variable.evidence_level}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )
          })}

          {/* Actions */}
          <div className={styles.actions}>
            <button
              type="button"
              onClick={handleClear}
              className={styles.clearButton}
              disabled={Object.keys(contextData).length === 0}
            >
              Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
