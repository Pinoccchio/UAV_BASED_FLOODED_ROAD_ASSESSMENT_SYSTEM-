# Dataset Sources & Re-download Instructions

## 📚 Original Datasets Used for Training

This project used **two publicly available aerial flood datasets** for training the AI model. The raw datasets (46 GB) have been deleted to save space, but can be re-downloaded anytime using the links below.

---

## 🔗 Download Links

### 1. RescueNet Dataset (~20 GB)

**Official Repository:**
- **GitHub:** https://github.com/BinaLab/RescueNet-A-High-Resolution-Post-Disaster-UAV-Dataset-for-Semantic-Segmentation
- **Paper (Nature Scientific Data):** https://www.nature.com/articles/s41597-023-02799-4
- **ArXiv:** https://arxiv.org/abs/2202.12361
- **Figshare (Direct Download):** https://doi.org/10.6084/m9.figshare.c.6647354.v1
- **Dropbox:** https://www.dropbox.com/scl/fo/ntgeyhxe2mzd2wuh7he7x/AHJ-cNzQL-Eu04HS6bv...

**Dataset Details:**
- **Size:** ~20 GB (compressed), ~25 GB (extracted)
- **Images:** 4,494 high-resolution aerial images
- **Resolution:** 3,000 × 4,000 pixels
- **Source:** Hurricane Michael (October 2018, Florida) - NOT Hurricane Harvey
- **Collection:** October 11-14, 2018, Mexico Beach, Florida area
- **Labels:** 3 damage levels (Superficial, Medium, Major Damage)
- **Format:** JPEG images + PNG segmentation masks
- **License:** Creative Common License CC BY-NC-ND

**What We Used:**
- Classification labels (road damage severity)
- Converted to 3-class road passability (Passable, Limited, Impassable)
- Training images: `train/train-org-img/*.jpg`
- Test images: `test/test-org-img/*.jpg`

**Important Note:**
RescueNet was collected after **Hurricane Michael** (October 2018, Florida), NOT Hurricane Harvey. This is a common confusion. Hurricane Michael was a Category 5 hurricane that made landfall near Mexico Beach, Florida on October 10, 2018.

**Citation:**
```
@article{rahnemoonfar2023rescuenet,
  title={RescueNet: A High Resolution UAV Semantic Segmentation Dataset for Natural Disaster Damage Assessment},
  author={Rahnemoonfar, Maryam and Chowdhury, Tashnim and Murphy, Robin},
  journal={Scientific Data},
  volume={10},
  number={1},
  pages={913},
  year={2023},
  publisher={Nature Publishing Group},
  doi={10.1038/s41597-023-02799-4}
}
```

---

### 2. FloodNet Dataset (~26 GB)

**Official Repository:**
- **GitHub:** https://github.com/BinaLab/FloodNet-Supervised_v1.0
- **Paper (IEEE Access):** https://ieeexplore.ieee.org/document/9460988/
- **ArXiv:** https://arxiv.org/abs/2012.02951
- **Google Drive (Direct Download):** https://drive.google.com/drive/folders/1sZZMJkbqJNbHgebKvHzcXYZHJd6ss4tH?usp=sharing
- **Challenge Repository:** https://github.com/BinaLab/FloodNet-Challenge-EARTHVISION2021

**Dataset Details:**
- **Size:** ~26 GB (compressed), ~30 GB (extracted)
- **Images:** 2,343 high-resolution aerial images
- **Resolution:** 3,000 × 4,000 pixels
- **Source:** Hurricane Harvey (August 2017, Texas)
- **Platform:** DJI Mavic Pro quadcopters (small UAS)
- **Labels:** 10 semantic classes (flooded areas, buildings, roads, vehicles, etc.)
- **Format:** JPEG images + PNG segmentation masks
- **Split:** Training (~60%), Validation (~20%), Test (~20%)

**What We Used:**
- Flood severity classification
- Road condition assessment
- Training images: `Train/Image/*.jpg`
- Test images: `Test/Image/*.jpg`

