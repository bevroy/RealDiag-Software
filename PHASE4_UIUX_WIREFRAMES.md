# Phase 4: UI/UX Wireframe Specifications
## RealDiag Mobile App - iOS & Android

**Date:** November 20, 2025  
**Version:** 1.0  
**Design System:** Material Design 3 + iOS Human Interface Guidelines  
**Target Screens:** iPhone 14/15, Pixel 7/8, iPad/Android tablets

---

## Design Philosophy

### Core Principles

1. **Clinical Clarity**
   - One decision point per screen
   - High contrast for readability in bright clinical environments
   - Clear visual hierarchy (emergency → urgent → routine)

2. **Cognitive Load Reduction**
   - Progressive disclosure (show details on demand)
   - Consistent patterns across all screens
   - Minimal taps to complete tasks

3. **Safety-Critical Design**
   - Red flags always visible when present
   - Emergency conditions prominently highlighted
   - Clear "Admit vs Discharge" guidance

4. **Professional Aesthetic**
   - Clean, medical-grade interface
   - Trust-building color palette
   - Evidence transparency

5. **Accessibility First**
   - WCAG 2.1 AA compliant
   - Screen reader optimized
   - Dynamic type support
   - High contrast mode

---

## Design System

### Color Palette

#### Primary Colors
```
Primary Blue:    #1976D2  (Trust, professionalism)
Primary Dark:    #0D47A1  (Headers, emphasis)
Primary Light:   #BBDEFB  (Backgrounds, highlights)

Accent Teal:     #00897B  (Actions, links)
Accent Dark:     #00695C  (Pressed states)
```

#### Clinical Status Colors
```
Emergency Red:   #D32F2F  (Critical conditions, red flags)
Urgent Orange:   #F57C00  (Time-sensitive, warnings)
Success Green:   #388E3C  (Safe, completed)
Info Blue:       #1976D2  (Information, references)
Specialty Purple:#7B1FA2  (Specialty content)
```

#### Neutral Colors
```
Background Light:#FFFFFF  (Main background)
Background Dark: #F5F5F5  (Card backgrounds)
Surface:         #FAFAFA  (Elevated surfaces)
Border:          #E0E0E0  (Dividers)

Text Primary:    #212121  (Main content)
Text Secondary:  #757575  (Supporting text)
Text Disabled:   #9E9E9E  (Inactive elements)
```

### Typography

#### Font Family
- **iOS:** SF Pro (system default)
- **Android:** Roboto (system default)
- **Fallback:** System font stack

#### Type Scale
```
Headline Large:  32pt / Bold    (Screen titles)
Headline Medium: 28pt / SemiBold (Section headers)
Headline Small:  24pt / SemiBold (Subsections)

Title Large:     22pt / Medium  (Card titles)
Title Medium:    16pt / Medium  (List items)
Title Small:     14pt / Medium  (Labels)

Body Large:      16pt / Regular (Main content)
Body Medium:     14pt / Regular (Supporting content)
Body Small:      12pt / Regular (Captions)

Label Large:     14pt / Medium  (Buttons)
Label Medium:    12pt / Medium  (Chips, badges)
Label Small:     11pt / Medium  (Tiny labels)
```

### Spacing System
```
xs:  4pt   (Icon padding)
sm:  8pt   (Element padding)
md:  16pt  (Card padding)
lg:  24pt  (Section spacing)
xl:  32pt  (Screen margins)
xxl: 48pt  (Major sections)
```

### Elevation (Material Design)
```
Level 0: 0dp   (Flat surfaces)
Level 1: 1dp   (Cards, lists)
Level 2: 3dp   (Raised buttons)
Level 3: 6dp   (Floating action buttons)
Level 4: 8dp   (Navigation drawer)
Level 5: 12dp  (Modals, dialogs)
```

---

## Screen Wireframes

### 1. Home Screen (Tree List)

