# Hurricane Dataset Correction: Michael (2018) vs Harvey (2017)

## ⚠️ Important Correction Made

After verifying with official sources, we corrected the hurricane information in all frontend disclaimers.

---

## What Was Wrong

**BEFORE (Incorrect):**
- Disclaimers said: "Hurricane Harvey/Irma, 2017"
- Sample gallery header: "US Hurricane Data 2017"
- Implied RescueNet was from Harvey/Irma

**Why This Was Wrong:**
- RescueNet dataset is actually from **Hurricane Michael (2018)**, NOT Harvey
- Hurricane Michael: Category 5, Mexico Beach Florida, October 10, 2018
- Hurricane Harvey: Different hurricane, Texas, August 2017 (FloodNet dataset)

---

## What Was Corrected

### ✅ Frontend Files Updated

#### 1. AssessmentDemo.tsx (Main Demo Section)

**Sample Gallery Header:**
```typescript
// BEFORE:
"Quick Test: Sample Images (US Hurricane Data 2017)"

// AFTER:
"Quick Test: Sample Images (Hurricane Michael 2018)"
```

**Sample Gallery Help Text:**
```typescript
// BEFORE:
"Sample images from RescueNet dataset (Hurricane Harvey/Irma, USA 2017)"

// AFTER:
"Sample images from RescueNet dataset (Hurricane Michael, USA 2018)"
```

**Main Disclaimer Banner:**
```typescript
// BEFORE:
"Trained on US hurricane data (2017-2018, not current conditions)"
"Sample images from USA 2017, map shows Philippines NCR (demo only)"

// AFTER:
"Trained on US hurricane data (Hurricane Michael 2018, not current conditions)"
"Sample images from USA 2018, map shows Philippines NCR (demo only)"
```

#### 2. public/sample-images/README.md

**Dataset Attribution:**
```markdown
// BEFORE:
- Source: RescueNet Classification Dataset (Hurricane Harvey & Irma, 2017)
- Citation: Rahnemoonfar, M., et al. (2021)

// AFTER:
- Source: RescueNet Classification Dataset (Hurricane Michael, Florida 2018)
- Citation: Rahnemoonfar, M., et al. (2023)
- License: Creative Common License CC BY-NC-ND
```

#### 3. DATASET_SOURCES.md

**RescueNet Section:**
- Updated all references from "Harvey/Irma 2017" to "Hurricane Michael 2018"
- Added collection dates: October 11-14, 2018
- Added location: Mexico Beach, Florida area
- Corrected citation year: 2023 (not 2021)
- Added DOI: 10.1038/s41597-023-02799-4

---

## The Correct Information

### RescueNet Dataset
- **Hurricane:** Michael (Category 5)
- **Date:** October 10, 2018 (landfall)
- **Collection:** October 11-14, 2018
- **Location:** Mexico Beach, Florida area
- **Images:** 4,494 high-resolution UAV images
- **Published:** 2023 (Nature Scientific Data)

### FloodNet Dataset
- **Hurricane:** Harvey (Category 4)
- **Date:** August 25, 2017 (landfall)
- **Location:** Texas
- **Images:** 2,343 high-resolution UAV images
- **Published:** 2020 (IEEE Access)

### Our Training Data
We used **both datasets** for training:
- RescueNet: Hurricane Michael 2018 (Florida)
- FloodNet: Hurricane Harvey 2017 (Texas)
- Combined: ~6,800 images total
- Final training set: 4,892 images (after filtering/balancing)

---

## Why This Confusion Happened

**Common Misconceptions:**
1. Both datasets come from BinaLab (same research group)
2. Both are flood/disaster aerial imagery
3. Both were published close together (2020-2023)
4. Documentation sometimes groups them as "US hurricane datasets 2017-2018"
5. RescueNet paper references FloodNet (Harvey), causing confusion

**The Truth:**
- RescueNet = Hurricane Michael (2018, Florida)
- FloodNet = Hurricane Harvey (2017, Texas)
- We used BOTH in training, but sample images are from RescueNet only

---

## Impact on Project

### Does This Change Anything?

