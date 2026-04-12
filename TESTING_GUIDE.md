# Quick Start Testing Guide: New Features

## 🚀 Testing the Implementation

### Prerequisites

1. **Backend API must be running:**
   ```bash
   cd ml_backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   ✅ Verify at: http://localhost:8000/docs

2. **Frontend dev server must be running:**
   ```bash
   cd uav-based-flooded-road-assessment-system
   npm run dev
   ```
   ✅ Verify at: http://localhost:3000

---

## Feature 1: Sample Images Gallery

### What to Test

#### Visual Verification
1. Navigate to http://localhost:3000
2. Scroll to "Try the demo" section
3. **Verify:**
   - ✅ Section header: "Upload your own image or click a sample below"
   - ✅ 4 sample image cards visible
   - ✅ Card labels:
     - "Clear Road" with ✅ emoji
     - "Moderate Flood" with ⚠️ emoji
     - "Severe Flood" with 🚫 emoji
     - "With GPS" with ⚠️ emoji
   - ✅ Descriptions under each card
   - ✅ Help text: "Click any sample to run AI classification instantly"

#### Functional Testing

**Test Case 1: Click "Clear Road" Sample**
```
Steps:
1. Click "Clear Road" card
2. Wait for AI processing

Expected Results:
✅ Card highlights with blue border
✅ Checkmark badge appears in top-right corner
✅ "Analyzing image..." spinner shows briefly
✅ After ~3 seconds: Results panel updates
✅ "Real AI prediction" badge shows (green background)
✅ Classification displays (likely "Passable" or "Limited")
✅ Confidence percentage animates (0% → final %)
✅ Vehicle recommendations table populates
✅ Map remains on demo mode (no GPS in this sample)
```

**Test Case 2: Click "Severe Flood" Sample**
```
Steps:
1. Click "Severe Flood" card

Expected Results:
✅ Previous sample deselects (checkmark disappears)
✅ New sample highlights
✅ AI processes again
✅ Classification: "Impassable" (high probability)
✅ All vehicle recommendations: "Blocked" ❌
✅ Red color theme for impassable result
```

**Test Case 3: Click "With GPS" Sample**
```
Steps:
1. Click "With GPS" card

Expected Results:
✅ Sample processes normally
✅ Classification completes
✅ GPS metadata section appears (if EXIF data present)
✅ Map zooms to GPS location
✅ Blue marker appears on map
✅ Coverage circle visualized
```

**Test Case 4: Upload Custom Image After Sample**
```
Steps:
1. Click any sample image
2. Wait for result
3. Click "Upload flood image" and select a file

Expected Results:
✅ Sample selection clears (checkmark disappears)
✅ Sample card no longer highlighted
✅ Custom upload processes normally
✅ Results update with new prediction
```

**Test Case 5: Switch Between Samples Quickly**
```
Steps:
1. Click "Clear Road"
2. Immediately click "Severe Flood" (before AI completes)

Expected Results:
✅ Previous request cancels or completes
✅ Latest sample processes
✅ No double-loading or race conditions
✅ Correct sample is highlighted
```

#### Mobile Responsiveness

**Test on Mobile (375px width):**
```
Steps:
1. Resize browser window to 375px
2. Or use Chrome DevTools device mode

Expected Results:
✅ Sample gallery switches to 2 columns (2×2 grid)
✅ Cards remain clickable
✅ Text remains readable
✅ Emoji icons visible
✅ Hover effects work on touch
```

#### Error Handling

**Test Case: Backend Offline**
```
Steps:
1. Stop backend server (Ctrl+C in terminal)
2. Click any sample image

Expected Results:
✅ Error message displays:
   "Failed to analyze sample image. Please try again."
✅ Sample selection clears
✅ Red error banner visible
✅ User can retry after restarting backend
```

---

## Feature 2: Results Export (JSON Download)

### What to Test

#### Visual Verification

**Test Case 1: Button Visibility - No Prediction**
```
Steps:
1. Fresh page load
2. Scroll to demo section
3. Click "Passable" sample scenario tab (NOT sample image)

Expected Results:
✅ Download button NOT visible
✅ Only sample scenario data shows
✅ "Sample scenario" badge (blue) visible
```

**Test Case 2: Button Visibility - With Prediction**
```
Steps:
1. Click any sample image OR upload custom image
2. Wait for AI prediction
3. Scroll to bottom of results panel

Expected Results:
✅ Download button appears
✅ Label: "Download Results (JSON)"
✅ Icon: Download arrow (📥)
✅ Primary color theme (blue/cyan)
✅ Button is full-width in left panel
✅ Hover effect: Brightens, subtle shadow
```

#### Functional Testing

**Test Case 1: Basic Export**
```
Steps:
1. Upload image or click sample
2. Wait for prediction
3. Click "Download Results (JSON)"

Expected Results:
✅ File downloads immediately
✅ Filename format: flood-assessment-{timestamp}.json
   Example: flood-assessment-1740182794567.json