```
┌──────────────────────────────────────────────────┐
│ ← RealDiag                    🔍 ⚙️             │ Header (64pt)
├──────────────────────────────────────────────────┤
│                                                  │
│  Filter by Specialty  [All ▼]        [⭐ Favorites] │ Filter Bar (48pt)
│                                                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🧠 PSYCHIATRY (4 trees)                    │ │ Section Header
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌─────────────────────────────────────────────┐│ Tree Card
│  │ 😟 Anxiety Disorders                    ⭐  ││
│  │ Panic disorder, GAD, specific phobias       ││
│  │                                             ││
│  │ Evidence: DSM-5-TR, APA Guidelines          ││
│  │ Last used: 2 days ago                       ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 😔 Depression & Mood Disorders              ││
│  │ MDD, dysthymia, bipolar depression          ││
│  │                                             ││
│  │ Evidence: DSM-5-TR, APA Guidelines          ││
│  │ Last used: Never                            ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 👁️ OPHTHALMOLOGY (4 trees)                 │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 👁️ Red Eye Evaluation                       ││
│  │ Conjunctivitis, uveitis, glaucoma           ││
│  │ ... (scrollable list)                       ││
│                                                  │
├──────────────────────────────────────────────────┤
│ [🏠 Home]  [🔍 Search]  [📚 Ref]  [⚙️ Settings]  │ Bottom Nav (56pt)
└──────────────────────────────────────────────────┘

Interactions:
- Tap tree card → Navigate to Tree Detail Screen
- Tap ⭐ → Toggle favorite status
- Tap specialty header → Collapse/expand section
- Swipe card left → Quick actions (Start, Info, Share)
- Pull to refresh → Check for updates
```

### 2. Tree Detail Screen

```
┌──────────────────────────────────────────────────┐
│ ← Anxiety Disorders                  ⭐ Share    │ Header
├──────────────────────────────────────────────────┤
│                                                  │
│  😟 Anxiety Disorders                           │ Title (28pt)
│  Psychiatry / Emergency Medicine                │ Specialty (14pt)
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 📊 Evidence Level                          │ │ Info Card
│  │ DSM-5-TR (2022)                            │ │
│  │ APA Practice Guidelines                    │ │
│  │ Last updated: Nov 2025                     │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 💡 Clinical Pearls (9)                ▼   │ │ Collapsible
│  ├────────────────────────────────────────────┤ │
│  │ • Panic attacks peak within 10 minutes    │ │
│  │ • GAD: worry >6 months, difficult control │ │
│  │ • Screen for comorbid depression (50%)    │ │
│  │   ... (7 more)                             │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🚨 Red Flags (8)                      ▼   │ │ Collapsible
│  ├────────────────────────────────────────────┤ │ (Red accent)
│  │ • Suicidal ideation or plan               │ │
│  │ • Severe panic with chest pain (r/o MI)   │ │
│  │ • Acute psychosis or hallucinations       │ │
│  │   ... (5 more)                             │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 📋 Diagnostic Flow Overview                │ │ Info Card
│  │ 9 decision nodes • Avg 8 min completion   │ │
│  │ Covers: GAD, panic disorder, phobias,     │ │
│  │ OCD, PTSD, adjustment disorders           │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│       [🎯 Start Diagnostic Session]             │ Primary CTA
│                                                  │
│  Recent Sessions (2)                            │
│  ┌─────────────────────────────────────────────┐│
│  │ Nov 18, 2025 • 7 min • GAD diagnosis       ││
│  │ Nov 15, 2025 • 5 min • Panic disorder      ││
│  └─────────────────────────────────────────────┘│
│                                                  │
└──────────────────────────────────────────────────┘

Interactions:
- Tap "Start Diagnostic Session" → Begin flow
- Tap clinical pearls/red flags → Expand/collapse
- Tap recent session → Resume or view summary
- Tap Share → Export tree details as PDF
- Tap ⭐ → Toggle favorite
```