**NO - No Impact on:**
- ✅ Model accuracy (still trained on same data)
- ✅ Sample images (still from RescueNet)
- ✅ Deployment (backend unchanged)
- ✅ Thesis conclusions (data source documented correctly now)

**YES - Improves:**
- ✅ **Accuracy of disclaimers** (now factually correct)
- ✅ **Academic integrity** (proper attribution)
- ✅ **Citation accuracy** (correct year, DOI, hurricane)
- ✅ **Thesis defense** (no factual errors when questioned)

---

## Updated Timeline

```
August 2017:
└─ Hurricane Harvey (Texas)
   └─ FloodNet dataset collected
   └─ Published: 2020 (IEEE Access)

October 2018:
└─ Hurricane Michael (Florida)
   └─ RescueNet dataset collected
   └─ Published: 2023 (Nature Scientific Data)

2024-2025:
└─ Our Project (PLM BSEcE Capstone)
   └─ Used BOTH datasets for training
   └─ Sample images: RescueNet only (Michael 2018)
```

---

## For Thesis Defense

### If Asked: "What hurricanes were your datasets from?"

**CORRECT Answer:**
> "We used two datasets for training:
> 1. **RescueNet** - Hurricane Michael (October 2018, Florida) - 4,494 images
> 2. **FloodNet** - Hurricane Harvey (August 2017, Texas) - 2,343 images
>
> The sample images in the demo are from RescueNet (Hurricane Michael 2018). Combined, we had ~6,800 images, filtered to 4,892 for final training."

### If Asked: "Why do your disclaimers say 2018?"

**CORRECT Answer:**
> "The RescueNet dataset, which provides our demo sample images, was collected after Hurricane Michael in October 2018. We also used FloodNet (Hurricane Harvey 2017) for training, but the visible sample images are specifically from the 2018 Hurricane Michael dataset."

---

## Verification Sources

**All information verified from:**
- [Nature Scientific Data Paper](https://www.nature.com/articles/s41597-023-02799-4)
- [RescueNet GitHub](https://github.com/BinaLab/RescueNet-A-High-Resolution-Post-Disaster-UAV-Dataset-for-Semantic-Segmentation)
- [FloodNet IEEE Paper](https://ieeexplore.ieee.org/document/9460988/)
- [BinaLab Official Sources](https://www.binatech.ai/)

**Web search conducted:** February 22, 2026
**All links verified:** ✅ Active and accessible

---

## Files Updated

### Frontend:
- ✅ `components/sections/AssessmentDemo.tsx` (3 locations)
- ✅ `public/sample-images/README.md` (2 locations)

### Documentation:
- ✅ `DATASET_SOURCES.md` (comprehensive update)
- ✅ `HURRICANE_CORRECTION.md` (this file)

### Backend:
- ❌ No changes needed (model unchanged, training data same)

---

## Checklist for Thesis Document

**Make sure your thesis mentions:**
- [ ] RescueNet: Hurricane Michael (October 2018, Florida)
- [ ] FloodNet: Hurricane Harvey (August 2017, Texas)
- [ ] Combined dataset: ~6,800 images from both hurricanes
- [ ] Sample images: Specifically from RescueNet (Michael 2018)
- [ ] Citation: Rahnemoonfar et al., 2023 (Nature Scientific Data)
- [ ] Training period: 2017-2018 hurricane seasons (both datasets)

---

## Summary

**What Changed:**
- ✅ Corrected hurricane name (Harvey → Michael)
- ✅ Corrected year (2017 → 2018) for RescueNet
- ✅ Updated citations (2021 → 2023, added DOI)
- ✅ Clarified dataset sources in all disclaimers

**Why It Matters:**
- ✅ Factual accuracy for thesis defense
- ✅ Proper academic attribution
- ✅ Avoids confusion during Q&A

**Impact:**
- ✅ No functional changes to system
- ✅ Improved documentation accuracy
- ✅ Better prepared for thesis defense

---

**Correction completed:** February 22, 2026
**Status:** ✅ All frontend disclaimers now accurate
**Verified by:** Web search of official sources (Nature, IEEE, GitHub)
