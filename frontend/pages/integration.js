"use client";
import { useState, useEffect } from "react";

export default function IntegrationPage() {
  const [apiBase, setApiBase] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    const runtimeConfig = (typeof window !== 'undefined' && window.__RUNTIME_CONFIG) ? window.__RUNTIME_CONFIG : null;
    const base = runtimeConfig?.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'https://realdiag-software.onrender.com';
    setApiBase(base.replace(/\/$/, ''));
  }, []);

  const testFHIRExport = async () => {
    if (!apiKey) {
      alert('Please enter an API key first');
      return;
    }

    try {
      const response = await fetch(`${apiBase}/integration/fhir/condition`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify({
          rule_id: 'CARD-ACS',
          patient_id: 'patient-123',
          clinical_status: 'active',
          verification_status: 'provisional'
        })
      });

      const data = await response.json();
      setTestResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setTestResult(`Error: ${error.message}`);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '2rem'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ 
          background: 'white', 
          borderRadius: '16px', 
          padding: '2rem', 
          marginBottom: '2rem',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
        }}>
          <h1 style={{ 
            margin: '0 0 0.5rem', 
            fontSize: '2.5rem', 
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            🔌 EHR Integration & API Access
          </h1>
          <p style={{ margin: 0, color: '#666', fontSize: '1.1rem' }}>
            Connect RealDiag with your Electronic Health Record system, FHIR endpoints, or custom applications
          </p>
        </div>

        {/* API Key Input */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '2rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
        }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#333' }}>
            🔑 API Key (for testing):
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your API key to test integration endpoints"
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '2px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '1rem',
              fontFamily: 'monospace'
            }}
          />
          <p style={{ margin: '0.5rem 0 0', fontSize: '0.875rem', color: '#666' }}>
            Don't have an API key? Contact your administrator or use the <code>/integration/api-keys</code> endpoint to create one.
          </p>
        </div>

        {/* Tabs */}
        <div style={{ 
          display: 'flex', 
          gap: '0.5rem', 
          marginBottom: '2rem',
          flexWrap: 'wrap'
        }}>
          {['overview', 'fhir', 'hl7', 'pdf-export', 'ehr-pull', 'cpoe', 'webhooks', 'api-keys', 'examples'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '0.75rem 1.5rem',
                background: activeTab === tab ? 'white' : 'rgba(255,255,255,0.2)',
                color: activeTab === tab ? '#667eea' : 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                textTransform: 'capitalize'
              }}
            >
              {tab === 'fhir' ? 'FHIR R4' : 
               tab === 'hl7' ? 'HL7 v2' : 
               tab === 'pdf-export' ? 'PDF Export' :
               tab === 'ehr-pull' ? 'EHR Pull' :
               tab === 'cpoe' ? 'CPOE Orders' :
               tab}
            </button>
          ))}
        </div>

        {/* Content */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
        }}>
          {activeTab === 'overview' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>Integration Overview</h2>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                RealDiag provides comprehensive integration capabilities to connect with modern and legacy healthcare systems.
              </p>

              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                gap: '1.5rem',
                marginTop: '2rem'
              }}>
                {[
                  { icon: '🏥', title: 'FHIR R4', desc: 'Modern standard for healthcare data exchange' },
                  { icon: '📨', title: 'HL7 v2', desc: 'Legacy messaging for clinical systems' },
                  { icon: '🔔', title: 'Webhooks', desc: 'Real-time event notifications' },
                  { icon: '🔐', title: 'API Keys', desc: 'Secure authentication & access control' },
                  { icon: '📤', title: 'Multi-Format Export', desc: 'JSON, XML, CSV, FHIR, HL7' },
                  { icon: '⚡', title: 'RESTful API', desc: 'Simple, standards-based integration' }
                ].map(feature => (
                  <div key={feature.title} style={{
                    padding: '1.5rem',
                    background: 'linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%)',
                    borderRadius: '12px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{feature.icon}</div>
                    <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.1rem', color: '#333' }}>{feature.title}</h3>
                    <p style={{ margin: 0, fontSize: '0.9rem', color: '#666', lineHeight: '1.6' }}>{feature.desc}</p>
                  </div>
                ))}
              </div>

              <div style={{
                marginTop: '2rem',
                padding: '1.5rem',
                background: '#fff7ed',
                borderLeft: '4px solid #f97316',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 0.5rem', color: '#c2410c' }}>🎯 Quick Start</h4>
                <ol style={{ margin: 0, paddingLeft: '1.5rem', color: '#9a3412', lineHeight: '1.8' }}>
                  <li>Create an API key using <code>/integration/api-keys</code></li>
                  <li>Include the key in request headers: <code>X-API-Key: your_key</code></li>
                  <li>Start integrating with FHIR, HL7, or webhooks</li>
                  <li>Export diagnoses in your preferred format</li>
                </ol>
              </div>
            </div>
          )}

          {activeTab === 'fhir' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>FHIR R4 Integration</h2>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                Export diagnoses as FHIR R4 Condition resources for seamless integration with modern EHR systems.
              </p>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>📍 Endpoint</h3>
              <pre style={{
                background: '#1e293b',
                color: '#e2e8f0',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.9rem'
              }}>
{`POST ${apiBase}/integration/fhir/condition
Content-Type: application/json
X-API-Key: your_api_key_here`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>📝 Request Body</h3>
              <pre style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem',
                border: '1px solid #e2e8f0'
              }}>
{`{
  "rule_id": "CARD-ACS",
  "patient_id": "patient-123",
  "encounter_id": "encounter-456",
  "clinical_status": "active",
  "verification_status": "provisional",
  "severity": "moderate",
  "onset_datetime": "2025-11-17T10:30:00Z",
  "note": "Patient presenting with chest pain"
}`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>✅ Response (FHIR Condition Resource)</h3>
              <pre style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem',
                border: '1px solid #e2e8f0',
                maxHeight: '400px'
              }}>
{`{
  "fhir_resource": {
    "resourceType": "Condition",
    "id": "realdiag-CARD-ACS-1700224800",
    "meta": {
      "profile": ["http://hl7.org/fhir/StructureDefinition/Condition"],
      "source": "RealDiag Clinical Decision Support System"
    },
    "clinicalStatus": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "active"
      }]
    },
    "code": {
      "coding": [{
        "system": "http://hl7.org/fhir/sid/icd-10-cm",
        "code": "I24.9"
      }],
      "text": "Acute coronary syndrome"
    },
    "subject": {
      "reference": "Patient/patient-123"
    }
  }
}`}
              </pre>

              <button
                onClick={testFHIRExport}
                style={{
                  marginTop: '2rem',
                  padding: '1rem 2rem',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                🧪 Test FHIR Export
              </button>

              {testResult && (
                <pre style={{
                  marginTop: '1rem',
                  background: '#1e293b',
                  color: '#e2e8f0',
                  padding: '1rem',
                  borderRadius: '8px',
                  overflow: 'auto',
                  fontSize: '0.875rem',
                  maxHeight: '400px'
                }}>
                  {testResult}
                </pre>
              )}
            </div>
          )}

          {activeTab === 'hl7' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>HL7 v2 Messaging</h2>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                Generate HL7 v2.5 messages for integration with legacy clinical information systems.
              </p>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>📍 Endpoint</h3>
              <pre style={{
                background: '#1e293b',
                color: '#e2e8f0',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.9rem'
              }}>
{`POST ${apiBase}/integration/hl7/message
Content-Type: application/json
X-API-Key: your_api_key_here`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>📝 Request Body</h3>
              <pre style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem',
                border: '1px solid #e2e8f0'
              }}>
{`{
  "message_type": "ORU",
  "rule_id": "CARD-ACS",
  "patient_id": "123456",
  "patient_name": "John Doe",
  "patient_dob": "19800515",
  "encounter_id": "ENC001",
  "ordering_provider": "Dr. Smith"
}`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>✅ Response (HL7 Message)</h3>
              <pre style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.8rem',
                border: '1px solid #e2e8f0',
                fontFamily: 'monospace'
              }}>
{`MSH|^~\\&|RealDiag|RealDiag System|EHR|Hospital|20251117103000||ORU^R01|a1b2c3d4|P|2.5
PID|1||123456||Doe^John||19800515|
PV1|1|O|||||Dr. Smith|||||||||||ENC001|
OBR|1|ENC001||DIAG^Diagnosis||20251117103000|||||||Dr. Smith|
OBX|1|CE|DIAG^Diagnosis||CARD-ACS^Acute coronary syndrome^RealDiag||||||F|||20251117103000
OBX|2|CE|ICD10^ICD-10 Code||I24.9||||||F|||20251117103000`}
              </pre>

              <div style={{
                marginTop: '2rem',
                padding: '1.5rem',
                background: '#eff6ff',
                borderLeft: '4px solid #3b82f6',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 0.5rem', color: '#1e40af' }}>💡 Supported Message Types</h4>
                <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#1e3a8a', lineHeight: '1.8' }}>
                  <li><strong>ORU^R01:</strong> Observation Result (most common)</li>
                  <li><strong>ADT:</strong> Admission/Discharge/Transfer</li>
                  <li><strong>ORM:</strong> Order Message</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'webhooks' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>Webhook Notifications</h2>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                Receive real-time notifications when diagnoses are created, updated, or searched.
              </p>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>1. Register Webhook</h3>
              <pre style={{
                background: '#1e293b',
                color: '#e2e8f0',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.9rem'
              }}>
{`POST ${apiBase}/integration/webhooks/register
Content-Type: application/json
X-API-Key: your_api_key_here

{
  "url": "https://your-server.com/webhook",
  "events": ["diagnosis.created", "diagnosis.updated"],
  "description": "Production webhook for EHR system"
}`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>2. Receive Notifications</h3>
              <p style={{ color: '#555', lineHeight: '1.8' }}>
                When subscribed events occur, RealDiag will POST to your webhook URL:
              </p>
              <pre style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem',
                border: '1px solid #e2e8f0'
              }}>
{`{
  "event": "diagnosis.created",
  "timestamp": "2025-11-17T10:30:00Z",
  "data": {
    "rule_id": "CARD-ACS",
    "label": "Acute coronary syndrome",
    "patient_id": "patient-123",
    "encounter_id": "encounter-456"
  }
}`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>3. Verify Signatures</h3>
              <p style={{ color: '#555', lineHeight: '1.8' }}>
                All webhook requests include an <code>X-Webhook-Signature</code> header for verification:
              </p>
              <pre style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem',
                border: '1px solid #e2e8f0'
              }}>
{`import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    computed = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)`}
              </pre>

              <div style={{
                marginTop: '2rem',
                padding: '1.5rem',
                background: '#fef3c7',
                borderLeft: '4px solid #f59e0b',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 0.5rem', color: '#92400e' }}>⚡ Event Types</h4>
                <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#78350f', lineHeight: '1.8' }}>
                  <li><code>diagnosis.created</code> - New diagnosis generated</li>
                  <li><code>diagnosis.updated</code> - Existing diagnosis modified</li>
                  <li><code>search.performed</code> - Symptom search executed</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'api-keys' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>API Key Management</h2>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                Create and manage API keys for secure access to integration endpoints.
              </p>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>Create API Key</h3>
              <pre style={{
                background: '#1e293b',
                color: '#e2e8f0',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.9rem'
              }}>
{`POST ${apiBase}/integration/api-keys
Content-Type: application/json

{
  "name": "Production EHR Integration",
  "scopes": ["read", "write"],
  "expires_days": 365
}`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>Response</h3>
              <pre style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem',
                border: '1px solid #e2e8f0'
              }}>
{`{
  "api_key": "rdiag_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "name": "Production EHR Integration",
  "scopes": ["read", "write"],
  "expires_at": "2026-11-17T10:30:00Z",
  "message": "API key created successfully..."
}`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>Using API Keys</h3>
              <p style={{ color: '#555', lineHeight: '1.8' }}>
                Include your API key in all integration endpoint requests:
              </p>
              <pre style={{
                background: '#f8fafc',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem',
                border: '1px solid #e2e8f0'
              }}>
{`curl -X POST ${apiBase}/integration/fhir/condition \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: rdiag_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \\
  -d '{"rule_id": "CARD-ACS", "patient_id": "123"}'`}
              </pre>

              <div style={{
                marginTop: '2rem',
                padding: '1.5rem',
                background: '#fee2e2',
                borderLeft: '4px solid #ef4444',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 0.5rem', color: '#991b1b' }}>🔒 Security Best Practices</h4>
                <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#7f1d1d', lineHeight: '1.8' }}>
                  <li>Store API keys securely (environment variables, secrets manager)</li>
                  <li>Never commit API keys to version control</li>
                  <li>Rotate keys regularly (recommended: every 90-180 days)</li>
                  <li>Use different keys for development, staging, and production</li>
                  <li>Revoke compromised keys immediately</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'pdf-export' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>📄 PDF Report Generation</h2>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                Generate professional PDF reports for diagnostic findings, workup plans, and differential diagnoses.
                Perfect for chart documentation, patient handouts, and provider communication.
              </p>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#667eea' }}>Single Diagnosis Report</h3>
                <p><strong>Endpoint:</strong> <code style={{ background: '#fff', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>POST /integration/export/pdf/diagnosis</code></p>
                
                <h4>Request Example:</h4>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: '1rem', borderRadius: '8px', overflow: 'auto', fontSize: '0.875rem' }}>
{`{
  "diagnosis_data": {
    "label": "Acute Coronary Syndrome",
    "family": "cardiology",
    "icd10": ["I21.9", "I24.9"],
    "snomed": ["394659003"],
    "presentations": ["chest pain", "dyspnea", "diaphoresis"],
    "clinical_pearls": [
      "Troponin elevation confirms diagnosis",
      "Time is muscle - early intervention critical"
    ],
    "management": [
      "Aspirin 325mg immediately",
      "Heparin anticoagulation",
      "Consider PCI vs fibrinolysis"
    ],
    "tests": ["ECG", "Troponin I/T", "CK-MB"],
    "referrals": ["Cardiology STAT"]
  },
  "patient_info": {
    "id": "MRN12345",
    "name": "John Doe",
    "dob": "1970-01-01",
    "age": 54
  },
  "clinical_context": "Presented with acute chest pain..."
}`}
                </pre>

                <h4 style={{ marginTop: '1.5rem' }}>Response:</h4>
                <p>Returns a PDF file (Content-Type: application/pdf) with comprehensive diagnostic report including:</p>
                <ul style={{ color: '#555', lineHeight: '1.8' }}>
                  <li>Patient demographics and report metadata</li>
                  <li>Clinical presentations and context</li>
                  <li>Highlighted clinical pearls in styled boxes</li>
                  <li>Management recommendations</li>
                  <li>Recommended tests and specialist referrals</li>
                  <li>ICD-10 and SNOMED CT codes</li>
                  <li>Professional disclaimer footer</li>
                </ul>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#667eea' }}>Differential Diagnosis Report</h3>
                <p><strong>Endpoint:</strong> <code style={{ background: '#fff', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>POST /integration/export/pdf/differential</code></p>
                
                <h4>Features:</h4>
                <ul style={{ color: '#555', lineHeight: '1.8' }}>
                  <li>Summary table of top 10 differential diagnoses with match scores</li>
                  <li>Detailed breakdown of top 3 diagnoses with key points</li>
                  <li>Search criteria and symptom documentation</li>
                  <li>Patient information header</li>
                  <li>Professional medical disclaimer</li>
                </ul>

                <h4>Python Example:</h4>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: '1rem', borderRadius: '8px', overflow: 'auto', fontSize: '0.875rem' }}>
{`import requests

response = requests.post(
    "${apiBase}/integration/export/pdf/diagnosis",
    headers={"X-API-Key": "your_api_key"},
    json={"diagnosis_data": {...}, "patient_info": {...}}
)

# Save PDF file
with open("diagnosis_report.pdf", "wb") as f:
    f.write(response.content)`}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'ehr-pull' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>📥 Pull Patient Data from EHR</h2>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                Retrieve comprehensive patient information from your Electronic Health Record system via FHIR API.
                Access demographics, active conditions, medications, allergies, recent vitals, and lab results.
              </p>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#fef3c7', borderRadius: '8px', border: '2px solid #f59e0b' }}>
                <h3 style={{ marginTop: 0, color: '#92400e' }}>⚙️ Configuration Required</h3>
                <p style={{ color: '#78350f' }}>
                  Before pulling patient data, you must configure your FHIR server connection using the
                  <code style={{ background: '#fff', padding: '0.25rem 0.5rem', borderRadius: '4px', margin: '0 0.25rem' }}>
                    POST /integration/ehr/fhir/configure
                  </code>
                  endpoint.
                </p>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#667eea' }}>Step 1: Configure FHIR Server</h3>
                <p><strong>Endpoint:</strong> <code style={{ background: '#fff', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>POST /integration/ehr/fhir/configure</code></p>
                
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: '1rem', borderRadius: '8px', overflow: 'auto', fontSize: '0.875rem' }}>
{`{
  "config_name": "main_ehr",
  "base_url": "https://fhir.hospital.org/api/R4",
  "auth_type": "bearer",
  "token": "eyJhbGciOiJSUzI1NiIs..."
}

// Supported auth types:
// - "none": No authentication
// - "basic": Username/password
// - "bearer": Bearer token
// - "oauth2": OAuth 2.0 (token must be obtained separately)`}
                </pre>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#667eea' }}>Step 2: Search for Patients</h3>
                <p><strong>Endpoint:</strong> <code style={{ background: '#fff', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>GET /integration/ehr/fhir/search/patients</code></p>
                
                <h4>Query Parameters:</h4>
                <ul style={{ color: '#555', lineHeight: '1.8' }}>
                  <li><code>name</code> - Patient name (e.g., "John Doe")</li>
                  <li><code>identifier</code> - Medical record number</li>
                  <li><code>birth_date</code> - Birth date (YYYY-MM-DD)</li>
                  <li><code>config_name</code> - FHIR configuration (default: "main_ehr")</li>
                </ul>

                <h4>Example:</h4>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: '1rem', borderRadius: '8px', overflow: 'auto', fontSize: '0.875rem' }}>
{`GET ${apiBase}/integration/ehr/fhir/search/patients?name=John%20Doe

Response:
{
  "patients": [
    {
      "id": "patient-12345",
      "name": "John Doe",
      "gender": "male",
      "birth_date": "1970-01-01"
    }
  ],
  "count": 1
}`}
                </pre>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#667eea' }}>Step 3: Pull Comprehensive Patient Data</h3>
                <p><strong>Endpoint:</strong> <code style={{ background: '#fff', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>GET /integration/ehr/fhir/pull/patient/&#123;patient_id&#125;</code></p>
                
                <h4>Returns:</h4>
                <ul style={{ color: '#555', lineHeight: '1.8' }}>
                  <li><strong>Demographics:</strong> Name, gender, date of birth, age</li>
                  <li><strong>Allergies:</strong> List of known allergies and intolerances</li>
                  <li><strong>Active Conditions:</strong> Current diagnoses with status</li>
                  <li><strong>Medications:</strong> Active medication orders</li>
                  <li><strong>Recent Vitals:</strong> Latest vital signs (BP, HR, temp, etc.)</li>
                  <li><strong>Recent Labs:</strong> Latest laboratory results</li>
                </ul>

                <h4>JavaScript Example:</h4>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: '1rem', borderRadius: '8px', overflow: 'auto', fontSize: '0.875rem' }}>
{`const response = await fetch(
  "${apiBase}/integration/ehr/fhir/pull/patient/patient-12345?config_name=main_ehr",
  {
    headers: { "X-API-Key": "your_api_key" }
  }
);

const patientData = await response.json();

console.log(\`Patient: \${patientData.name}, Age: \${patientData.age}\`);
console.log(\`Allergies: \${patientData.allergies.join(", ")}\`);
console.log(\`Active Conditions: \${patientData.conditions.length}\`);
console.log(\`Current Medications: \${patientData.medications.length}\`);`}
                </pre>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#ecfdf5', borderRadius: '8px', border: '2px solid #10b981' }}>
                <h3 style={{ marginTop: 0, color: '#065f46' }}>💡 Use Case: Context-Aware Diagnosis</h3>
                <p style={{ color: '#064e3b' }}>
                  Pull patient data before running diagnostic searches to get context-aware recommendations.
                  RealDiag can consider existing conditions, medications, and recent labs when suggesting diagnoses.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'cpoe' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>🏥 CPOE Integration - Order Tests & Referrals</h2>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                Seamlessly create orders in your Computerized Provider Order Entry (CPOE) system directly from RealDiag recommendations.
                Supports labs, imaging, specialist referrals, and medications via FHIR ServiceRequest resources.
              </p>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#667eea' }}>Create CPOE Order</h3>
                <p><strong>Endpoint:</strong> <code style={{ background: '#fff', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>POST /integration/cpoe/order</code></p>
                
                <h4>Supported Order Types:</h4>
                <ul style={{ color: '#555', lineHeight: '1.8' }}>
                  <li><strong>lab</strong> - Laboratory tests (CBC, CMP, troponin, etc.)</li>
                  <li><strong>imaging</strong> - Radiology orders (X-ray, CT, MRI, etc.)</li>
                  <li><strong>referral</strong> - Specialist consultations</li>
                  <li><strong>medication</strong> - Medication orders</li>
                </ul>

                <h4>Priority Levels:</h4>
                <ul style={{ color: '#555', lineHeight: '1.8' }}>
                  <li><strong>stat</strong> - Immediate/emergent (&lt; 1 hour)</li>
                  <li><strong>urgent</strong> - Urgent (within 24 hours)</li>
                  <li><strong>routine</strong> - Standard timing</li>
                </ul>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#667eea' }}>Request Example - Lab Order</h3>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: '1rem', borderRadius: '8px', overflow: 'auto', fontSize: '0.875rem' }}>
{`{
  "order_type": "lab",
  "description": "Troponin I",
  "patient_id": "patient-12345",
  "encounter_id": "visit-789",
  "priority": "stat",
  "ordering_provider": "Dr. Jane Smith",
  "clinical_indication": "Suspected acute coronary syndrome",
  "diagnosis_codes": ["I21.9", "R07.9"],
  "config_name": "main_ehr"
}`}
                </pre>

                <h4 style={{ marginTop: '1.5rem' }}>Response:</h4>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: '1rem', borderRadius: '8px', overflow: 'auto', fontSize: '0.875rem' }}>
{`{
  "message": "Order created successfully",
  "order_id": "ServiceRequest/sr-67890",
  "status": "active",
  "service_request": {
    "resourceType": "ServiceRequest",
    "id": "sr-67890",
    "status": "active",
    "intent": "order",
    "priority": "stat",
    "code": { "text": "Troponin I" },
    "subject": { "reference": "Patient/patient-12345" },
    "authoredOn": "2024-11-17T10:30:00Z"
  }
}`}
                </pre>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginTop: 0, color: '#667eea' }}>Python Example - Cardiology Referral</h3>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: '1rem', borderRadius: '8px', overflow: 'auto', fontSize: '0.875rem' }}>
{`import requests

# Create cardiology referral order
response = requests.post(
    "${apiBase}/integration/cpoe/order",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "your_api_key"
    },
    json={
        "order_type": "referral",
        "description": "Cardiology consultation - ACS workup",
        "patient_id": "patient-12345",
        "priority": "urgent",
        "ordering_provider": "Dr. Smith",
        "clinical_indication": "Troponin positive, STEMI on ECG",
        "diagnosis_codes": ["I21.02"],  # STEMI involving LAD
        "config_name": "main_ehr"
    }
)

order = response.json()
print(f"Referral created: {order['order_id']}")
print(f"Status: {order['status']}")`}
                </pre>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#ecfdf5', borderRadius: '8px', border: '2px solid #10b981' }}>
                <h3 style={{ marginTop: 0, color: '#065f46' }}>💡 Workflow Integration</h3>
                <div style={{ color: '#064e3b', lineHeight: '1.8' }}>
                  <strong>1.</strong> RealDiag suggests diagnosis (e.g., "Acute Coronary Syndrome")<br/>
                  <strong>2.</strong> Recommended tests appear (ECG, Troponin, CK-MB)<br/>
                  <strong>3.</strong> One-click order creation sends to EHR CPOE<br/>
                  <strong>4.</strong> Order automatically includes ICD-10 codes and clinical context<br/>
                  <strong>5.</strong> Track order status via FHIR ServiceRequest
                </div>
              </div>

              <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#fef3c7', borderRadius: '8px', border: '2px solid #f59e0b' }}>
                <h3 style={{ marginTop: 0, color: '#92400e' }}>⚙️ Prerequisites</h3>
                <ul style={{ color: '#78350f', lineHeight: '1.8' }}>
                  <li>FHIR server must be configured (see EHR Pull tab)</li>
                  <li>Ordering provider must have active credentials in EHR</li>
                  <li>Patient and encounter must exist in EHR system</li>
                  <li>Your FHIR server must support ServiceRequest resource creation</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'examples' && (
            <div>
              <h2 style={{ margin: '0 0 1rem', color: '#333' }}>Code Examples</h2>
              
              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>Python Example</h3>
              <pre style={{
                background: '#1e293b',
                color: '#e2e8f0',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem'
              }}>
{`import requests

API_BASE = "${apiBase}"
API_KEY = "your_api_key_here"

# Export to FHIR
response = requests.post(
    f"{API_BASE}/integration/fhir/condition",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    },
    json={
        "rule_id": "CARD-ACS",
        "patient_id": "patient-123",
        "clinical_status": "active",
        "verification_status": "provisional"
    }
)

fhir_resource = response.json()["fhir_resource"]
print(f"Created FHIR Condition: {fhir_resource['id']}")`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>JavaScript/Node.js Example</h3>
              <pre style={{
                background: '#1e293b',
                color: '#e2e8f0',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem'
              }}>
{`const API_BASE = "${apiBase}";
const API_KEY = "your_api_key_here";

// Generate HL7 message
const response = await fetch(\`\${API_BASE}/integration/hl7/message\`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    message_type: 'ORU',
    rule_id: 'CARD-ACS',
    patient_id: '123456',
    patient_name: 'John Doe'
  })
});

const { hl7_message } = await response.json();
console.log('HL7 Message:', hl7_message);`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>cURL Example</h3>
              <pre style={{
                background: '#1e293b',
                color: '#e2e8f0',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem'
              }}>
{`# Register webhook
curl -X POST ${apiBase}/integration/webhooks/register \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your_api_key_here" \\
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["diagnosis.created"],
    "description": "Production webhook"
  }'`}
              </pre>

              <h3 style={{ marginTop: '2rem', color: '#667eea' }}>C# Example</h3>
              <pre style={{
                background: '#1e293b',
                color: '#e2e8f0',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.875rem'
              }}>
{`using System.Net.Http;
using System.Text.Json;

var client = new HttpClient();
client.DefaultRequestHeaders.Add("X-API-Key", "your_api_key_here");

var request = new {
    rule_id = "CARD-ACS",
    format = "fhir",
    patient_context = new { patient_id = "patient-123" }
};

var response = await client.PostAsJsonAsync(
    "${apiBase}/integration/export",
    request
);

var result = await response.Content.ReadAsStringAsync();
Console.WriteLine(result);`}
              </pre>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          marginTop: '2rem',
          padding: '1.5rem',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '12px',
          color: 'white',
          textAlign: 'center'
        }}>
          <p style={{ margin: 0, fontSize: '0.9rem' }}>
            📚 For complete API documentation, visit <a href={`${apiBase}/docs`} style={{ color: '#fff', fontWeight: '600' }}>
              {apiBase}/docs
            </a>
          </p>
          <p style={{ margin: '0.5rem 0 0', fontSize: '0.85rem', opacity: 0.8 }}>
            Need help with integration? Contact support or check our GitHub repository.
          </p>
        </div>
      </div>
    </div>
  );
}