### 3. Diagnostic Flow Screen (Main Interface)

```
┌──────────────────────────────────────────────────┐
│ ← Anxiety Disorders              [💡] [🚨] [⋯]   │ Header
│ Node 3 of 9 • ████████░░░░░ 67%                 │ Progress (8pt)
├──────────────────────────────────────────────────┤
│                                                  │
│  🔹 SYMPTOM PATTERN ASSESSMENT                  │ Node Title (20pt)
│                                                  │
│  How long has the patient experienced anxiety?  │ Question (16pt)
│                                                  │
│  ┌────────────────────────────────────────────┐ │ Response Options
│  │ ⚪ Less than 1 month                        │ │ (48pt tap target)
│  └────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────┐ │
│  │ ⚪ 1-6 months                               │ │
│  └────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────┐ │
│  │ ⚪ More than 6 months                       │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │ Collapsible Cards
│  │ 🧪 Tests to Consider              ▼       │ │ (Collapsed)
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🎯 Suggested Diagnoses            ▼       │ │
│  ├────────────────────────────────────────────┤ │ (Expanded)
│  │ • Generalized Anxiety Disorder (GAD)      │ │
│  │ • Adjustment Disorder with Anxiety        │ │
│  │ • Substance-Induced Anxiety               │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 💊 Management Options             ▼       │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🏥 Referrals                      ▼       │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
├──────────────────────────────────────────────────┤
│  [← Back]                           [Next →]    │ Footer (56pt)
└──────────────────────────────────────────────────┘

Interactions:
- Tap response option → Select (radio highlight)
- Tap "Next" → Evaluate routing, navigate to next node
- Tap "Back" → Return to previous node
- Tap [💡] → Show clinical pearls modal
- Tap [🚨] → Show red flags modal
- Tap [⋯] → Menu (Restart, Export, Quit)
- Tap collapsible card → Expand/collapse details
- Long press collapsible → Quick peek preview
```

### 4. Clinical Pearls Modal

```
┌──────────────────────────────────────────────────┐
│                                                  │
│                                              ✕   │ Close button
│                                                  │
│  💡 Clinical Pearls                             │ Modal Title
│  Anxiety Disorders                              │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ Key Insights                               │ │ Section
│  ├────────────────────────────────────────────┤ │
│  │                                            │ │
│  │ • Panic attacks peak within 10 minutes    │ │
│  │   and typically resolve in 20-30 minutes  │ │
│  │                                            │ │
│  │ • GAD requires worry lasting >6 months    │ │
│  │   that is difficult to control            │ │
│  │                                            │ │
│  │ • Screen for comorbid depression (50%+    │ │
│  │   of anxiety patients have depression)    │ │
│  │                                            │ │
│  │ • Substance use disorders coexist in      │ │
│  │   20-30% of anxiety patients              │ │
│  │                                            │ │
│  │ • Medical causes: hyperthyroidism,        │ │
│  │   pheochromocytoma, caffeine, drugs       │ │
│  │                                            │ │
│  │ • SSRIs are first-line (sertraline,       │ │
│  │   escitalopram, paroxetine)               │ │
│  │                                            │ │
│  │ • Avoid long-term benzodiazepines         │ │
│  │   (dependence risk, cognitive effects)    │ │
│  │                                            │ │
│  │ • CBT is as effective as medications      │ │
│  │   for most anxiety disorders              │ │
│  │                                            │ │
│  │ • Response to treatment: 6-8 weeks        │ │
│  │   for full SSRI effect                    │ │
│  │                                            │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│              [Copy All Pearls]                  │ Action button
│                                                  │
└──────────────────────────────────────────────────┘

Interactions:
- Tap ✕ → Close modal
- Swipe down → Dismiss modal
- Tap "Copy All Pearls" → Copy to clipboard
- Scroll → View all pearls
```

### 5. Red Flags Alert Modal