✅ File saves to default Downloads folder
✅ No errors in browser console
```

**Test Case 2: Verify JSON Structure**
```
Steps:
1. Download results file
2. Open in text editor or JSON viewer

Expected Structure:
{
  "timestamp": "2026-02-22T...",  // ISO 8601 format
  "system": "UAV Flood Assessment System - PLM BSEcE Capstone 2025",

  "prediction": {
    "class": "passable" | "limited_passability" | "impassable",
    "confidence": 0.0 - 1.0,  // Float
    "confidence_level": "High confidence" | ...,
    "probabilities": {
      "passable": 0.0 - 1.0,
      "limited_passability": 0.0 - 1.0,
      "impassable": 0.0 - 1.0
    }
  },

  "vehicle_recommendations": {
    "civilian_sedan": boolean,
    "high_clearance_suv": boolean,
    "heavy_vehicle": boolean,
    "emergency_vehicle": boolean
  },

  "image_metadata": {
    "has_gps": boolean,
    "latitude": number | null,
    "longitude": number | null,
    "latitude_dms": string | null,
    "longitude_dms": string | null,
    "altitude": number | null
  },

  "safety_info": {
    "safety_applied": boolean,
    "safety_reason": string | null,
    "original_prediction": object | null
  },

  "uploaded_image": string  // Filename
}

Validation Checks:
✅ Valid JSON (no syntax errors)
✅ All fields present (no missing keys)
✅ Timestamp is valid ISO 8601
✅ Confidence is between 0.0 and 1.0
✅ Probabilities sum to ~1.0 (within 0.01)
✅ Vehicle recommendations are booleans
✅ GPS data present if image had EXIF
```

**Test Case 3: Multiple Exports (Different Data)**
```
Steps:
1. Upload Image A → Click Download
2. Upload Image B → Click Download
3. Compare JSON files

Expected Results:
✅ Two different files with different timestamps
✅ File A has Image A's prediction data
✅ File B has Image B's prediction data
✅ Timestamps differ by upload time
✅ No data overlap/contamination
```

**Test Case 4: Export After Sample Image**
```
Steps:
1. Click "Moderate Flood" sample
2. Wait for prediction
3. Click Download

Expected Results:
✅ JSON contains real AI prediction
✅ uploaded_image: "moderate-flood.jpg" (sample filename)
✅ Confidence matches displayed value
✅ Vehicle recommendations match UI table
```

**Test Case 5: Export with GPS Metadata**
```
Steps:
1. Click "With GPS" sample OR upload GPS-tagged image
2. Download results

Expected Results:
✅ image_metadata.has_gps: true
✅ latitude/longitude fields populated
✅ latitude_dms/longitude_dms formatted correctly
✅ altitude present (if in EXIF)
```

**Test Case 6: Export with Safety Warning**
```
Steps:
1. Upload image that triggers safety measure
   (e.g., low-confidence prediction)
2. Download results

Expected Results:
✅ safety_info.safety_applied: true
✅ safety_info.safety_reason: <explanation string>
✅ safety_info.original_prediction: { ... }
✅ Main prediction shows conservative classification
```

#### Browser Compatibility

**Test on Multiple Browsers:**
```
Browsers to test:
- Chrome/Edge (Chromium)
- Firefox
- Safari (if on Mac)

Expected Results:
✅ Download works in all browsers
✅ Filename format consistent
✅ File saves to Downloads folder
✅ No security warnings
✅ No popup blockers triggered
```

---

## Integration Testing

### End-to-End Flow

**Test Case: Complete Demo Flow**
```
Steps:
1. Load page
2. Scroll to demo section
3. Observe 4 sample images
4. Click "Clear Road" sample
5. Wait for prediction
6. Review results panel
7. Click download button
8. Open JSON file
9. Click "Severe Flood" sample
10. Download again
11. Compare JSON files

Expected Results:
✅ All 10 steps complete without errors
✅ UI updates smoothly
✅ No console errors
✅ Downloads work correctly
✅ Data integrity maintained
```

**Test Case: Sample → Upload → Sample Flow**
```
Steps:
1. Click sample image → Download results
2. Upload custom image → Download results
3. Click different sample → Download results

Expected Results:
✅ All downloads work
✅ Each JSON has correct data
✅ No state pollution between uploads
✅ Sample selection clears appropriately
```

---

## Performance Testing

### Load Times

**Test Case: Sample Image Click Speed**
```
Steps:
1. Open DevTools Network tab
2. Click sample image
3. Measure time from click to result display

Expected Results:
✅ Sample fetch: < 500ms
✅ AI prediction: ~2-3 seconds (backend dependent)
✅ UI update: < 100ms
✅ Total time-to-result: < 4 seconds
```

**Test Case: Export Speed**
```
Steps:
1. Click download button
2. Measure time to file download

