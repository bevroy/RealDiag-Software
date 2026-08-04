import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function AdminReview() {
  const [pendingTrees, setPendingTrees] = useState([]);
  const [selectedTree, setSelectedTree] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [adminToken, setAdminToken] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [reviewNotes, setReviewNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [roleEmail, setRoleEmail] = useState('');
  const [roleUserId, setRoleUserId] = useState('');
  const [targetRole, setTargetRole] = useState('provider');
  const [roleReason, setRoleReason] = useState('');
  const [roleUpdating, setRoleUpdating] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://realdiag-software.onrender.com';

  // Load admin token from localStorage
  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      setAdminToken(token);
      setIsAuthenticated(true);
      loadData(token);
    } else {
      setLoading(false);
    }
  }, []);

  const loadData = async (token) => {
    setLoading(true);
    try {
      // Load pending trees
      const treesRes = await fetch(`${API_URL}/admin/trees/pending`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (treesRes.ok) {
        const treesData = await treesRes.json();
        setPendingTrees(treesData.trees || []);
      } else if (treesRes.status === 403 || treesRes.status === 401) {
        setIsAuthenticated(false);
        localStorage.removeItem('admin_token');
      }

      // Load stats
      const statsRes = await fetch(`${API_URL}/admin/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (e) => {
    e.preventDefault();
    localStorage.setItem('admin_token', adminToken);
    setIsAuthenticated(true);
    loadData(adminToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    setAdminToken('');
    setIsAuthenticated(false);
    setPendingTrees([]);
    setSelectedTree(null);
    setStats(null);
  };

  const loadTreeDetail = async (treeId) => {
    try {
      const res = await fetch(`${API_URL}/admin/trees/pending/${treeId}`, {
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setSelectedTree(data.tree);
        setReviewNotes('');
        setRejectionReason('');
      }
    } catch (error) {
      console.error('Failed to load tree:', error);
      alert('Failed to load tree details');
    }
  };

  const handleReview = async (action) => {
    if (action === 'reject' && !rejectionReason.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    try {
      const res = await fetch(`${API_URL}/admin/trees/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify({
          tree_id: selectedTree.tree_id,
          action: action,
          reviewer_notes: reviewNotes || undefined,
          rejection_reason: action === 'reject' ? rejectionReason : undefined
        })
      });

      if (res.ok) {
        const data = await res.json();
        alert(data.message);
        setSelectedTree(null);
        loadData(adminToken); // Reload data
      } else {
        const error = await res.json();
        alert(`Failed to ${action}: ${error.detail}`);
      }
    } catch (error) {
      console.error(`Failed to ${action} tree:`, error);
      alert(`Failed to ${action} tree`);
    }
  };

  const handleUpdateRoleByEmail = async (e) => {
    e.preventDefault();
    if (!roleEmail.trim()) {
      alert('Please provide an email address');
      return;
    }
    setRoleUpdating(true);
    try {
      const res = await fetch(`${API_URL}/admin/users/role/by-email`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify({
          email: roleEmail.trim().toLowerCase(),
          role: targetRole,
          reason: roleReason || undefined,
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Role update failed');
      }
      alert(`Role updated for ${data.email}: ${data.old_role || 'unset'} -> ${data.new_role}`);
    } catch (error) {
      alert(error.message || 'Failed to update role');
    } finally {
      setRoleUpdating(false);
    }
  };

  const handleUpdateRoleByUserId = async (e) => {
    e.preventDefault();
    if (!roleUserId.trim()) {
      alert('Please provide a user_id');
      return;
    }
    setRoleUpdating(true);
    try {
      const res = await fetch(`${API_URL}/admin/users/${encodeURIComponent(roleUserId.trim())}/role`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify({
          role: targetRole,
          reason: roleReason || undefined,
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Role update failed');
      }
      alert(`Role updated for ${data.user_id}: ${data.old_role || 'unset'} -> ${data.new_role}`);
    } catch (error) {
      alert(error.message || 'Failed to update role');
    } finally {
      setRoleUpdating(false);
    }
  };

  // Login form
  if (!isAuthenticated) {
    return (
      <>
        <Head>
          <title>Admin Login - RealDiag</title>
        </Head>
        <div style={styles.container}>
          <div style={styles.loginBox}>
            <h1 style={styles.title}>🔐 Admin Authentication</h1>
            <p style={styles.subtitle}>Enter admin token to access tree review system</p>
            <form onSubmit={handleLogin} style={styles.form}>
              <input
                type="password"
                value={adminToken}
                onChange={(e) => setAdminToken(e.target.value)}
                placeholder="Admin Token"
                style={styles.input}
                required
              />
              <button type="submit" style={styles.loginButton}>
                Login
              </button>
            </form>
            <div style={styles.backLink}>
              <Link href="/">← Back to Home</Link>
            </div>
          </div>
        </div>
      </>
    );
  }

  // Main admin interface
  return (
    <>
      <Head>
        <title>AI Tree Review - RealDiag Admin</title>
      </Head>
      <div style={styles.container}>
        {/* Navigation */}
        <nav style={styles.nav}>
          <div style={styles.navGrid}>
            <Link href="/" style={styles.navButton}>🏠 Home</Link>
            <Link href="/symptom-search" style={styles.navButton}>🔬 Symptom Search</Link>
            <Link href="/search" style={styles.navButton}>🔍 Diagnosis Search</Link>
            <Link href="/rules" style={styles.navButton}>📋 Browse Rules</Link>
            <Link href="/integration" style={styles.navButton}>🔌 API</Link>
            <Link href="/features-demo" style={styles.navButton}>✨ Features</Link>
            <Link href="/education" style={styles.navButton}>📚 Training</Link>
            <Link href="/sources" style={styles.navButton}>📖 Sources</Link>
            <Link href="/patient-history" style={styles.navButton}>📋 Patient History</Link>
            <Link href="/account" style={styles.navButton}>👤 Account</Link>
          </div>
        </nav>

        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>🤖 AI Decision Tree Review</h1>
          <div style={styles.headerActions}>
            <button onClick={handleLogout} style={styles.logoutButton}>
              Logout
            </button>
          </div>
        </div>

        {/* Role Management */}
        <div style={styles.roleManagerContainer}>
          <h2 style={styles.sectionTitle}>👥 Role Management</h2>
          <p style={styles.roleHelpText}>
            Promote or demote account roles using the admin API. Allowed roles: user, patient, provider, doctor, admin.
          </p>

          <div style={styles.roleFormGrid}>
            <form onSubmit={handleUpdateRoleByEmail} style={styles.roleFormBox}>
              <h3 style={styles.roleFormTitle}>Update By Email</h3>
              <input
                type="email"
                value={roleEmail}
                onChange={(e) => setRoleEmail(e.target.value)}
                placeholder="user@realdiag.com"
                style={styles.input}
              />
              <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)} style={styles.input}>
                <option value="user">user</option>
                <option value="patient">patient</option>
                <option value="provider">provider</option>
                <option value="doctor">doctor</option>
                <option value="admin">admin</option>
              </select>
              <input
                type="text"
                value={roleReason}
                onChange={(e) => setRoleReason(e.target.value)}
                placeholder="Reason (optional)"
                style={styles.input}
              />
              <button type="submit" disabled={roleUpdating} style={styles.roleActionButton}>
                {roleUpdating ? 'Updating...' : 'Update Role by Email'}
              </button>
            </form>

            <form onSubmit={handleUpdateRoleByUserId} style={styles.roleFormBox}>
              <h3 style={styles.roleFormTitle}>Update By User ID</h3>
              <input
                type="text"
                value={roleUserId}
                onChange={(e) => setRoleUserId(e.target.value)}
                placeholder="user_xxxxx"
                style={styles.input}
              />
              <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)} style={styles.input}>
                <option value="user">user</option>
                <option value="patient">patient</option>
                <option value="provider">provider</option>
                <option value="doctor">doctor</option>
                <option value="admin">admin</option>
              </select>
              <input
                type="text"
                value={roleReason}
                onChange={(e) => setRoleReason(e.target.value)}
                placeholder="Reason (optional)"
                style={styles.input}
              />
              <button type="submit" disabled={roleUpdating} style={styles.roleActionButton}>
                {roleUpdating ? 'Updating...' : 'Update Role by User ID'}
              </button>
            </form>
          </div>
        </div>

        {/* Stats Dashboard */}
        {stats && (
          <div style={styles.statsContainer}>
            <div style={styles.statCard}>
              <div style={styles.statNumber}>{stats.trees.pending}</div>
              <div style={styles.statLabel}>Pending Review</div>
            </div>
            <div style={styles.statCard}>
              <div style={styles.statNumber}>{stats.trees.approved}</div>
              <div style={styles.statLabel}>Approved</div>
            </div>
            <div style={styles.statCard}>
              <div style={styles.statNumber}>{stats.trees.rejected}</div>
              <div style={styles.statLabel}>Rejected</div>
            </div>
            <div style={styles.statCard}>
              <div style={styles.statBadge} data-enabled={stats.ai_generation.enabled}>
                {stats.ai_generation.enabled ? '✅ Enabled' : '⏸️ Disabled'}
              </div>
              <div style={styles.statLabel}>AI Generation</div>
            </div>
          </div>
        )}

        <div style={styles.mainContent}>
          {/* Tree List */}
          <div style={styles.treeList}>
            <h2 style={styles.sectionTitle}>Pending Trees ({pendingTrees.length})</h2>
            
            {loading ? (
              <div style={styles.loadingMessage}>Loading...</div>
            ) : pendingTrees.length === 0 ? (
              <div style={styles.emptyMessage}>
                No pending trees for review
              </div>
            ) : (
              <div style={styles.treeCards}>
                {pendingTrees.map((tree) => (
                  <div
                    key={tree.tree_id}
                    style={{
                      ...styles.treeCard,
                      ...(selectedTree && selectedTree.tree_id === tree.tree_id ? styles.treeCardSelected : {})
                    }}
                    onClick={() => loadTreeDetail(tree.tree_id)}
                  >
                    <div style={styles.treeCardHeader}>
                      <h3 style={styles.treeCardTitle}>{tree.name}</h3>
                      <span style={styles.urgencyBadge} data-urgency={tree.urgency}>
                        {tree.urgency || 'routine'}
                      </span>
                    </div>
                    <p style={styles.treeCardDescription}>{tree.description}</p>
                    <div style={styles.treeCardMeta}>
                      <span>🏥 {tree.specialty}</span>
                      <span>❓ {tree.question_count} questions</span>
                      <span>🧬 {tree.differential_count} differentials</span>
                    </div>
                    <div style={styles.treeCardSymptoms}>
                      <strong>Source Symptoms:</strong> {tree.source_symptoms.join(', ')}
                    </div>
                    <div style={styles.treeCardFooter}>
                      Generated {new Date(tree.generated_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Tree Detail */}
          <div style={styles.treeDetail}>
            {selectedTree ? (
              <>
                <div style={styles.detailHeader}>
                  <h2 style={styles.detailTitle}>{selectedTree.name}</h2>
                  <button
                    onClick={() => setSelectedTree(null)}
                    style={styles.closeButton}
                  >
                    ✕
                  </button>
                </div>

                <div style={styles.detailContent}>
                  {/* Basic Info */}
                  <section style={styles.section}>
                    <h3 style={styles.sectionSubtitle}>📋 Basic Information</h3>
                    <div style={styles.infoGrid}>
                      <div><strong>Tree ID:</strong> {selectedTree.tree_id}</div>
                      <div><strong>Family:</strong> {selectedTree.family}</div>
                      <div><strong>Specialty:</strong> {selectedTree.specialty}</div>
                      <div><strong>Urgency:</strong> {selectedTree.urgency}</div>
                      <div><strong>Chief Complaint:</strong> {selectedTree.chief_complaint}</div>
                      <div><strong>ICD-10:</strong> {selectedTree.icd10 || 'N/A'}</div>
                      <div><strong>SNOMED:</strong> {selectedTree.snomed?.join(', ') || 'N/A'}</div>
                    </div>
                    <p style={styles.description}>{selectedTree.description}</p>
                  </section>

                  {/* Diagnosis */}
                  {selectedTree.diagnosis && (
                    <section style={styles.section}>
                      <h3 style={styles.sectionSubtitle}>🎯 Diagnosis</h3>
                      <p><strong>{selectedTree.diagnosis.name}</strong></p>
                      <p><strong>Confidence:</strong> {(selectedTree.diagnosis.confidence * 100).toFixed(0)}%</p>
                      
                      {selectedTree.diagnosis.differential_diagnoses && (
                        <div>
                          <h4 style={styles.listTitle}>Differential Diagnoses:</h4>
                          <ul style={styles.list}>
                            {selectedTree.diagnosis.differential_diagnoses.map((dd, i) => (
                              <li key={i}>{dd}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </section>
                  )}

                  {/* Questions */}
                  {selectedTree.questions && selectedTree.questions.length > 0 && (
                    <section style={styles.section}>
                      <h3 style={styles.sectionSubtitle}>❓ Diagnostic Questions ({selectedTree.questions.length})</h3>
                      {selectedTree.questions.map((q, i) => (
                        <div key={q.id} style={styles.questionBox}>
                          <p><strong>Q{i+1}: {q.text}</strong></p>
                          <p><em>Type: {q.type}</em></p>
                          <ul style={styles.answerList}>
                            {q.answers.map((a, j) => (
                              <li key={j}>
                                {a.text} → {a.next} (weight: {a.weight || 'N/A'})
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </section>
                  )}

                  {/* Workup */}
                  {selectedTree.diagnosis?.workup && selectedTree.diagnosis.workup.length > 0 && (
                    <section style={styles.section}>
                      <h3 style={styles.sectionSubtitle}>🔬 Workup</h3>
                      {selectedTree.diagnosis.workup.map((w, i) => (
                        <div key={i} style={styles.workupBox}>
                          <p><strong>{w.test}</strong></p>
                          <p><em>Rationale:</em> {w.rationale}</p>
                          <p><em>Expected Findings:</em> {w.findings}</p>
                        </div>
                      ))}
                    </section>
                  )}

                  {/* Treatment */}
                  {selectedTree.diagnosis?.treatment && selectedTree.diagnosis.treatment.length > 0 && (
                    <section style={styles.section}>
                      <h3 style={styles.sectionSubtitle}>💊 Treatment</h3>
                      {selectedTree.diagnosis.treatment.map((t, i) => (
                        <div key={i} style={styles.treatmentBox}>
                          <p><strong>{t.intervention}</strong></p>
                          <p>{t.details}</p>
                          {t.considerations && <p><em>Considerations:</em> {t.considerations}</p>}
                        </div>
                      ))}
                    </section>
                  )}

                  {/* Clinical Pearls */}
                  {selectedTree.diagnosis?.clinical_pearls && selectedTree.diagnosis.clinical_pearls.length > 0 && (
                    <section style={styles.section}>
                      <h3 style={styles.sectionSubtitle}>💎 Clinical Pearls</h3>
                      <ul style={styles.list}>
                        {selectedTree.diagnosis.clinical_pearls.map((pearl, i) => (
                          <li key={i}>{pearl}</li>
                        ))}
                      </ul>
                    </section>
                  )}

                  {/* Red Flags */}
                  {selectedTree.diagnosis?.red_flags && selectedTree.diagnosis.red_flags.length > 0 && (
                    <section style={styles.section}>
                      <h3 style={styles.sectionSubtitle}>🚩 Red Flags</h3>
                      <ul style={styles.redFlagList}>
                        {selectedTree.diagnosis.red_flags.map((flag, i) => (
                          <li key={i}>{flag}</li>
                        ))}
                      </ul>
                    </section>
                  )}

                  {/* Review Section */}
                  <section style={styles.reviewSection}>
                    <h3 style={styles.sectionSubtitle}>📝 Review Notes (Optional)</h3>
                    <textarea
                      value={reviewNotes}
                      onChange={(e) => setReviewNotes(e.target.value)}
                      placeholder="Add any notes about this tree (visible to admin team)..."
                      style={styles.textarea}
                      rows={3}
                    />

                    <h3 style={styles.sectionSubtitle}>⚠️ Rejection Reason (Required for Rejection)</h3>
                    <textarea
                      value={rejectionReason}
                      onChange={(e) => setRejectionReason(e.target.value)}
                      placeholder="Explain why this tree is being rejected (medical accuracy issues, incomplete information, etc.)..."
                      style={styles.textarea}
                      rows={3}
                    />

                    <div style={styles.reviewActions}>
                      <button
                        onClick={() => handleReview('approve')}
                        style={styles.approveButton}
                      >
                        ✅ Approve Tree
                      </button>
                      <button
                        onClick={() => handleReview('reject')}
                        style={styles.rejectButton}
                      >
                        ❌ Reject Tree
                      </button>
                    </div>
                  </section>
                </div>
              </>
            ) : (
              <div style={styles.emptyDetail}>
                <p>Select a tree from the list to review</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '20px',
  },
  nav: {
    marginBottom: '20px',
  },
  navGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: '10px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  navButton: {
    background: 'rgba(255, 255, 255, 0.95)',
    border: '2px solid #ccfbf1',
    borderRadius: '8px',
    padding: '12px',
    fontSize: '0.9rem',
    fontWeight: '600',
    color: '#0f766e',
    textDecoration: 'none',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  loginBox: {
    maxWidth: '400px',
    margin: '100px auto',
    background: 'white',
    borderRadius: '12px',
    padding: '40px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  input: {
    padding: '12px',
    fontSize: '16px',
    border: '2px solid #e2e8f0',
    borderRadius: '8px',
  },
  loginButton: {
    background: '#667eea',
    color: 'white',
    padding: '12px 24px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  backLink: {
    marginTop: '20px',
    textAlign: 'center',
  },
  header: {
    maxWidth: '1400px',
    margin: '0 auto 30px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    background: 'white',
    borderRadius: '12px',
    padding: '20px 30px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  title: {
    fontSize: '2rem',
    fontWeight: '700',
    color: '#1e293b',
    margin: 0,
  },
  subtitle: {
    color: '#64748b',
    marginBottom: '20px',
  },
  headerActions: {
    display: 'flex',
    gap: '10px',
  },
  logoutButton: {
    background: '#ef4444',
    color: 'white',
    padding: '8px 16px',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  statsContainer: {
    maxWidth: '1400px',
    margin: '0 auto 30px',
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
  },
  roleManagerContainer: {
    maxWidth: '1400px',
    margin: '0 auto 30px',
    background: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  roleHelpText: {
    marginTop: '-8px',
    marginBottom: '16px',
    color: '#475569',
    fontSize: '0.9rem',
  },
  roleFormGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
    gap: '16px',
  },
  roleFormBox: {
    border: '1px solid #e2e8f0',
    borderRadius: '10px',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    background: '#f8fafc',
  },
  roleFormTitle: {
    margin: 0,
    fontSize: '1rem',
    color: '#1e293b',
  },
  roleActionButton: {
    background: '#2563eb',
    color: 'white',
    padding: '10px 14px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '0.9rem',
    fontWeight: '600',
    cursor: 'pointer',
  },
  statCard: {
    background: 'white',
    borderRadius: '12px',
    padding: '25px',
    textAlign: 'center',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  statNumber: {
    fontSize: '3rem',
    fontWeight: '700',
    color: '#667eea',
    marginBottom: '10px',
  },
  statLabel: {
    fontSize: '0.95rem',
    color: '#64748b',
    fontWeight: '500',
  },
  statBadge: {
    fontSize: '1.5rem',
    fontWeight: '600',
    marginBottom: '10px',
  },
  mainContent: {
    maxWidth: '1400px',
    margin: '0 auto',
    display: 'grid',
    gridTemplateColumns: '400px 1fr',
    gap: '20px',
  },
  treeList: {
    background: 'white',
    borderRadius: '12px',
    padding: '20px',
    maxHeight: 'calc(100vh - 400px)',
    overflowY: 'auto',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  sectionTitle: {
    fontSize: '1.3rem',
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: '20px',
  },
  loadingMessage: {
    textAlign: 'center',
    padding: '40px',
    color: '#64748b',
  },
  emptyMessage: {
    textAlign: 'center',
    padding: '40px',
    color: '#94a3b8',
  },
  treeCards: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  treeCard: {
    padding: '15px',
    border: '2px solid #e2e8f0',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  treeCardSelected: {
    borderColor: '#667eea',
    background: '#f8f9ff',
  },
  treeCardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'start',
    marginBottom: '10px',
  },
  treeCardTitle: {
    fontSize: '1rem',
    fontWeight: '600',
    color: '#1e293b',
    margin: 0,
  },
  urgencyBadge: {
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: '600',
    background: '#fef3c7',
    color: '#92400e',
  },
  treeCardDescription: {
    fontSize: '0.85rem',
    color: '#64748b',
    marginBottom: '10px',
  },
  treeCardMeta: {
    display: 'flex',
    gap: '15px',
    fontSize: '0.8rem',
    color: '#64748b',
    marginBottom: '10px',
  },
  treeCardSymptoms: {
    fontSize: '0.8rem',
    color: '#475569',
    marginBottom: '10px',
  },
  treeCardFooter: {
    fontSize: '0.75rem',
    color: '#94a3b8',
    marginTop: '10px',
    paddingTop: '10px',
    borderTop: '1px solid #e2e8f0',
  },
  treeDetail: {
    background: 'white',
    borderRadius: '12px',
    padding: '20px',
    maxHeight: 'calc(100vh - 400px)',
    overflowY: 'auto',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  detailHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    paddingBottom: '15px',
    borderBottom: '2px solid #e2e8f0',
  },
  detailTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#1e293b',
    margin: 0,
  },
  closeButton: {
    background: '#f1f5f9',
    border: 'none',
    borderRadius: '6px',
    padding: '8px 12px',
    fontSize: '1.2rem',
    cursor: 'pointer',
    color: '#64748b',
  },
  detailContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '25px',
  },
  section: {
    paddingBottom: '20px',
    borderBottom: '1px solid #e2e8f0',
  },
  sectionSubtitle: {
    fontSize: '1.1rem',
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: '15px',
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '12px',
    fontSize: '0.9rem',
    marginBottom: '15px',
  },
  description: {
    fontSize: '0.95rem',
    color: '#475569',
    lineHeight: '1.6',
  },
  listTitle: {
    fontSize: '0.95rem',
    fontWeight: '600',
    color: '#475569',
    marginTop: '15px',
    marginBottom: '8px',
  },
  list: {
    paddingLeft: '20px',
    marginTop: '10px',
    fontSize: '0.9rem',
    color: '#475569',
    lineHeight: '1.8',
  },
  redFlagList: {
    paddingLeft: '20px',
    marginTop: '10px',
    fontSize: '0.9rem',
    color: '#dc2626',
    lineHeight: '1.8',
    fontWeight: '500',
  },
  questionBox: {
    background: '#f8fafc',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '12px',
    border: '1px solid #e2e8f0',
  },
  answerList: {
    paddingLeft: '20px',
    marginTop: '8px',
    fontSize: '0.85rem',
    color: '#64748b',
  },
  workupBox: {
    background: '#f0fdf4',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '12px',
    border: '1px solid #bbf7d0',
  },
  treatmentBox: {
    background: '#fef3c7',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '12px',
    border: '1px solid #fde68a',
  },
  reviewSection: {
    background: '#f8fafc',
    padding: '20px',
    borderRadius: '12px',
    border: '2px solid #e2e8f0',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    fontSize: '0.9rem',
    border: '2px solid #e2e8f0',
    borderRadius: '8px',
    marginBottom: '15px',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  reviewActions: {
    display: 'flex',
    gap: '15px',
    marginTop: '20px',
  },
  approveButton: {
    flex: 1,
    background: '#10b981',
    color: 'white',
    padding: '14px 24px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
  },
  rejectButton: {
    flex: 1,
    background: '#ef4444',
    color: 'white',
    padding: '14px 24px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
  },
  emptyDetail: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '400px',
    color: '#94a3b8',
    fontSize: '1.1rem',
  },
};