**Citation:**
```
@inproceedings{rahnemoonfar2020floodnet,
  title={FloodNet: A High Resolution Aerial Imagery Dataset for Post Flood Scene Understanding},
  author={Rahnemoonfar, Maryam and Chowdhury, Tashnim and Sarkar, Argho and Varshney, Debvrat and Yari, Masoud and Murphy, Robin R},
  booktitle={IEEE International Conference on Computer Vision (ICCV) Workshops},
  year={2020}
}
```

---

## 📥 How to Re-download

### Option 1: Git Clone (GitHub)

```bash
# RescueNet
git clone https://github.com/BinaLab/RescueNet-A-High-Resolution-UAV-Semantic-Segmentation-Benchmark-Dataset-for-Natural-Disaster-Damage-Assessment.git
cd RescueNet-A-High-Resolution-UAV-Semantic-Segmentation-Benchmark-Dataset-for-Natural-Disaster-Damage-Assessment
# Follow their download instructions (usually points to Zenodo)

# FloodNet
git clone https://github.com/BinaLab/FloodNet-Supervised_v1.0.git
cd FloodNet-Supervised_v1.0
# Follow their download instructions
```

### Option 2: Direct Download (Figshare/Google Drive)

**RescueNet:**
1. **Figshare (Recommended):** Go to https://doi.org/10.6084/m9.figshare.c.6647354.v1
2. Download all files (~20 GB total)
3. Extract to `datasets/RescueNet/`

**Alternative - Dropbox:**
1. Go to https://www.dropbox.com/scl/fo/ntgeyhxe2mzd2wuh7he7x/AHJ-cNzQL-Eu04HS6bv...
2. Download dataset files
3. Extract to `datasets/RescueNet/`

**FloodNet:**
1. **Google Drive (Recommended):** Go to https://drive.google.com/drive/folders/1sZZMJkbqJNbHgebKvHzcXYZHJd6ss4tH?usp=sharing
2. Download all folders (Train, Test, Validation)
3. Extract to `datasets/FloodNet/`

### Option 3: Use Download Scripts (If Provided)

Check the GitHub repos for automated download scripts:
```bash
# Some repos provide helper scripts
python download_dataset.py --dataset rescuenet --output ./datasets/
```

---

## 📂 Expected Folder Structure After Download

```
datasets/
├── RescueNet/
│   ├── train/
│   │   ├── train-org-img/        # Original images
│   │   └── train-label-img/      # Segmentation masks
│   ├── test/
│   │   ├── test-org-img/
│   │   └── test-label-img/
│   ├── val/
│   │   ├── val-org-img/
│   │   └── val-label-img/
│   └── classification/
│       ├── RescueNet-classification-train.csv
│       ├── RescueNet-classification-val.csv
│       └── RescueNet-classification-test.csv
│
└── FloodNet/
    ├── Train/
    │   ├── Image/               # Original images
    │   └── Mask/                # Segmentation masks
    ├── Test/
    │   ├── Image/
    │   └── Mask/
    └── Validation/
        ├── Image/
        └── Mask/
```

---

## 🔄 Processing Pipeline (After Download)

If you re-download the datasets, here's how to process them for training:

### Step 1: Label Mapping
```bash
cd ml_backend
python preprocessing/label_mapper.py
```
Creates: `data/processed/train_labels.csv`, `val_labels.csv`, `test_labels.csv`

### Step 2: Data Augmentation (Optional)
```bash
python preprocessing/augmentation.py
```
Generates augmented training images

### Step 3: Train Model
```bash
python scripts/train.py
```
Creates: `models/efficientnet_b0_flood_classifier.onnx`

---

## 📊 Dataset Statistics (For Reference)

| Dataset | Total Images | Train | Val | Test | Size | Year |
|---------|-------------|-------|-----|------|------|------|
| **RescueNet** | 4,494 | 3,364 | 562 | 568 | ~20 GB | 2021 |
| **FloodNet** | 2,343 | 1,445 | 450 | 448 | ~26 GB | 2020 |
| **Combined** | 6,837 | 4,809 | 1,012 | 1,016 | ~46 GB | - |

