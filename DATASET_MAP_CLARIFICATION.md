# Dataset vs Map Visualization: Important Clarification

## ⚠️ Key Point: Training Data ≠ Map Location

You've identified a **critical clarification** that users might find confusing:

### The Situation
- **Training Data:** US hurricane imagery (Florida/Texas 2017-2018)
- **Sample Images:** From RescueNet dataset (Hurricane Harvey/Irma, USA)
- **Map Visualization:** Shows Philippines NCR (Metro Manila) roads

### Why This Matters
1. **Different years:** Training data is from 2017-2018
2. **Different locations:** US floods vs Philippine map
3. **Domain shift:** Model trained on US data, applied to PH context
4. **Potential confusion:** Users might think sample images are from Philippines

---

## ✅ Disclaimers Added

### 1. Sample Images Gallery Header
```
"Quick Test: Sample Images (US Hurricane Data 2017)"
```
- **Clear date:** 2017 (not current)
- **Clear location:** US data

### 2. Sample Images Help Text
```
"Sample images from RescueNet dataset (Hurricane Harvey/Irma, USA 2017).
Click to test AI classification."
```
- **Dataset name:** RescueNet
- **Event:** Hurricane Harvey/Irma
- **Location:** USA
- **Year:** 2017

### 3. Updated Main Disclaimer
```
⚠️ Prototype research system
• Trained on US hurricane data (Florida/Texas 2017-2018)
• Sample images are from USA, map shows Philippines NCR (demo visualization only)
• Expected Philippine accuracy: ~65-70% (domain shift impact)
• For demonstration/research only — not for emergency deployment
```

**New bullet point added:**
> "Sample images are from USA, map shows Philippines NCR (demo visualization only)"

This **explicitly states** the mismatch between data and map.

---

## Why We Show Philippines Map

### Reason 1: Target Deployment Context
- **Research goal:** Assess Philippine flood risk (especially NCR)
- **Map shows:** Where the system WOULD be deployed (if it were production-ready)
- **Not claiming:** These US samples are Philippine floods

### Reason 2: Demonstrate Localization Potential
- Shows how the system could be integrated with local GIS data
- Demonstrates Philippine road network visualization
- Maps to local context (Tondo/Navotas flood-prone areas)

### Reason 3: Educational/Demo Purpose
- **The map is a DEMO VISUALIZATION**, not claiming to show actual flood locations
- Demonstrates potential user interface for emergency responders in Philippines
- Shows scalability to different geographic contexts

---

## What Users Should Understand

### ✅ Clear Facts
1. **Training data:** US hurricanes 2017-2018 (Florida/Texas)
2. **Sample images:** Also from US (Hurricane Harvey/Irma)
3. **AI model:** Trained on US data, being TESTED for Philippine applicability
4. **Map:** Hypothetical deployment visualization (Philippines NCR)
5. **Accuracy:** Expected to drop from 79.6% (US) to ~65-70% (PH) due to domain shift

### ❌ What We're NOT Claiming
- ❌ These are Philippine flood images
- ❌ The map shows actual flood events
- ❌ The system is currently deployed in Philippines
- ❌ The accuracy will be the same in Philippine context

---

## Thesis Defense Explanation

### If Asked: "Why use US data with Philippine map?"

**Answer:**
> "Great question! This is a **proof-of-concept** research project. We used publicly available US datasets (RescueNet, FloodNet) because Philippine aerial flood datasets don't exist yet. The map shows the National Capital Region because that's the **target deployment context** where this system could help address flooding issues like in Tondo/Navotas. The ~65-70% expected Philippine accuracy reflects the domain shift we anticipate when applying US-trained models to Philippine conditions. Future work would involve collecting Philippine flood imagery to improve local accuracy."

### If Asked: "Aren't the sample images misleading?"

**Answer:**
> "We've added clear disclaimers:
> 1. Gallery header states 'US Hurricane Data 2017'
> 2. Help text specifies 'RescueNet dataset (Hurricane Harvey/Irma, USA 2017)'
> 3. Main disclaimer explicitly states: 'Sample images are from USA, map shows Philippines NCR (demo visualization only)'
>
> The samples are for **technical demonstration** of the AI classification pipeline, not to represent actual Philippine floods. Users can upload their own Philippine flood images to test real-world applicability."

---

## Additional Context in Other Sections

### Technology Section
Already states:
> "Dataset context: Model trained on US hurricane/flood imagery (RescueNet + FloodNet: 4,892 images)."

### About Section
Already states:
> "proof-of-concept using deep learning trained on US hurricane datasets"

### Hero Section
Already states:
> "Test accuracy (US data)"

### Features Section
Already states:
> "79.6% test accuracy (US data)"

**Conclusion:** The frontend is **consistently transparent** about using US data throughout.

---

## Recommendations for Clarity

### ✅ Already Implemented
1. ✅ Gallery header mentions "US Hurricane Data 2017"
2. ✅ Help text specifies dataset and location
3. ✅ Main disclaimer has explicit bullet about data/map mismatch
4. ✅ Multiple sections note "US data" accuracy

### Optional Additional Clarifications

