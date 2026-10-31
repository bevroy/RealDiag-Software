import { useState } from 'react';
import { ClinicalReviewNotice, ReviewStatusBadge } from './ClinicalReview';
import { walkQuestionnaire, walkEndMessage } from '../utils/questionnaireWalker';

// One question at a time through a questionnaire tree, then its outcome step.
// Content is shown as written in the tree; nothing is ranked or chosen for the
// clinician. A step's ICD-10 and urgency are display only.
export default function QuestionnaireWalk({ questionnaire, onClose }) {
  const [answers, setAnswers] = useState([]);
  const walk = walkQuestionnaire(questionnaire, answers);
  const tree = questionnaire.tree || {};
  const endMessage = walkEndMessage(walk);

  return (
    <section style={styles.card} aria-live="polite">
      <div style={styles.header}>
        <h2 style={{ margin: 0 }}>{tree.title || tree.id}</h2>
        <ReviewStatusBadge status={tree.review_status} label={tree.review_status_label} />
      </div>
      <ClinicalReviewNotice notice={questionnaire.clinical_review_notice} />

      {walk.path.length > 0 && (
        <ol style={styles.path}>
          {walk.path.map((step, i) => (
            <li key={i}><span style={styles.muted}>{step.question}</span> <strong>{step.answer}</strong></li>
          ))}
        </ol>
      )}

      {walk.current && (
        <div>
          <h3>{walk.current.text}</h3>
          <div style={styles.options}>
            {walk.current.options.map((option, i) => (
              <button key={i} style={styles.option} onClick={() => setAnswers([...answers, i])}>{option.label}</button>
            ))}
          </div>
        </div>
      )}

      {walk.outcome && (
        <div style={styles.outcome}>
          <h3 style={{ marginTop: 0 }}>{walk.outcome.title}</h3>
          {walk.outcome.description && <p>{walk.outcome.description}</p>}
          <List title="Workup listed in the tree" items={walk.outcome.workup} />
          <List title="Treatment information from the tree (reference, not an order)" items={walk.outcome.treatment} />
          <List title="Recommendations listed in the tree" items={walk.outcome.recommendations} />
          {(walk.outcome.icd10.length > 0 || walk.outcome.urgency) && (
            <p style={styles.muted}>
              {walk.outcome.icd10.length > 0 && <>ICD-10 (as written): {walk.outcome.icd10.join(', ')}. </>}
              {walk.outcome.urgency && <>Step urgency (as written): {walk.outcome.urgency}. </>}
              {questionnaire.step_values_note}
            </p>
          )}
        </div>
      )}

      {endMessage && <div role="status" style={styles.note}>{endMessage}</div>}

      <div style={styles.actions}>
        {answers.length > 0 && <button style={styles.secondary} onClick={() => setAnswers(answers.slice(0, -1))}>← Back</button>}
        {answers.length > 0 && <button style={styles.secondary} onClick={() => setAnswers([])}>Start over</button>}
        <button style={styles.secondary} onClick={onClose}>Choose another tree</button>
      </div>
    </section>
  );
}

function List({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h4 style={{ marginBottom: '0.25rem' }}>{title}:</h4>
      <ul style={{ marginTop: 0 }}>{items.map((item, i) => <li key={i}>{item}</li>)}</ul>
    </div>
  );
}

const styles = {
  card: { maxWidth: '800px', margin: '0 auto 2rem', background: 'white', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
  header: { display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '0.75rem' },
  path: { color: '#374151', fontSize: '0.9rem', paddingLeft: '1.25rem' },
  options: { display: 'flex', flexDirection: 'column', gap: '0.5rem' },
  option: { textAlign: 'left', padding: '0.75rem 1rem', border: '1px solid #3b82f6', borderRadius: '6px', background: '#eff6ff', color: '#1e3a8a', cursor: 'pointer', fontSize: '0.95rem' },
  outcome: { borderLeft: '4px solid #0f766e', padding: '0.5rem 1rem', background: '#f9fafb', borderRadius: '6px' },
  note: { padding: '0.75rem 1rem', margin: '1rem 0', background: '#eff6ff', border: '1px solid #3b82f6', borderRadius: '8px', color: '#1e3a8a' },
  actions: { display: 'flex', gap: '0.5rem', marginTop: '1rem', flexWrap: 'wrap' },
  secondary: { padding: '0.5rem 1rem', border: '1px solid #d1d5db', borderRadius: '6px', background: 'white', cursor: 'pointer' },
  muted: { color: '#6b7280', fontSize: '0.85rem' },
};