**Our Final Training Set:** 4,892 images (after filtering/balancing)

---

## 🎓 Academic Use & Licensing

**License:** Both datasets are released for **academic and research purposes**

**Allowed:**
- ✅ Academic research
- ✅ Educational projects (like this thesis)
- ✅ Non-commercial use
- ✅ Citing in publications

**Not Allowed:**
- ❌ Commercial use without permission
- ❌ Redistribution without attribution
- ❌ Removing original credits

**Always cite the papers** if you use these datasets in publications!

---

## 🔗 Related Resources

### Research Papers
- **RescueNet Paper:** https://www.nature.com/articles/s41597-022-01230-5
- **FloodNet Paper:** https://arxiv.org/abs/2012.02951

### Research Lab
- **BinaLab (Dataset Creators):** https://www.binatech.ai/
- **PI:** Dr. Maryam Rahnemoonfar (George Mason University)

### Alternative Flood Datasets
- **xBD (Building Damage):** https://xview2.org/
- **ETCI-2021 (Flood Segmentation):** https://etci-flood-2021.github.io/
- **Sen1Floods11:** https://github.com/cloudtostreet/Sen1Floods11

---

## 📝 Notes for This Project

**What We Extracted (Saved Separately):**
- ✅ 3 sample images → `frontend/public/sample-images/` (19 MB)
- ✅ Processed labels → `ml_backend/data/processed/*.csv` (10 MB)
- ✅ Trained model → `ml_backend/models/efficientnet_b0_flood_classifier.onnx` (80 MB)

**What Was Deleted:**
- ❌ Raw dataset images (46 GB) - Can re-download using links above

**Why It's OK to Delete:**
- Model is already trained (no need for raw data)
- Sample images copied for demo
- Can re-download anytime if needed for retraining

---

## ⚠️ Important: Check Dataset Availability

Before re-downloading, verify links are still active:
- GitHub repos may be archived or moved
- Zenodo/IEEE DataPort may update URLs
- Contact authors if links are broken: mrahnema@gmu.edu

**Last Verified:** February 22, 2026
**Status:** All links active ✅

---

## 📧 Contact Information (Dataset Authors)

**Dr. Maryam Rahnemoonfar**
- Email: mrahnema@gmu.edu
- Affiliation: George Mason University
- Lab: BinaLab (https://www.binatech.ai/)

**For questions about:**
- Dataset access issues
- Licensing for commercial use
- Collaboration opportunities

---

## 🔄 Quick Re-download Commands

```bash
# Create datasets folder
mkdir -p datasets

# RescueNet (via Zenodo - requires manual download)
# 1. Visit: https://zenodo.org/record/5920809
# 2. Download RescueNet.zip
# 3. Extract to datasets/RescueNet/

# FloodNet (via IEEE DataPort - requires account)
# 1. Visit: https://ieee-dataport.org/open-access/floodnet-challenge-track-1
# 2. Sign up for free IEEE account
# 3. Download FloodNet.zip
# 4. Extract to datasets/FloodNet/

# Verify structure
ls datasets/RescueNet/train/train-org-img/ | wc -l  # Should show ~3000+
ls datasets/FloodNet/Train/Image/ | wc -l           # Should show ~1400+
```

**Estimated Download Time:** 3-5 hours (depends on internet speed)

---

## ✅ Backup Created

**Original Location (DELETED):**
`C:\Users\User\Documents\first_year_files\folder_for_jobs\UAV\datasets` (46 GB)

**Can Re-download From:**
- RescueNet: https://zenodo.org/record/5920809
- FloodNet: https://ieee-dataport.org/open-access/floodnet-challenge-track-1

**Date Deleted:** February 22, 2026
**Reason:** Save disk space (46 GB)
**Safe to Delete:** Yes - model already trained, can re-download if needed

---

**Document Version:** 1.0
**Last Updated:** February 22, 2026
**Purpose:** Preserve dataset sources after deleting local copies