#### Option 1: Add Tooltip on Map
```typescript
// In FloodMap.tsx, add info icon with tooltip
<div className="absolute top-4 right-4 bg-card/90 p-2 rounded-lg border border-border text-xs">
  ℹ️ Demo visualization (NCR roads)
</div>
```

#### Option 2: Add Note Above Map
```typescript
// In AssessmentDemo.tsx, above map component
<div className="text-xs text-muted-foreground mb-2">
  Map shows sample NCR roads (demo visualization)
</div>
```

#### Option 3: Footer Attribution
```typescript
// In Footer.tsx
<p className="text-xs">
  Training data: RescueNet/FloodNet (USA 2017-2018) |
  Map: Philippines NCR (demo context)
</p>
```

**Recommendation:** Current disclaimers are sufficient. Adding more might clutter the UI.

---

## Why This Is Actually GOOD Design

### Academic Integrity ✅
- **Transparent about limitations** (domain shift, accuracy drop)
- **Clear about data sources** (US datasets)
- **Honest about prototype status** (not production-ready)

### Demonstrates Understanding ✅
- Shows awareness of **transfer learning challenges**
- Acknowledges **domain adaptation** issues
- Realistic about **real-world deployment** considerations

### Research Contribution ✅
- Proves concept feasibility with existing datasets
- Identifies need for Philippine flood imagery
- Establishes baseline for future local training

---

## Data Flow Summary

```
┌────────────────────────────────────────────────────┐
│ TRAINING DATA (2017-2018)                          │
│ • RescueNet: Hurricane Harvey/Irma (Florida/Texas)│
│ • FloodNet: Various US hurricane events            │
│ • 4,892 images total                              │
│ • 79.6% test accuracy (US validation set)         │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ AI MODEL (EfficientNet-B0)                         │
│ • Trained on US data                               │
│ • 3 classes: Passable, Limited, Impassable        │
│ • ONNX deployment format                          │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ SAMPLE IMAGES (for demo)                           │
│ • Also from RescueNet (Hurricane Harvey/Irma)     │
│ • 3 examples: Clear, Moderate, Severe             │
│ • Purpose: Test AI pipeline without upload        │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ MAP VISUALIZATION (demo context)                   │
│ • Philippines NCR roads                           │
│ • Tondo/Navotas area (flood-prone)                │
│ • Shows WHERE system could be deployed            │
│ • NOT claiming to show actual flood locations     │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│ FUTURE WORK                                        │
│ • Collect Philippine flood aerial imagery         │
│ • Retrain model on local data                     │
│ • Validate on Philippine flood events             │
│ • Improve accuracy to >80% for local context      │
└────────────────────────────────────────────────────┘
```

---

## Comparison: Good vs Bad Approaches

### ❌ BAD: Misleading Approach
- Hide dataset origin
- Pretend samples are Philippine floods
- Show map without clarification
- Claim high accuracy for Philippine use
- No disclaimers about domain shift

### ✅ GOOD: Your Current Approach
- **Transparent disclaimers** everywhere
- **Clear dataset attribution** (RescueNet/FloodNet)
- **Explicit about data/map mismatch**
- **Realistic accuracy expectations** (65-70% for PH)
- **Honest about prototype status**

**Your approach demonstrates academic integrity and research rigor.** ✅

---

## Final Verdict

### Is the current implementation appropriate?
**YES ✅**

### Are the disclaimers sufficient?
**YES ✅** - Multiple layers:
1. Gallery header: "US Hurricane Data 2017"
2. Help text: "RescueNet dataset (Hurricane Harvey/Irma, USA 2017)"
3. Main disclaimer: "Sample images are from USA, map shows Philippines NCR (demo visualization only)"
4. Technology section: "Model trained on US hurricane/flood imagery"
5. Multiple "US data" accuracy mentions

### Could users still be confused?
**Low risk** - The disclaimers are prominent and repeated throughout the interface.

### What if a panelist asks about this during defense?
**You're well-prepared** - The disclaimers show you've thought about this issue and addressed it proactively.

---

## For Thesis Defense: Key Points

### 1. Acknowledge the Limitation Upfront
> "This is a proof-of-concept trained on US hurricane data (2017-2018). The map shows Philippines NCR as the target deployment context, but the sample images are from US hurricanes to demonstrate the AI pipeline."

### 2. Explain the Rationale
> "We used publicly available US datasets (RescueNet, FloodNet) because there are no comparable Philippine aerial flood datasets. This establishes a baseline and proves the concept is technically feasible."

### 3. Highlight the Transparency
> "We've been explicit about this throughout the interface with multiple disclaimers, and we estimate accuracy will drop to 65-70% in Philippine context due to domain shift."

### 4. Propose Future Work
> "Future research should collect Philippine flood aerial imagery to retrain the model and improve local accuracy to >80%."

---

## Conclusion

**You've correctly identified a potential source of confusion**, and the implementation now addresses it with:
- ✅ Clear dataset labeling
- ✅ Explicit data/map mismatch disclaimer
- ✅ Consistent "US data" mentions throughout
- ✅ Honest accuracy expectations for Philippine context

**This demonstrates research maturity and academic integrity** - exactly what thesis committees want to see.

---

**Document created:** February 22, 2026
**Issue:** Clarify dataset origin vs map location
**Status:** ✅ Resolved with comprehensive disclaimers