```
┌──────────────────────────────────────────────────┐
│                                                  │
│                                              ✕   │ Close
│                                                  │
│  🚨 RED FLAGS - ANXIETY                         │ Title (Red accent)
│  EMERGENCY CONDITIONS TO RULE OUT               │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ ⚠️  IMMEDIATE EVALUATION REQUIRED          │ │ Warning banner
│  └────────────────────────────────────────────┘ │ (Red bg)
│                                                  │
│  Critical Concerns:                             │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🔴 Suicidal ideation with plan/intent      │ │ Red flag item
│  │    → Immediate psychiatric evaluation      │ │ (Red icon)
│  │    → Safety assessment (Columbia-SSRS)     │ │
│  │    → Consider involuntary commitment       │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🔴 Severe panic with chest pain            │ │
│  │    → Rule out acute MI (troponin, ECG)    │ │
│  │    → Check for arrhythmia, PE             │ │
│  │    → Vital signs monitoring               │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🔴 Acute psychosis or hallucinations       │ │
│  │    → Consider brief psychotic disorder    │ │
│  │    → Substance intoxication/withdrawal    │ │
│  │    → Immediate psychiatric consultation   │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🔴 Signs of substance withdrawal           │ │
│  │    → CIWA-Ar for alcohol withdrawal       │ │
│  │    → Benzodiazepine withdrawal risk       │ │
│  │    → Seizure precautions                  │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ... (4 more red flags, scrollable)             │
│                                                  │
│          [Emergency Resources 📞]               │ Action button
│                                                  │
└──────────────────────────────────────────────────┘

Interactions:
- High contrast red theme
- Tap "Emergency Resources" → Phone numbers, protocols
- Tap ✕ or swipe → Dismiss (requires confirmation)
- Auto-dismiss after 30 seconds (unless scrolled)
```

### 6. Results Summary Screen

```
┌──────────────────────────────────────────────────┐
│ ← Anxiety Disorders         Share  Export  ⋯    │ Header
├──────────────────────────────────────────────────┤
│                                                  │
│  ✅ DIAGNOSTIC SESSION COMPLETE                 │ Status (Green)
│  Completed in 7 minutes • 5 nodes evaluated     │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🎯 PRIMARY DIAGNOSES                       │ │ Diagnosis Card
│  ├────────────────────────────────────────────┤ │ (Elevated)
│  │                                            │ │
│  │ 1. Generalized Anxiety Disorder (GAD)     │ │
│  │    Confidence: High                       │ │
│  │    Evidence: >6 months worry, multiple    │ │
│  │    domains, difficult to control          │ │
│  │                                            │ │
│  │ 2. Adjustment Disorder with Anxiety       │ │
│  │    Confidence: Moderate                   │ │
│  │    Consider if identifiable stressor      │ │
│  │                                            │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 💊 RECOMMENDED MANAGEMENT          ▼      │ │ Collapsible
│  ├────────────────────────────────────────────┤ │
│  │ First-Line Pharmacotherapy:               │ │
│  │ • Sertraline 25mg daily → 50-200mg/day    │ │
│  │ • Escitalopram 5-10mg → 10-20mg/day       │ │
│  │ • Paroxetine 10mg → 20-50mg/day           │ │
│  │                                            │ │
│  │ Non-Pharmacologic:                        │ │
│  │ • Cognitive Behavioral Therapy (CBT)      │ │
│  │ • Mindfulness-based stress reduction      │ │
│  │ • Relaxation techniques                   │ │
│  │                                            │ │
│  │ Avoid:                                    │ │
│  │ ⚠️  Long-term benzodiazepines             │ │
│  │                                            │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🏥 DISPOSITION & FOLLOW-UP         ▼      │ │ Collapsible
│  ├────────────────────────────────────────────┤ │
│  │ Recommended Disposition:                  │ │
│  │ ✅ Outpatient management appropriate      │ │
│  │                                            │ │
│  │ Follow-Up:                                │ │
│  │ • Psychiatry: Routine (2-4 weeks)         │ │
│  │ • Primary care: 1-2 weeks post-start Rx   │ │
│  │ • Monitor for treatment response (6-8 wk) │ │
│  │                                            │ │
│  │ Admit Criteria (Not Met):                 │ │
│  │ • Active suicidal ideation with plan      │ │
│  │ • Severe functional impairment            │ │
│  │ • Acute substance withdrawal              │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 📚 EVIDENCE BASE                           │ │
│  │ • DSM-5-TR (2022) - Diagnostic criteria   │ │
│  │ • APA Practice Guidelines (2020)          │ │
│  │ • [View all 5 references →]               │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│     [📋 Copy Summary]  [💾 Save to Files]      │ Actions
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 📊 Session Timeline (Collapsed)       ▼   │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│           [🏠 Return to Home]                   │ Primary CTA
│                                                  │
└──────────────────────────────────────────────────┘

Interactions:
- Tap "Share" → Export as PDF or text
- Tap "Export" → Save to Files app, email, print
- Tap collapsible sections → Expand/collapse
- Tap "View all references" → Evidence detail screen
- Tap "Copy Summary" → Copy formatted text
- Tap "Return to Home" → Back to tree list
```

