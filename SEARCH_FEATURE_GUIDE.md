# Diagnosis Search Feature Guide

## Overview
The Diagnosis Search feature allows users who already know a diagnosis or ICD-10 code to quickly find the corresponding decision tree and supplemental information without going through the symptom-based diagnostic flow.

## Implementation Details

### Backend API (`backend/services/search_router.py`)

#### Endpoints

1. **`GET /api/search?q={query}`**
   - Main search endpoint
   - Searches across:
     - ICD-10 codes (exact and partial matches)
     - Diagnosis names
     - Descriptions
     - Chief complaints
     - Tree IDs
   - Returns sorted results (exact ICD-10 matches first, then alphabetically by name)
   - Query parameter: `q` (required) - search term

2. **`GET /api/search/by-family?family={family}`**
   - Filter decision trees by medical specialty/family
   - Query parameter: `family` (required) - specialty name
   - Returns all trees in the specified family

3. **`GET /api/search/families`**
   - Lists all available medical families/specialties
   - No parameters required
   - Returns array of unique family names

### Frontend Interface (`frontend/pages/search.js`)

#### Features
- Clean, user-friendly search interface
- Text input for searching by diagnosis name or ICD-10 code
- Dropdown to browse by medical specialty
- Real-time search results display
- Click-through to full decision tree
- Loading states and error handling
- Responsive design matching RealDiag's UI style

#### Search Result Display
Each result shows:
- Diagnosis name (title)
- ICD-10 code (badge)
- Description
- Medical family/specialty
- Chief complaint
- Clickable card to navigate to full decision tree

### Navigation Integration
The search feature is accessible from all main navigation menus:
- Home page
- Rules page
- Education page
- Symptom Search page
- Account page
- Sources page

Look for "🔍 Diagnosis Search" in the navigation dropdown.

## Use Cases

### 1. Direct Diagnosis Lookup
**Scenario**: User knows the diagnosis and wants supplemental information
```
Search: "pneumonia"
Result: Shows all pneumonia-related decision trees (Community-Acquired, Hospital-Acquired, etc.)
Action: Click on desired tree to view full diagnostic criteria and management
```

### 2. ICD-10 Code Lookup
**Scenario**: Medical coder needs decision tree for billing code
```
Search: "I21.9"
Result: Acute Myocardial Infarction
Action: View diagnostic criteria and documentation requirements
```

### 3. Browse by Specialty
**Scenario**: Student wants to review all cardiology cases
```
Select Specialty: "CARDIOLOGY"
Result: Shows all cardiology decision trees
Action: Browse and study different cardiac conditions
```

### 4. Partial Search
**Scenario**: User remembers part of diagnosis name
```
Search: "diab"
Result: Shows Diabetes Mellitus Type 1, Type 2, Diabetic Ketoacidosis, etc.
Action: Find specific diabetes-related condition
```

## Technical Notes

### Search Algorithm
- Case-insensitive matching
- Partial string matching supported
- Prioritizes exact ICD-10 matches
- Secondary sort by diagnosis name
- Searches across multiple metadata fields for comprehensive results

### Performance
- Searches all 363 decision trees in memory
- Fast response time (typically <100ms)
- No database queries required
- Uses existing DecisionTreeEngine infrastructure

### Error Handling
- Displays user-friendly error messages on search failure
- Handles empty search results gracefully
- Shows "No results found" message with suggestion to try different terms
- Loading states during API calls

## Future Enhancements (Potential)
- [ ] Auto-complete suggestions as user types
- [ ] Search history/recent searches
- [ ] Favorite/bookmark diagnoses
- [ ] Export search results
- [ ] Advanced filters (by severity, age group, etc.)
- [ ] Search analytics (most searched diagnoses)

## Testing the Feature

### Manual Testing
1. Navigate to `/search` or click "🔍 Diagnosis Search" in navigation
2. Test exact ICD-10 code: `I21.9`
3. Test diagnosis name: `pneumonia`
4. Test partial match: `hyper`
5. Test specialty filter: Select "EMERGENCY"
6. Click on a result to navigate to decision tree
7. Test empty search and no results scenarios

### API Testing
```bash
# Search by diagnosis name
curl "https://realdiag-software.onrender.com/api/search?q=pneumonia"

# Search by ICD-10 code
curl "https://realdiag-software.onrender.com/api/search?q=I21.9"

# Get all families
curl "https://realdiag-software.onrender.com/api/search/families"

# Filter by family
curl "https://realdiag-software.onrender.com/api/search/by-family?family=CARDIOLOGY"
```

## Deployment Status
✅ Backend API deployed to Render
✅ Frontend UI deployed to Netlify
✅ Navigation links added to all pages
✅ Integrated with existing DecisionTreeEngine
✅ Production ready

## Files Modified/Created
- **Created**: `backend/services/search_router.py` - Backend search API
- **Created**: `frontend/pages/search.js` - Frontend search page
- **Modified**: `backend/main.py` - Added search router integration
- **Modified**: `frontend/pages/index.js` - Added navigation link
- **Modified**: `frontend/pages/rules.js` - Added navigation link
- **Modified**: `frontend/pages/education.js` - Added navigation link
- **Modified**: `frontend/pages/symptom-search.js` - Added navigation link
- **Modified**: `frontend/pages/account.js` - Added navigation link
- **Modified**: `frontend/pages/sources.js` - Added navigation link

## Support
For issues or questions about the search feature, check:
1. Browser console for frontend errors
2. Backend logs at Render dashboard for API errors
3. Verify search API endpoints are responding: `/api/search/families`
