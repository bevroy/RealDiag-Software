# Legal Disclaimer & Terms of Use

## ⚖️ IMPORTANT LEGAL NOTICE

**PLEASE READ CAREFULLY BEFORE USING THIS SOFTWARE**

---

## 🚨 Medical Disclaimer

### NOT FOR CLINICAL USE

**RealDiag-Software is provided for EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY.**

This software:
- ❌ **Is NOT FDA-approved, cleared, or authorized** for medical use
- ❌ **Is NOT a medical device** under FDA regulations
- ❌ **Is NOT intended for diagnosis, treatment, cure, or prevention** of any disease
- ❌ **Is NOT a substitute for professional medical advice, diagnosis, or treatment**
- ❌ **Should NOT be used for clinical decision-making** without physician oversight

### Healthcare Professional Responsibility

If you are a healthcare professional using this software:

1. **Professional Judgment Required**: This tool provides suggestions only. Always apply your professional judgment and clinical expertise.

2. **Verify All Information**: Do not rely solely on software recommendations. Verify all diagnostic suggestions against current medical literature and clinical guidelines.

3. **Patient Safety First**: This software has not been validated for clinical accuracy. Use only as a supplemental educational reference.

4. **Liability**: You assume full responsibility for any clinical decisions made, whether or not informed by this software.

### Patient Notice

If you are a patient or non-healthcare professional:

**SEEK PROFESSIONAL MEDICAL ADVICE**
- Always consult a qualified healthcare provider for medical concerns
- Call 911 or go to the emergency room for urgent medical issues
- Do not delay seeking medical care based on information from this software
- This software cannot provide personalized medical advice

**National Suicide Prevention Lifeline:** 988  
**Emergency Services:** 911 (US) or your local emergency number

---

## 📜 Copyright & Licensing

### Software License

**MIT License**

Copyright (c) 2025 RealDiag-Software Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**

### Medical Knowledge Attribution

The diagnostic rules, clinical guidelines, and medical knowledge contained in this software are compiled from:

1. **Public Medical Literature**: Evidence-based guidelines from peer-reviewed medical journals
2. **Clinical Practice Guidelines**: Publicly available guidelines from medical societies
3. **Educational Resources**: Medical textbooks and educational materials

**Sources Referenced:**
- American Heart Association (AHA)
- American College of Cardiology (ACC)
- American Academy of Neurology (AAN)
- Centers for Disease Control and Prevention (CDC)
- National Institutes of Health (NIH)
- World Health Organization (WHO)
- UpToDate® (referenced, not copied)
- Various peer-reviewed medical journals

**Important Notes:**
- Medical knowledge changes rapidly; guidelines may become outdated
- This software does not replace subscribing to professional medical references
- Clinical guidelines are adapted for software use and may differ from original sources
- Users should always refer to primary sources for detailed guidance

### Third-Party Dependencies

This software uses open-source libraries and frameworks:

**Frontend:**
- Next.js (MIT License)
- React (MIT License)
- Web Speech API (W3C Standard)
- BarcodeDetector API (W3C Standard)

**Backend:**
- FastAPI (MIT License)
- Python standard libraries (PSF License)

See `package.json` and `requirements.txt` for complete dependency lists.

### Code Examples & Drug Information

**Drug Information:**
- Drug names, interactions, and dosing information compiled from FDA-approved labels and published medical literature
- Not comprehensive; always check official prescribing information
- Drug information may be outdated; verify current guidelines

**Clinical Calculators:**
- Wells Score, PERC Rule, HEART Score, etc. are publicly available clinical tools
- Formulas based on published medical literature
- Not proprietary; widely used in medical education

---

## 🛡️ Limitation of Liability

### No Warranty

THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. THE AUTHORS AND CONTRIBUTORS:

1. **Make no representations** about the accuracy, reliability, completeness, or timeliness of the information
2. **Do not guarantee** that the software will be error-free or uninterrupted
3. **Do not warrant** that defects will be corrected
4. **Make no guarantees** about diagnostic accuracy or clinical outcomes

### Limitation of Damages

**TO THE MAXIMUM EXTENT PERMITTED BY LAW:**

The authors, contributors, and distributors of this software shall NOT be liable for:

- ❌ Direct, indirect, incidental, special, or consequential damages
- ❌ Loss of profits, revenue, data, or use
- ❌ Personal injury or death
- ❌ Medical malpractice claims
- ❌ Errors in diagnosis or treatment
- ❌ Any damages arising from use or inability to use the software

**EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.**

### Indemnification

By using this software, you agree to indemnify, defend, and hold harmless the authors, contributors, and distributors from any claims, damages, losses, liabilities, and expenses (including attorney fees) arising from:

1. Your use or misuse of the software
2. Your violation of these terms
3. Your violation of any third-party rights
4. Any clinical decisions made based on software recommendations

---

## 🏥 HIPAA & Privacy

### Current Status: NOT HIPAA COMPLIANT

**This software is currently NOT compliant with HIPAA regulations.**

### Data Collection & Storage

**What we collect:**
- Symptoms entered by users
- Search history (optional, stored locally)
- User preferences (theme, font size, etc.)
- Scanned patient IDs (stored temporarily in memory only)

**What we do NOT collect:**
- Patient names
- Medical record numbers (unless scanned, then stored temporarily)
- Social Security numbers
- Insurance information
- Full medical records

**Storage:**
- Data stored locally in browser (IndexedDB, localStorage)
- No server-side storage of PHI in current version
- Offline mode stores diagnostic rules only (no patient data)

