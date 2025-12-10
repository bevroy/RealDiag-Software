# RealDiag Beta Testing - Tester Access Guide

## 🎯 How to Access RealDiag Test Environment

### Option 1: Web Access (Recommended)
If you've deployed the test environment to a web server:

**URL**: `https://test.realdiag.com` (or your test domain)

1. Open the URL in your browser
2. Click "Sign Up" to create an account
3. Enter your email and create a password
4. Log in and start testing
5. **All features are automatically unlocked** - no payment needed!

---

### Option 2: Local Access (For Technical Testers)

If running locally on your machine:

**Frontend**: `http://localhost:3000`  
**Backend API**: `http://localhost:8000`

#### Prerequisites:
- Git installed
- Python 3.8+ installed
- Node.js 16+ installed
- PostgreSQL installed (optional)

#### Setup Steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/bevroy/RealDiag-Software.git
   cd RealDiag-Software
   ```

2. **Run the automated setup**
   ```bash
   chmod +x setup_test_environment.sh
   ./setup_test_environment.sh
   ```

3. **Start the backend** (Terminal 1)
   ```bash
   ./start_backend_test.sh
   ```
   Wait for: `Uvicorn running on http://127.0.0.1:8000`

4. **Start the frontend** (Terminal 2)
   ```bash
   ./start_frontend_test.sh
   ```
   Wait for: `Ready on http://localhost:3000`

5. **Open your browser**
   Navigate to: `http://localhost:3000`

---

### Option 3: Docker (Coming Soon)

Quick one-command setup:
```bash
docker-compose -f docker-compose.test.yml up
```

---

## 🔐 Creating Your Test Account

### Sign Up Process

1. **Navigate to the application**
   - Web: Your test URL
   - Local: `http://localhost:3000`

2. **Click "Register" or "Sign Up"**

3. **Fill in your details:**
   - **Email**: Use your real email (for password resets)
   - **Password**: At least 8 characters
   - **Name**: Your full name (optional)

4. **Email Verification** (if enabled):
   - Check your inbox for verification email
   - Click the verification link
   - Or ask admin to manually verify your account

5. **Log In**
   - Use your email and password
   - You'll immediately have **enterprise-level access**!

### No Payment Required! ✅

Unlike production, test accounts automatically get:
- ✅ All premium features
- ✅ Unlimited searches
- ✅ API access
- ✅ Export capabilities
- ✅ Priority support access

---

## 🎯 What You Should Test

### Core Features

#### 1. Symptom Search
- [ ] Search for common symptoms (e.g., "headache", "chest pain")
- [ ] Try multi-word symptoms (e.g., "facial pain", "abdominal pain")
- [ ] Test with multiple symptoms together
- [ ] Verify results are medically appropriate

#### 2. Diagnostic Evaluation
- [ ] Select a diagnostic from search results
- [ ] Review the clinical information
- [ ] Check treatment recommendations
- [ ] Verify references and citations

#### 3. Health Records
- [ ] Add personal health information
- [ ] Connect wearable devices (if you have them)
- [ ] Integrate EHR data (if available)
- [ ] Track symptoms over time

#### 4. Reports & Export
- [ ] Generate diagnostic reports
- [ ] Export data to PDF
- [ ] Export to CSV
- [ ] Email reports to yourself

#### 5. User Experience
- [ ] Navigation - Is it intuitive?
- [ ] Mobile responsiveness - Test on phone/tablet
- [ ] Loading speeds - Are pages fast?
- [ ] Error handling - What happens with bad input?
- [ ] Help/documentation - Is it clear?

### Advanced Features (If You're Adventurous)

- [ ] API access (for developers)
- [ ] Bulk diagnostics
- [ ] Integration with other tools
- [ ] Custom workflows
- [ ] Organization features (multi-user)

---

## 🐛 How to Report Issues

### Quick Bug Report

Found a bug? Report it immediately:

**Option 1: GitHub Issues** (Preferred)
1. Go to: https://github.com/bevroy/RealDiag-Software/issues
2. Click "New Issue"
3. Select "Bug Report" template
4. Fill in the details (see template below)

**Option 2: Email**
Send to: `testing@realdiag.com`

**Option 3: In-App Feedback**
Click the feedback button (if visible in the UI)

### Bug Report Template

```markdown
**Bug Description**
A clear description of what went wrong.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Enter '...'
4. See error

**Expected Behavior**
What should have happened?

**Actual Behavior**
What actually happened?

**Screenshots**
Add screenshots if applicable

**Environment**
- Browser: [e.g., Chrome 120]
- Device: [e.g., iPhone 14, Desktop]
- OS: [e.g., iOS 17, Windows 11]

**Additional Context**
Any other relevant information
```

### Severity Levels

- 🔴 **Critical**: App crashes, data loss, security issue
- 🟠 **High**: Feature doesn't work, blocking workflow
- 🟡 **Medium**: Feature works but has issues
- 🟢 **Low**: Minor UI/UX issue, typo, suggestion

---

## 💡 Providing Feedback

### What We Want to Know

#### Usability
- Is the interface intuitive?
- Could you find what you needed?
- Did anything confuse you?
- What would make it easier to use?

#### Features
- Are the features useful?
- What's missing?
- What would you add/change?
- Which features do you use most?

#### Performance
- Is it fast enough?
- Any slow pages or actions?
- Does it work well on mobile?
- Battery/resource usage concerns?

#### Content
- Is medical information accurate?
- Are explanations clear?
- Too much/too little detail?
- Missing important information?

### Feedback Methods