### 7. Search Screen

```
┌──────────────────────────────────────────────────┐
│  🔍 Search Diagnostic Trees                     │ Header
│  ┌──────────────────────────────────────────┐   │ Search Bar
│  │ 🔍 Chest pain, headache, anxiety...      │   │ (56pt)
│  └──────────────────────────────────────────┘   │
├──────────────────────────────────────────────────┤
│                                                  │
│  Filter by Specialty:                           │ Filter Chips
│  [All] [🧠 Psych] [👁️ Ophtho] [👂 ENT] [More ▼] │ (Horizontal scroll)
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🕐 Recent Searches                         │ │ Section
│  ├────────────────────────────────────────────┤ │
│  │ 🕐 chest pain              [×]             │ │
│  │ 🕐 anxiety                 [×]             │ │
│  │ 🕐 red eye                 [×]             │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🔥 Frequently Used Trees                   │ │
│  ├────────────────────────────────────────────┤ │
│  │ • Chest Pain (Cardiology)                 │ │
│  │ • Headache (Neurology)                    │ │
│  │ • Abdominal Pain (Gastroenterology)       │ │
│  │ • Red Eye (Ophthalmology)                 │ │
│  │ • Anxiety (Psychiatry)                    │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 💡 Search Tips                             │ │
│  │ Try: symptom, specialty, condition name   │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
├──────────────────────────────────────────────────┤
│ [🏠 Home]  [🔍 Search]  [📚 Ref]  [⚙️ Settings]  │ Bottom Nav
└──────────────────────────────────────────────────┘

// After typing search query:

┌──────────────────────────────────────────────────┐
│  ← anxiety                                   ✕   │ Active Search
│  ┌──────────────────────────────────────────┐   │
│  │ 🔍 anxiety                                │   │
│  └──────────────────────────────────────────┘   │
├──────────────────────────────────────────────────┤
│                                                  │
│  Found 3 trees for "anxiety"                    │ Results count
│                                                  │
│  ┌─────────────────────────────────────────────┐│ Result Card
│  │ 😟 Anxiety Disorders                     ⭐ ││ (Highlighted)
│  │ Psychiatry / Emergency Medicine             ││
│  │ Panic disorder, GAD, specific phobias...    ││
│  │ Evidence: DSM-5-TR, APA Guidelines          ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 😔 Depression & Mood Disorders              ││
│  │ Psychiatry                                  ││
│  │ Comorbid anxiety common (50%+)              ││
│  │ Evidence: DSM-5-TR, APA Guidelines          ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 💔 Chest Pain                               ││
│  │ Cardiology / Emergency Medicine             ││
│  │ Rule out panic disorder vs ACS              ││
│  │ Evidence: AHA/ACC Guidelines                ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  No more results                                │
│                                                  │
└──────────────────────────────────────────────────┘

Interactions:
- Type in search bar → Instant results (debounced 300ms)
- Tap specialty chip → Filter results
- Tap result card → Navigate to tree detail
- Tap ✕ → Clear search
- Tap recent search → Re-run search
- Swipe left on recent → Delete [×]
```

