# 💰 Pricing Calculator - Implementation Guide

## Overview

An interactive web-based pricing calculator has been added to the RealDiag subscription system. This calculator allows users to estimate their costs based on customer type, number of users, and selected plans.

## Access

**URL**: `http://localhost:8000/subscriptions/calculator`

**Direct Link from Home**: The calculator is now accessible from the main landing page via the "💰 Pricing Calculator" button.

## Features

### 1. Customer Type Selection
- **Individual Clinician**: Choose from Starter, Professional, or Professional Plus plans
- **Healthcare Organization**: Volume-based pricing (10-1000+ seats)
- **Academic Institution**: Faculty, Resident/Fellow, or Student pricing
- **Non-Profit Organization**: Standard or Safety-Net tier pricing

### 2. Dynamic Form
The form adapts based on customer type:
- Individual: Shows plan selection dropdown
- Organization: Shows number of seats input
- Academic: Shows role selection (Faculty/Resident/Student)
- Non-Profit: Shows tier selection (Standard/Expanded)

### 3. Real-Time Calculations
- **Monthly Cost**: Immediate calculation based on selections
- **Annual Cost**: Shows yearly pricing with savings
- **Savings Badge**: Highlights annual savings (2 months free for individuals)
- **Plan Features**: Displays detailed feature list for selected plan

### 4. Quick Reference Table
Visual comparison of all plan tiers with key features:
- Free, Starter, Professional, Professional Plus
- Organization, Enterprise

## Pricing Logic

### Individual Plans
```javascript
Starter:          $29/month
Professional:     $49/month
Professional+:    $69/month

Annual Discount:  2 months free (pay for 10, get 12)
Example:          $49/mo → $490/year (save $98)
```

### Organization Plans (Volume-Based)
```javascript
1-10 seats:       $40/seat/month
11-50 seats:      $32/seat/month
51-100 seats:     $28/seat/month
101-300 seats:    $24/seat/month
300+ seats:       $20/seat/month (enterprise estimate)

Example: 25 seats → $32/seat × 25 = $800/month
```

### Academic Plans
```javascript
Faculty:          $25/month per user
Resident/Fellow:  $12/month per user
Student:          Free

Example: 10 faculty → $25 × 10 = $250/month
```

### Non-Profit Plans
```javascript
Standard:         $18/month per clinician
Safety-Net:       $10/month per clinician

Example: 15 clinicians (Standard) → $18 × 15 = $270/month
```

## Technical Implementation

### Files Created/Modified

1. **backend/templates/pricing_calculator.html** (NEW)
   - Standalone HTML page with embedded CSS and JavaScript
   - Responsive design
   - Interactive calculator form
   - Real-time calculations
   - Plan comparison table

2. **backend/services/subscription_router.py** (MODIFIED)
   - Added `GET /subscriptions/calculator` endpoint
   - Returns HTML template response
   - Public access (no authentication required)

3. **backend/templates/index.html** (MODIFIED)
   - Added "💰 Pricing Calculator" button
   - Links to `/subscriptions/calculator`

4. **SUBSCRIPTION_SYSTEM.md** (MODIFIED)
   - Added calculator documentation
   - Updated API endpoint reference

### API Endpoint

```python
@router.get("/calculator", response_class=HTMLResponse)
async def pricing_calculator(request: Request):
    """
    Interactive pricing calculator page.
    
    Public endpoint - displays HTML calculator for estimating costs.
    """
    return templates.TemplateResponse("pricing_calculator.html", {"request": request})
```

## Usage Examples

### Example 1: Individual Professional Plan
**Selections**:
- Customer Type: Individual Clinician
- Plan: Professional

**Results**:
- Monthly Cost: $49
- Annual Cost: $490 (Save $98/year)
- Features: All modules, FHIR export, priority support

### Example 2: Organization with 25 Seats
**Selections**:
- Customer Type: Healthcare Organization
- Number of Seats: 25

