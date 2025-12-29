import json

# Define the 49 new cases (CASE-052 to CASE-100)
new_cases = [
    {
        "case_id": "CASE-052",
        "title": "Woman with Itchy Rash Between Fingers",
        "specialty": "dermatology",
        "difficulty": "beginner",
        "learning_objectives": [
            "Recognize scabies presentation",
            "Understand transmission and treatment",
            "Manage household contacts"
        ],
        "presentation": "32-year-old woman with 3 weeks of intensely itchy rash, worse at night",
        "history": {
            "chief_complaint": "Itchy rash driving me crazy, especially at night",
            "hpi": "Progressive itching for 3 weeks, most severe at night, disrupting sleep. Rash started between fingers, now spread to wrists, waist, and breasts. Partner also itching. No fever. Tried OTC hydrocortisone without relief.",
            "pmh": "Eczema as child",
            "medications": "Hydrocortisone cream",
            "social": "Lives with partner, no recent travel, works as teacher",
            "family": "Non-contributory"
        },
        "physical_exam": {
            "vitals": "Normal",
            "skin": "Erythematous papules and burrows in finger webs, wrists, waistline, around nipples. Excoriations from scratching. Linear burrows visible",
            "general": "Appears tired, multiple excoriations"
        },
        "labs": {
            "skin_scraping": "Microscopy shows mites, eggs, and fecal pellets"
        },
        "imaging": {
            "none": "Not indicated"
        },
        "correct_diagnosis": "DERM-SCABIES",
        "differential": [
            "DERM-SCABIES",
            "DERM-ECZEMA",
            "DERM-CONTACT-DERMATITIS",
            "DERM-BED-BUGS"
        ],
        "explanation": "Scabies caused by Sarcoptes scabiei mite. Key features: (1) Intense pruritus worse at night (mite activity), (2) Burrows in web spaces, wrists, waistline, genitals, breasts, (3) Spreads to household contacts, (4) Microscopy confirms diagnosis. Highly contagious via prolonged skin contact.",
        "management_pearls": [
            "Permethrin 5% cream: apply neck to toes, leave 8-14 hours (overnight), wash off. Repeat in 1 week",
            "Alternative: Ivermectin 200 mcg/kg PO, repeat in 1-2 weeks",
            "Treat ALL household and close contacts simultaneously even if asymptomatic",
            "Wash all clothes, bedding, towels in hot water and dry on high heat",
            "Vacuum furniture and carpets",
            "Items that can't be washed: seal in plastic bag for 72 hours",
            "Oral antihistamines for itching (may persist 2-4 weeks after successful treatment)",
            "Post-scabetic dermatitis: itching may persist despite cure - treat with topical steroids"
        ],
        "pitfalls": [
            "Crusted (Norwegian) scabies: immunocompromised patients, hyperinfestation with millions of mites, highly contagious",
            "Itching persists 2-4 weeks after successful treatment - does not indicate treatment failure",
            "Must treat contacts to prevent reinfection",
            "Nodular scabies: persistent nodules in groin/axilla after treatment"
        ],
        "tags": ["scabies", "itching", "dermatology", "infectious"],
        "created_at": "2025-12-29T18:00:00.000000",
        "author": "Dr. Dermatology"
    },
    {
        "case_id": "CASE-053",
        "title": "Man with Red, Painful Eye",
        "specialty": "ophthalmology",
        "difficulty": "beginner",
        "learning_objectives": [
            "Recognize viral conjunctivitis",
            "Differentiate from bacterial and allergic conjunctivitis",
            "Understand management and prevention"
        ],
        "presentation": "28-year-old man with 2 days of red, watery left eye with discharge",
        "history": {
            "chief_complaint": "My eye is really red and watery",
            "hpi": "Woke up 2 days ago with left eye redness and watering. Watery discharge, eyes stuck together in morning. Gritty sensation. No pain. Vision normal. No photophobia. Coworker had pink eye last week. Now right eye starting to get red too.",
            "pmh": "Healthy",
            "medications": "None",
            "social": "Office worker, wears glasses",
            "family": "Non-contributory"
        },
        "physical_exam": {
            "vitals": "Normal",
            "eye_exam": "Left eye: diffuse conjunctival injection, watery discharge, lid edema, preauricular lymphadenopathy. Right eye: mild injection starting. Visual acuity 20/20 both eyes. Pupils equal and reactive. No corneal infiltrate on fluorescein staining",
            "general": "Well-appearing"
        },
        "labs": {
            "none": "Clinical diagnosis"
        },
        "imaging": {
            "none": "Not indicated"
        },
        "correct_diagnosis": "OPHTHO-VIRAL-CONJUNCTIVITIS",
        "differential": [
            "OPHTHO-VIRAL-CONJUNCTIVITIS",
            "OPHTHO-BACTERIAL-CONJUNCTIVITIS",
            "OPHTHO-ALLERGIC-CONJUNCTIVITIS",
            "OPHTHO-SUBCONJUNCTIVAL-HEMORRHAGE"
        ],
        "explanation": "Viral conjunctivitis ('pink eye') is highly contagious. Key features: (1) Watery discharge (vs purulent in bacterial), (2) Preauricular lymphadenopathy, (3) Often bilateral or sequential, (4) Outbreak setting, (5) No vision loss or severe pain. Most common cause: adenovirus. Self-limited but contagious for 10-14 days.",
        "management_pearls": [
            "Supportive care: cool compresses, artificial tears",
            "NO ANTIBIOTICS - viral etiology",
            "Contagious for 10-14 days - avoid work/school until discharge resolves",
            "Prevention: frequent handwashing, avoid touching eyes, don't share towels/pillows",
            "If bacterial conjunctivitis suspected (purulent discharge): topical antibiotics (erythromycin ointment, polymyxin B-trimethoprim drops)",
            "Return precautions: vision loss, severe pain, photophobia - may indicate keratitis"
        ],
        "pitfalls": [
            "Bacterial vs viral: purulent (thick, yellow-green) discharge suggests bacterial",
            "Allergic: bilateral, itching, seasonal pattern, no lymphadenopathy",
            "Neonatal conjunctivitis: <28 days old - consider chlamydia, gonorrhea, chemical (from prophylaxis)",
            "Red flags: vision loss, severe pain, photophobia, halo vision, corneal opacity - refer to ophthalmology"
        ],
        "tags": ["conjunctivitis", "pink eye", "ophthalmology", "infectious"],
        "created_at": "2025-12-29T18:00:00.000000",
        "author": "Dr. Ophthalmology"
    }
]

# Continue adding more cases...
# Due to length, I'll add them in batches
print(f"Created {len(new_cases)} new case templates")