**Surveys** (Sent via email)
- Weekly check-in surveys
- End-of-testing comprehensive survey

**Interviews** (Optional)
- 30-minute video call
- Share your screen while testing
- Walk through your workflow

**Usage Analytics** (Automatic)
- We track what features are used
- No personal data collected
- Helps us prioritize improvements

---

## 📱 Multi-Device Testing

### Please Test On Multiple Devices

#### Desktop
- [ ] Windows PC
- [ ] Mac
- [ ] Linux

#### Mobile
- [ ] iPhone (iOS)
- [ ] Android phone
- [ ] iPad/tablet

#### Browsers
- [ ] Chrome
- [ ] Safari
- [ ] Firefox
- [ ] Edge

**Note**: Not everyone has all devices - just test what you have!

---

## ⚠️ Important Reminders

### Do NOT Use for Real Medical Decisions

This is a **TEST ENVIRONMENT**:
- ❌ Not approved for clinical use
- ❌ Not validated for patient care
- ❌ Data may be incomplete/incorrect
- ❌ Not HIPAA compliant yet

**For Testing Purposes Only!**

### Privacy & Data

- ✅ Your data is kept confidential
- ✅ We won't share your information
- ✅ Data may be reset during testing
- ✅ Test data is isolated from production
- ❌ Don't enter real patient data
- ❌ Don't use for actual diagnosis

### Test Data Examples

Use these fictional scenarios for testing:

**Patient 1: Migraine**
- Symptoms: severe headache, sensitivity to light, nausea
- Age: 35, Female
- Duration: 4 hours

**Patient 2: Chest Pain**
- Symptoms: chest pain, shortness of breath, sweating
- Age: 55, Male  
- Duration: 30 minutes

**Patient 3: Abdominal Pain**
- Symptoms: lower right abdominal pain, fever, nausea
- Age: 28, Female
- Duration: 12 hours

---

## 🔧 Troubleshooting

### Can't Access the Application

**Problem**: URL doesn't load

**Solutions**:
- Check your internet connection
- Verify the URL is correct
- Try a different browser
- Clear browser cache
- Contact support

### Can't Create Account

**Problem**: Registration fails

**Solutions**:
- Check email format is correct
- Use a stronger password (8+ characters)
- Try a different email address
- Check if email already registered
- Contact admin for manual account creation

### Features Are Locked

**Problem**: Features show "Upgrade Required"

**Solutions**:
- Verify you're in test environment (look for test banner)
- Check URL is the test domain
- Log out and log back in
- Clear browser cookies
- Contact support to verify account status

### Slow Performance

**Problem**: App is very slow

**Solutions**:
- Check your internet speed
- Close other browser tabs
- Clear browser cache
- Try a different browser
- Report persistent issues

### Email Not Received

**Problem**: Verification email not arriving

**Solutions**:
- Check spam/junk folder
- Wait 5-10 minutes
- Request another verification email
- Contact admin to manually verify
- Use a different email provider

---

## 📞 Getting Help

### Support Channels

**Email Support**
- testing@realdiag.com
- Response time: 24-48 hours

**Slack Channel** (If provided)
- #test-environment
- Real-time community help

**Documentation**
- Full guide: `docs/TEST_ENVIRONMENT.md`
- API docs: http://localhost:8000/docs (or your domain)

**Emergency Contact**
For critical issues only:
- Emergency email: support@realdiag.com
- Include: Your name, email, issue description

---

## 📅 Testing Timeline

### Phase 1: Initial Testing (Week 1-2)
- Get familiar with the app
- Test core features
- Report obvious bugs
- Provide initial feedback

### Phase 2: Deep Testing (Week 3-4)
- Test edge cases
- Try advanced features
- Stress test with lots of data
- Provide detailed feedback

### Phase 3: Final Testing (Week 5-6)
- Verify bug fixes
- Retest problem areas
- Complete final survey
- Prepare for launch

**Your participation timeline may vary**

---

## 🎁 Thank You!

### Why Your Testing Matters

Your feedback helps us:
- ✅ Find bugs before launch
- ✅ Improve user experience
- ✅ Prioritize features
- ✅ Ensure medical accuracy
- ✅ Build a better product

### Acknowledgment

All beta testers will be:
- Listed in our acknowledgments (if you agree)
- Given early access to new features
- Offered discounted subscription (when we launch)
- Invited to exclusive webinars
- Recognized as founding users

**Thank you for helping make RealDiag better!** 🎉

---

## 📋 Quick Reference Card

Print or save this for easy reference:

```
┌─────────────────────────────────────────┐
│     RealDiag Beta Testing Cheat Sheet   │
├─────────────────────────────────────────┤
│                                         │
│ 🌐 Access URL:                          │
│    [Your test environment URL]          │
│                                         │
│ 📧 Support Email:                       │
│    testing@realdiag.com                 │
│                                         │
│ 🐛 Report Bugs:                         │
│    GitHub Issues or Email               │
│                                         │
│ 📱 Test Account:                        │
│    Email: ___________________           │
│    Password: ___________________        │
│                                         │
│ ✅ Key Features to Test:                │
│    □ Symptom search                     │
│    □ Diagnostic results                 │
│    □ Health records                     │
│    □ Reports & export                   │
│    □ Mobile responsiveness              │
│                                         │
│ ⚠️  Remember:                            │
│    • Test environment only              │
│    • No real medical use                │
│    • All features unlocked              │
│    • No payment required                │
│                                         │
└─────────────────────────────────────────┘
```

---

**Last Updated**: December 10, 2025  
**Version**: 1.0.0  
**Questions?** Contact testing@realdiag.com