**Results**:
- Monthly Cost: $800 ($32/seat)
- Annual Cost: $9,600
- Features: Admin dashboard, EHR integration, SSO, 24/7 support

### Example 3: Academic Institution with 50 Residents
**Selections**:
- Customer Type: Academic Institution
- Academic Role: Resident/Fellow
- Number of Users: 50

**Results**:
- Monthly Cost: $600 ($12/user)
- Annual Cost: $7,200
- Features: All Professional features, Board prep, Teaching mode

### Example 4: Non-Profit with 8 Clinicians
**Selections**:
- Customer Type: Non-Profit Organization
- Tier: Safety-Net/Expanded
- Number of Clinicians: 8

**Results**:
- Monthly Cost: $80 ($10/clinician)
- Annual Cost: $960
- Features: All Professional features, Mission-focused support

## User Interface

### Design Features
- **Gradient Background**: Purple gradient for visual appeal
- **White Card Design**: Clean calculator container
- **Responsive Layout**: Works on mobile and desktop
- **Color Scheme**: Professional purple (#4f46e5) for actions
- **Typography**: System font stack for consistency
- **Interactive Elements**: Hover effects on buttons and cards

### Calculator Components
1. **Form Section**
   - Dropdown selects for customer type and plans
   - Number inputs for seat/user counts
   - Calculate button with hover effects

2. **Results Section**
   - Plan name display
   - Monthly and annual costs (large, prominent)
   - Savings badge (green) when applicable
   - Feature list with checkmarks

3. **Quick Reference Table**
   - 6-column grid layout
   - Plan cards with hover effects
   - Pricing and key features
   - Responsive grid (adapts to screen size)

### Visual Elements
```
┌────────────────────────────────────────┐
│     RealDiag Pricing Calculator        │
│  Estimate your subscription costs      │
├────────────────────────────────────────┤
│                                        │
│  Customer Type: [Individual ▼]        │
│  Individual Plan: [Professional ▼]    │
│                                        │
│       [Calculate Pricing]              │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Plan Selected: Professional      │ │
│  │ Monthly Cost: $49                │ │
│  │ Annual Cost: $490 [Save $98]     │ │
│  │                                  │ │
│  │ Plan Features:                   │ │
│  │ ✓ All modules                    │ │
│  │ ✓ FHIR export                    │ │
│  │ ✓ Priority support               │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## Testing

### Manual Testing Steps

1. **Start Backend**:
   ```bash
   cd /workspaces/RealDiag-Software
   python backend/main.py
   ```

2. **Access Calculator**:
   ```
   Open browser → http://localhost:8000/subscriptions/calculator
   ```

3. **Test Individual Pricing**:
   - Select "Individual Clinician"
   - Choose "Professional" plan
   - Click "Calculate Pricing"
   - Verify: $49/month, $490/year, saves $98

4. **Test Organization Pricing**:
   - Select "Healthcare Organization"
   - Enter 25 seats
   - Click "Calculate Pricing"
   - Verify: $800/month ($32/seat), $9,600/year

5. **Test Academic Pricing**:
   - Select "Academic Institution"
   - Choose "Resident/Fellow"
   - Enter 10 users
   - Click "Calculate Pricing"
   - Verify: $120/month, $1,440/year

6. **Test Non-Profit Pricing**:
   - Select "Non-Profit Organization"
   - Choose "Safety-Net/Expanded"
   - Enter 5 clinicians
   - Click "Calculate Pricing"
   - Verify: $50/month, $600/year

### Automated Testing

Add to `test_subscriptions.py`:

```python
def test_pricing_calculator_page():
    """Test that pricing calculator page loads."""
    response = requests.get(f"{BASE_URL}/subscriptions/calculator")
    assert response.status_code == 200
    assert "RealDiag Pricing Calculator" in response.text
    print("✅ Pricing calculator page loads successfully")
```

## Integration with Existing System

### 1. Subscription Router
The calculator is integrated into the subscription router:
- New endpoint: `GET /subscriptions/calculator`
- Returns HTML template
- No authentication required (public access)

### 2. Main Application
Added to navigation:
- Button on home page
- Links to calculator
- Seamless user experience

### 3. API Consistency
Uses same pricing logic as API endpoints:
- `calculate_organization_price()`
- Volume discount tiers
- Annual savings calculations

## Business Benefits

### 1. User Experience
- **Self-Service**: Users can estimate costs without contacting sales
- **Transparency**: Clear pricing visibility
- **Comparison**: Easy plan comparison
- **Education**: Learn about features before purchasing

### 2. Sales Enablement
- **Qualification**: Users self-qualify before inquiry
- **Expectations**: Clear cost expectations upfront
- **Conversions**: Faster decision-making
- **Volume**: Shows savings for larger organizations

### 3. Marketing
- **Lead Generation**: Calculator drives engagement
- **Value Demonstration**: Shows ROI clearly
- **Competitive**: Transparent pricing builds trust
- **Sharing**: Shareable URL for partners

## Customization

### Modify Pricing
Edit pricing logic in the JavaScript:

```javascript
function getOrgPerClinicianPrice(n) {
  if (n <= 10) return 40;
  if (n <= 50) return 32;
  // Add more tiers as needed
}
```

### Change Styling
Modify the `<style>` section in `pricing_calculator.html`:

```css
.pricing-calculator {
  background: #f7f7fb;  /* Change background color */
  border-radius: 12px;   /* Adjust corner radius */
}
```

### Add Features
Extend the calculator with:
- Payment frequency toggle (monthly/annual)
- Add-on module pricing
- Multi-year discounts
- Promo code input
- Export PDF quotes

## Future Enhancements

### Phase 1: Basic Improvements
- [ ] Print/PDF export of estimates
- [ ] Email quote to user
- [ ] Social sharing buttons
- [ ] Comparison mode (side-by-side plans)

### Phase 2: Advanced Features
- [ ] Integration with Stripe for direct checkout
- [ ] Save estimates (requires authentication)
- [ ] ROI calculator (time saved, diagnoses improved)
- [ ] Custom quote request form (for Enterprise)

### Phase 3: Personalization
- [ ] Recommended plan based on usage
- [ ] Historical pricing comparison
- [ ] Industry-specific templates
- [ ] Multi-currency support

## SEO & Marketing

### Meta Tags (Future Addition)
```html
<meta name="description" content="Calculate your RealDiag subscription cost. Pricing for individuals, organizations, academic institutions, and non-profits.">
<meta name="keywords" content="RealDiag pricing, medical diagnosis pricing, EHR pricing calculator">
```

### URL Structure
```
/subscriptions/calculator              # Main calculator
/subscriptions/calculator/individual   # Pre-selected individual
/subscriptions/calculator/organization # Pre-selected organization
```

### Analytics Tracking
```javascript
// Track calculator usage
function trackCalculation(type, amount) {
  gtag('event', 'pricing_calculated', {
    'customer_type': type,
    'monthly_cost': amount
  });
}
```

## Support & Maintenance

### Common Issues

**Issue**: Calculator not loading
**Solution**: Check that backend server is running and templates directory exists

**Issue**: Incorrect calculations
**Solution**: Verify JavaScript pricing functions match backend logic

**Issue**: Form not submitting
**Solution**: Check JavaScript console for errors, ensure all required fields present

### Monitoring

Track these metrics:
- Calculator page views
- Calculation completions
- Average estimated cost
- Most popular customer types
- Conversion rate (calculator → signup)

## Conclusion

The pricing calculator provides:
- ✅ Self-service cost estimation
- ✅ Transparent pricing
- ✅ Interactive user experience
- ✅ Plan comparison
- ✅ Volume discount visualization
- ✅ Integration with existing subscription system

**Status**: ✅ Complete and ready to use
**Access**: http://localhost:8000/subscriptions/calculator
**Documentation**: This guide + SUBSCRIPTION_SYSTEM.md