### User Responsibility

If you choose to use this software with patient data:

1. **You are responsible** for HIPAA compliance
2. **You must obtain** appropriate patient consent
3. **You must ensure** secure data handling
4. **You must implement** Business Associate Agreements (if applicable)
5. **You assume all risk** of data breaches

### Data Security

**Current Security Measures:**
- HTTPS encryption in transit
- No persistent server-side storage of PHI
- Client-side encryption not implemented

**Known Vulnerabilities:**
- IndexedDB data not encrypted
- LocalStorage accessible via browser DevTools
- No automatic data expiration

**See SECURITY.md for complete security information.**

---

## 🌍 Geographic & Regulatory Restrictions

### United States

**FDA Regulations:**
- This software has NOT been submitted to the FDA
- Not classified as a medical device
- Not cleared for clinical use under 510(k) or PMA
- May be subject to FDA enforcement action if used clinically

**Intended Use:**
- Educational tool for healthcare professionals
- Reference guide for medical students
- Demonstration of clinical decision support systems

### European Union

**MDR Compliance:**
- Not CE marked
- Not certified under EU Medical Device Regulation (MDR 2017/745)
- Not intended for use in EU healthcare settings

### Other Jurisdictions

This software may be subject to medical device regulations in your jurisdiction. Users are responsible for:
- Determining if use is permitted under local law
- Obtaining necessary approvals or clearances
- Complying with local healthcare regulations

---

## 📊 Clinical Validation & Evidence

### Validation Status: NOT VALIDATED

**This software has NOT undergone:**
- ❌ Clinical trials
- ❌ Peer review for clinical use
- ❌ Validation studies
- ❌ Sensitivity/specificity testing
- ❌ Real-world effectiveness evaluation
- ❌ Comparison against physician diagnosis

### Evidence Base

The diagnostic rules are based on:
- Published medical literature (as available up to 2025)
- Clinical practice guidelines
- Expert consensus recommendations

**However:**
- Medical knowledge evolves rapidly
- Guidelines change frequently
- Individual patient circumstances vary
- Software logic may not capture clinical nuance

### Accuracy Limitations

**Known limitations:**
- Simplified decision trees may miss complex cases
- No integration with patient medical history
- Cannot account for physical examination findings
- Cannot replace laboratory or imaging interpretation
- May not include rare or emerging conditions

---

## ⚕️ Professional Use Guidelines

### For Healthcare Professionals

**Acceptable Use:**
✅ Educational reference
✅ Quick clinical pearls lookup
✅ Differential diagnosis brainstorming
✅ Teaching tool for medical students
✅ Personal learning aid

**Prohibited Use:**
❌ Sole basis for clinical decisions
❌ Replacement for clinical judgment
❌ Documentation in medical records as "computer diagnosis"
❌ Billing based on software recommendations
❌ Use in emergency situations without verification

### Standard of Care

Using this software does NOT constitute:
- Meeting the standard of care
- Following clinical practice guidelines
- Adequate patient assessment
- Complete differential diagnosis

### Documentation

If you reference this software in clinical practice:
- Document it as "educational reference consulted"
- Note that clinical decision was independently verified
- Include primary sources for any diagnostic reasoning
- Never document as "computer-generated diagnosis"

---

## 🔒 Terms of Service

### Acceptance of Terms

By accessing or using RealDiag-Software, you agree to be bound by these terms. If you do not agree, do not use the software.

### Modifications

We reserve the right to modify these terms at any time. Continued use after changes constitutes acceptance.

### Termination

We may terminate or suspend access to the software at any time, without notice, for any reason.

### Governing Law

These terms are governed by the laws of [Your Jurisdiction], without regard to conflict of law provisions.

### Dispute Resolution

Any disputes shall be resolved through binding arbitration in [Your Jurisdiction].

### Severability

If any provision is found unenforceable, the remaining provisions remain in effect.

---

## 📞 Contact Information

**For Legal Inquiries:**
- Email: legal@realdiag.com
- GitHub: https://github.com/bevroy/RealDiag-Software/issues

**For Medical Content Questions:**
- Email: medical@realdiag.com
- Note: We cannot provide medical advice to patients

**For Security Issues:**
- See SECURITY.md
- Email: security@realdiag.com

---

## 📅 Version & Updates

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-19  
**Next Review:** Annually or upon major software changes

**Change Log:**
- 2025-01-19: Initial comprehensive legal disclaimer created

---

## ✅ Acknowledgment

**BY USING THIS SOFTWARE, YOU ACKNOWLEDGE THAT:**

1. ✅ You have read and understood this disclaimer
2. ✅ You agree to all terms and conditions
3. ✅ You understand this is not medical advice
4. ✅ You will not use this for clinical decisions without independent verification
5. ✅ You assume all responsibility for any use of the software
6. ✅ You will comply with all applicable laws and regulations
7. ✅ You understand the limitations and risks

**IF YOU DO NOT AGREE, DO NOT USE THIS SOFTWARE.**

---

## 🆘 Emergency Medical Disclaimer

**THIS IS NOT AN EMERGENCY SERVICE**

**For Medical Emergencies:**
- 🚨 Call 911 (US) or your local emergency number
- 🚨 Go to the nearest emergency room
- 🚨 Call your doctor immediately

**For Mental Health Emergencies:**
- 988 Suicide & Crisis Lifeline (US)
- Crisis Text Line: Text HOME to 741741

**DO NOT rely on this software in emergency situations.**

---

**© 2025 RealDiag-Software Contributors. All Rights Reserved.**