### 8. Clinical Reference Screen

```
┌──────────────────────────────────────────────────┐
│  📚 Clinical Reference                          │ Header
├──────────────────────────────────────────────────┤
│                                                  │
│  [💡 Pearls]  [🚨 Red Flags]  [📖 Guidelines]   │ Tabs
│  ════════════                                    │ (Active: Pearls)
│                                                  │
│  Filter by Specialty:                           │
│  [All] [🧠 Psych] [👁️ Ophtho] [👂 ENT] [More ▼] │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 🧠 PSYCHIATRY                              │ │ Category
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌─────────────────────────────────────────────┐│ Pearl Card
│  │ 💡 Anxiety Disorders                        ││
│  │ • Panic attacks peak in 10 min              ││
│  │ • GAD requires >6 months duration           ││
│  │ • Screen for depression (50% comorbidity)   ││
│  │                                             ││
│  │ [View Full Tree →]                          ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 💡 Depression                               ││
│  │ • PHQ-9 ≥10: moderate to severe depression  ││
│  │ • SSRIs take 6-8 weeks for full effect      ││
│  │ • 30-40% achieve remission with first SSRI  ││
│  │ [View Full Tree →]                          ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 👁️ OPHTHALMOLOGY                           │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 💡 Red Eye                                  ││
│  │ • Acute angle-closure: rock-hard eye        ││
│  │ • Viral conjunctivitis: watery discharge    ││
│  │ • Bacterial: purulent discharge             ││
│  │ [View Full Tree →]                          ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ... (scrollable)                               │
│                                                  │
├──────────────────────────────────────────────────┤
│ [🏠 Home]  [🔍 Search]  [📚 Ref]  [⚙️ Settings]  │ Bottom Nav
└──────────────────────────────────────────────────┘

// Red Flags Tab:

┌──────────────────────────────────────────────────┐
│  [💡 Pearls]  [🚨 Red Flags]  [📖 Guidelines]   │ Tabs
│               ════════════                       │ (Active: Red Flags)
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 🚨 EMERGENCY CONDITIONS                     ││ Warning Card
│  │ Immediate evaluation required               ││ (Red accent)
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 🔴 Suicidal Ideation with Plan             ││ Red Flag Item
│  │ Tree: Anxiety, Depression, Psychosis        ││
│  │ Action: Immediate psychiatric evaluation    ││
│  │ Tools: Columbia-SSRS, safety contract       ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │ 🔴 Acute Vision Loss                        ││
│  │ Tree: Vision Loss, Diplopia                 ││
│  │ Action: Emergent ophthalmology consult      ││
│  │ DDx: CRAO, retinal detachment, stroke       ││
│  └─────────────────────────────────────────────┘│
│                                                  │
│  ... (all red flags from 41 trees)              │
│                                                  │
└──────────────────────────────────────────────────┘

Interactions:
- Tap tab → Switch between Pearls, Red Flags, Guidelines
- Tap specialty chip → Filter by specialty
- Tap card → Expand full details
- Tap "View Full Tree" → Navigate to tree
- Long press card → Quick actions (Share, Copy, Bookmark)
```

### 9. Settings Screen