Expected Results:
✅ JSON generation: < 50ms
✅ Download trigger: < 100ms
✅ Total: < 200ms (instant perception)
```

---

## Accessibility Testing

### Keyboard Navigation

**Test Case: Tab Through Interface**
```
Steps:
1. Click in browser address bar
2. Press Tab repeatedly
3. Navigate through sample images and buttons

Expected Results:
✅ Focus order: Header → Samples → Upload → Scenarios → Download
✅ Sample cards have visible focus ring
✅ Enter key activates sample selection
✅ Download button accessible via keyboard
```

### Screen Reader

**Test Case: ARIA Labels (Optional)**
```
Tools: NVDA, JAWS, or VoiceOver

Expected Announcements:
✅ Sample cards: "Clear Road, Minimal water, safe passage, button"
✅ Download button: "Download Results (JSON), button"
✅ Result indicators: "Real AI prediction" or "Sample scenario"
```

---

## Common Issues & Solutions

### Issue 1: Sample Images Not Loading
```
Symptom: 404 error on sample image fetch
Cause: Images not in public/sample-images/
Solution:
  cd uav-based-flooded-road-assessment-system/public
  ls sample-images/  # Verify files exist
  # Should show: passable-road.jpg, limited-flood.jpg, etc.
```

### Issue 2: Download Not Working
```
Symptom: Click download, nothing happens
Cause: Browser popup blocker
Solution:
  - Check browser console for errors
  - Allow popups for localhost:3000
  - Try different browser
```

### Issue 3: AI Prediction Fails
```
Symptom: "Failed to analyze sample image"
Cause: Backend not running
Solution:
  cd ml_backend
  uvicorn app.main:app --reload
  # Verify: http://localhost:8000/docs
```

### Issue 4: Wrong Data in Export
```
Symptom: JSON has stale prediction
Cause: State not updated properly
Solution:
  - Hard refresh (Ctrl+Shift+R)
  - Clear browser cache
  - Check React DevTools state
```

---

## Success Criteria

### All Tests Pass When:

**Sample Images Gallery:**
- ✅ 4 samples visible and clickable
- ✅ Real AI predictions work
- ✅ Selection tracking functions
- ✅ Mobile responsive
- ✅ Error handling works

**Results Export:**
- ✅ Download button appears after prediction
- ✅ JSON file downloads correctly
- ✅ Data structure is valid
- ✅ All metadata included
- ✅ Works across browsers

**Integration:**
- ✅ No console errors
- ✅ Smooth user experience
- ✅ Fast performance
- ✅ Accessible interface

---

## Regression Testing

### Verify Existing Features Still Work

**Test Case: Original Upload Flow**
```
Steps:
1. Click "Upload flood image"
2. Select custom file
3. Wait for prediction

Expected Results:
✅ Works exactly as before
✅ No interference from new features
✅ Map updates correctly
✅ Sample tabs still functional
```

**Test Case: Sample Scenario Tabs**
```
Steps:
1. Click "Passable" tab
2. Click "Limited" tab
3. Click "Impassable" tab

Expected Results:
✅ Tabs switch correctly
✅ Hardcoded demo data shows
✅ "Sample scenario" badge (blue) visible
✅ No download button (no real prediction)
```

---

## Automated Testing (Future)

### Suggested Test Suite

```javascript
// Jest + React Testing Library

describe('Sample Images Gallery', () => {
  it('renders 4 sample images', () => { ... });
  it('selects sample on click', () => { ... });
  it('calls API on sample selection', () => { ... });
  it('clears selection on manual upload', () => { ... });
});

describe('Results Export', () => {
  it('shows download button after prediction', () => { ... });
  it('hides button for sample scenarios', () => { ... });
  it('generates valid JSON on export', () => { ... });
  it('includes all required fields', () => { ... });
});
```

---

## Testing Completion Checklist

### Before Thesis Defense

- [ ] All sample images load correctly
- [ ] Each sample produces valid AI prediction
- [ ] Download button works reliably
- [ ] JSON export has correct structure
- [ ] Mobile responsiveness verified
- [ ] Error handling tested (backend offline)
- [ ] Cross-browser compatibility confirmed
- [ ] No console errors during normal flow
- [ ] Performance is acceptable (<5 sec total)
- [ ] Regression tests pass (old features work)

### Demo Preparation

- [ ] Practice full demo flow 3+ times
- [ ] Prepare backup: Pre-downloaded JSON files
- [ ] Test on presentation laptop/projector
- [ ] Verify internet connection (if cloud-hosted)
- [ ] Have sample images ready (in case of issues)

---

## Quick Reference: Test Commands

```bash
# Start backend
cd ml_backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start frontend
cd uav-based-flooded-road-assessment-system && npm run dev

# Check backend health
curl http://localhost:8000/api/v1/health

# Check frontend
open http://localhost:3000

# View sample images
ls uav-based-flooded-road-assessment-system/public/sample-images/

# Check file sizes
du -h uav-based-flooded-road-assessment-system/public/sample-images/*
```

---

**Testing Guide Version:** 1.0
**Last Updated:** February 22, 2026
**Status:** ✅ Ready for Testing
