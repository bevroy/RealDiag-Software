/**
 * Task 6.1: Accessibility Helper Components
 * WCAG 2.1 AA Compliant Elements
 */

import React from 'react';

// Skip Link Component
export const SkipLink = ({ targetId = "main-content", children = "Skip to main content" }) => {
  const [isVisible, setIsVisible] = React.useState(false);

  return (
    <a
      href={`#${targetId}`}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
      style={{
        position: isVisible ? 'fixed' : 'absolute',
        left: isVisible ? '10px' : '-9999px',
        top: isVisible ? '10px' : 'auto',
        zIndex: 9999,
        padding: '1rem 1.5rem',
        background: '#3b82f6',
        color: 'white',
        textDecoration: 'none',
        borderRadius: '6px',
        fontWeight: '600',
        boxShadow: '0 4px 6px rgba(0,0,0,0.2)',
        transition: 'all 0.2s'
      }}
    >
      {children}
    </a>
  );
};

// Accessible Button with proper ARIA
export const AccessibleButton = ({ 
  children, 
  onClick, 
  ariaLabel, 
  ariaPressed, 
  ariaExpanded,
  ariaControls,
  disabled = false,
  ...props 
}) => {
  return (
    <button
      onClick={onClick}
      aria-label={ariaLabel}
      aria-pressed={ariaPressed}
      aria-expanded={ariaExpanded}
      aria-controls={ariaControls}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

// Visually Hidden Text (for screen readers)
export const VisuallyHidden = ({ children }) => {
  return (
    <span style={{
      position: 'absolute',
      left: '-10000px',
      width: '1px',
      height: '1px',
      overflow: 'hidden'
    }}>
      {children}
    </span>
  );
};

// Accessible Form Label
export const AccessibleLabel = ({ htmlFor, required, children, ...props }) => {
  return (
    <label htmlFor={htmlFor} {...props}>
      {children}
      {required && <span aria-label="required" style={{ color: '#ef4444', marginLeft: '0.25rem' }}>*</span>}
    </label>
  );
};

// Live Region for Announcements
export const LiveRegion = ({ children, assertive = false, ...props }) => {
  return (
    <div
      role="status"
      aria-live={assertive ? "assertive" : "polite"}
      aria-atomic="true"
      {...props}
    >
      {children}
    </div>
  );
};

// Keyboard Navigation Hook
export const useKeyboardNavigation = (onEscape, dependencies = []) => {
  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && onEscape) {
        onEscape();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, dependencies);
};

// Focus Trap for Modals
export const useFocusTrap = (ref, isActive) => {
  React.useEffect(() => {
    if (!isActive || !ref.current) return;

    const focusableElements = ref.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };

    firstElement?.focus();
    document.addEventListener('keydown', handleTabKey);
    return () => document.removeEventListener('keydown', handleTabKey);
  }, [isActive, ref]);
};

export default {
  SkipLink,
  AccessibleButton,
  VisuallyHidden,
  AccessibleLabel,
  LiveRegion,
  useKeyboardNavigation,
  useFocusTrap
};