```
┌──────────────────────────────────────────────────┐
│ ← Settings                                       │ Header
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ APPEARANCE                                 │ │ Section
│  ├────────────────────────────────────────────┤ │
│  │ Theme                          [Light  ▼] │ │
│  │ Text Size                      [Medium ▼] │ │
│  │ High Contrast Mode             [Toggle]   │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ CONTENT                                    │ │
│  ├────────────────────────────────────────────┤ │
│  │ Specialty Filters              [15/15 ✓] │ │
│  │ Show Clinical Pearls by Default [Toggle]  │ │
│  │ Show Red Flags by Default      [Toggle]   │ │
│  │ Auto-expand Suggestions        [Toggle]   │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ DATA & SYNC                                │ │
│  ├────────────────────────────────────────────┤ │
│  │ Clear Search History           [Clear]    │ │
│  │ Clear Session Data             [Clear]    │ │
│  │ Check for Tree Updates         [Check]    │ │
│  │ Last updated: Nov 20, 2025                │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ ANALYTICS (Anonymous)                      │ │
│  ├────────────────────────────────────────────┤ │
│  │ Share usage data               [Toggle]   │ │
│  │ Helps improve clinical content            │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ ABOUT                                      │ │
│  ├────────────────────────────────────────────┤ │
│  │ Version                        1.0.0      │ │
│  │ Diagnostic Trees               41 trees   │ │
│  │ Specialties                    15         │ │
│  │ Evidence Citations             200+       │ │
│  │                                            │ │
│  │ [📄 Privacy Policy]                        │ │
│  │ [⚖️  Terms of Service]                     │ │
│  │ [📧 Contact Support]                       │ │
│  │ [⭐ Rate App]                              │ │
│  │ [🐛 Report Bug]                            │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ DISCLAIMER                                 │ │
│  │ This app is a clinical reference tool.    │ │
│  │ Not a substitute for clinical judgment.   │ │
│  │ Consult official guidelines and experts.  │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
├──────────────────────────────────────────────────┤
│ [🏠 Home]  [🔍 Search]  [📚 Ref]  [⚙️ Settings]  │ Bottom Nav
└──────────────────────────────────────────────────┘

Interactions:
- Tap dropdown → Show options
- Tap toggle → Enable/disable feature
- Tap "Specialty Filters" → Multi-select screen
- Tap "Clear" → Confirmation dialog
- Tap "Check for Tree Updates" → Background sync
- Tap links → Open in-app browser or external
```

---

## Component Library

### Reusable Components

#### 1. TreeCard Component
```tsx
<TreeCard
  id="PSYCH-ANXIETY"
  title="Anxiety Disorders"
  specialty="Psychiatry / Emergency Medicine"
  description="Panic disorder, GAD, specific phobias"
  evidenceLevel="DSM-5-TR, APA Guidelines"
  isFavorite={false}
  lastUsed="2 days ago"
  onPress={() => navigate('TreeDetail')}
  onFavoriteToggle={() => toggleFavorite('PSYCH-ANXIETY')}
/>
```

#### 2. ClinicalPearlCard Component
```tsx
<ClinicalPearlCard
  icon="💡"
  title="Clinical Pearls"
  count={9}
  isExpanded={false}
  onToggle={() => setExpanded(!expanded)}
>
  <BulletList items={clinicalPearls} />
</ClinicalPearlCard>
```

#### 3. RedFlagAlert Component
```tsx
<RedFlagAlert
  severity="critical"
  title="Suicidal ideation with plan/intent"
  action="Immediate psychiatric evaluation"
  protocols={[
    "Safety assessment (Columbia-SSRS)",
    "Consider involuntary commitment"
  ]}
/>
```

#### 4. ProgressIndicator Component
```tsx
<ProgressIndicator
  currentNode={3}
  totalNodes={9}
  percentage={67}
  treeTitle="Anxiety Disorders"
/>
```

#### 5. DiagnosisCard Component
```tsx
<DiagnosisCard
  rank={1}
  diagnosis="Generalized Anxiety Disorder (GAD)"
  confidence="High"
  reasoning=">6 months worry, multiple domains, difficult to control"
/>
```

---

## Responsive Design

### iPhone (Portrait)
- Single column layout
- Bottom navigation (56pt)
- Safe area insets for notch/Dynamic Island
- Modal sheets for details

### iPhone (Landscape)
- Two-column layout for wider screens
- Side-by-side navigation during diagnostic flow
- Clinical pearls in sidebar

### iPad (Portrait & Landscape)
- Two-column master-detail layout
- Tree list always visible (master pane)
- Tree detail/flow in detail pane
- Floating modals instead of sheets

### Android Tablets
- Similar to iPad layout
- Material Design 3 navigation rail
- Adaptive layouts based on screen width

---

## Accessibility Features

### Screen Reader Support
- Semantic HTML/ARIA labels
- Descriptive button labels
- Heading hierarchy
- Alt text for icons
- Live region announcements for state changes

### Visual Accessibility
- WCAG 2.1 AA contrast ratios (4.5:1 minimum)
- Dynamic type support (up to 200% scale)
- High contrast mode
- Color-blind friendly palette (no red-green dependencies)

### Motor Accessibility
- Minimum 44x44pt touch targets
- No time-based interactions
- Swipe alternatives (buttons)
- Voice control support (iOS/Android)

### Cognitive Accessibility
- Simple, consistent language
- One task per screen
- Progress indicators
- Undo/back functionality
- Confirmation dialogs for destructive actions

---

## Animation & Micro-interactions

### Transitions
- **Screen transitions:** 300ms ease-in-out
- **Modal entry:** Slide up 250ms with fade
- **Modal exit:** Slide down 200ms with fade
- **Collapsible expand:** 200ms ease-out
- **Button press:** Scale 0.95 with 100ms duration

### Loading States
- **Initial load:** Skeleton screens (gray blocks)
- **Content load:** Shimmer effect
- **Background sync:** Subtle progress bar in header
- **Button loading:** Spinner replaces text

### Feedback
- **Success:** Green checkmark animation (500ms)
- **Error:** Red shake animation (300ms)
- **Added favorite:** Star fills with pulse (400ms)
- **Copied text:** Toast notification (2s)

---

## Dark Mode Specifications

### Dark Color Palette
```
Background:      #121212  (Pure black with slight elevation)
Surface:         #1E1E1E  (Cards, elevated surfaces)
Primary:         #82B1FF  (Lighter blue for contrast)
Accent:          #26A69A  (Teal accent)
Error:           #FF5252  (Bright red for visibility)
Text Primary:    #FFFFFF  (White text)
Text Secondary:  #B0B0B0  (Gray text)
```

### Dark Mode Considerations
- Reduce bright whites to #E0E0E0
- Elevate surfaces with subtle shadows
- Increase contrast for clinical content
- Red flags remain highly visible
- Preserve clinical color coding

---

## Performance Considerations

### Image Optimization
- Use SVG for icons (scalable, small)
- WebP for photos (if needed)
- Lazy load images below fold
- Cache specialty icons

### Code Splitting
- Lazy load specialty-specific screens
- Dynamic import for large reference data
- Route-based code splitting

### Rendering Optimization
- FlatList for long lists (virtualization)
- React.memo for static components
- useMemo for expensive computations
- Avoid inline functions in render

---

## Conclusion

These wireframes provide a comprehensive blueprint for the RealDiag mobile app UI/UX. The design prioritizes clinical clarity, safety, and efficiency while maintaining a professional aesthetic appropriate for medical professionals.

**Key Design Achievements:**
- ✅ One decision point per screen (cognitive load reduction)
- ✅ Red flags always accessible (safety first)
- ✅ Evidence transparency (trust building)
- ✅ Offline-first functionality (reliable in all settings)
- ✅ WCAG 2.1 AA accessible (inclusive design)

**Next Step:** Develop 6-8 week technical roadmap with implementation milestones.

---

**Document Prepared By:** RealDiag Development Team  
**Date:** November 20, 2025  
**Next Review:** Technical Roadmap Completion  
**Contact:** GitHub @bevroy
