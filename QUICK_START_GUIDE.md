# Quick Start Guide - Design Graph Similarity Demo

## ⚡ 3-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
streamlit run app.py
```

### Step 3: Open Browser
The app will automatically open at: `http://localhost:8501`

---

## 🎯 5-Minute Demo Flow (for Slide 26)

### 1. **Introduction** (30 seconds)
- Show the main page
- Explain: "4-channel framework for architectural design similarity"
- Point out: 10 models (ALL10 dataset)

### 2. **Structural Channel Deep Dive** (2 minutes)
- Click through S1-S4 tabs
- **S1**: "Adjacency - topological relationships"
- **S2**: "Motifs - structural patterns like frame nodes"
- **S3**: "System families - Frame, Wall, Dual, Braced" → **Show radar chart** 🎯
- **S4**: "Functional roles - LoadBearing, Shear, etc."
- **S_struct**: "Combined structural similarity"

### 3. **Total Similarity** (1.5 minutes)
- Select a model (e.g., "Building_05_DG.rdf")
- Show top-5 similar models
- Point to **highlighted heatmap** 🎯
- Explain: "Fusion weights: 30% content, 20% typed-edge, 10% edge-sets, 40% structural"

### 4. **Model-Pair Comparison** (1 minute)
- Select two interesting models (e.g., Building03 vs Building04)
- Show channel breakdown
- Highlight: "Different channels capture different aspects"

### 5. **Wrap-up** (30 seconds)
- Scroll to "Interpretation Notes"
- Mention: "All matrices validated, results reproducible"
- Show downloads section

---

## 🔧 Troubleshooting

### App won't start?
```bash
# Check Python version (need 3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Data not loading?
- Check that `/data` and `/thesis_submission_bundle_ALL_2` folders exist
- Verify CSV files are not corrupted
- Press 'C' in the app to clear cache

### Heatmaps not showing?
- Check that PNG files exist in `/data` folder
- App will generate heatmaps if images are missing (slower)

---

## 📊 Key Features

### ✅ What's New in ALL10 Update

- **10 models** (was 5)
- **S1-S4 sub-channels** fully visualized
- **Evidence tables** for transparency
- **Pre-rendered heatmaps** for performance
- **Enhanced model-pair comparison**
- **Matrix verification** built-in
- **Thesis-aligned terminology**

### ✅ What Works

- All similarity matrices load and display
- Interactive radar charts (S3)
- Hierarchical clustering dendrograms
- Quick compare (upload RDF)
- Download all data files
- Matrix validation checks

---

## 📝 Presentation Tips

### Do's ✅
- Start with overview, then dive into S1-S4
- Highlight the **S3 radar chart** (visually striking)
- Show **total similarity heatmap** (clear clusters)
- Explain **fusion weights** (transparency)
- Mention **10 models, 4 channels, 4 sub-channels**

### Don'ts ❌
- Don't skip the structural channel (core contribution)
- Don't forget to explain S1-S4 nomenclature
- Don't rush through the radar chart
- Don't ignore the verification section

### Backup Plan 🛡️
- Have thesis PDF ready
- Screenshot key visualizations
- Prepare to explain without demo if tech fails

---

## 🎓 Key Talking Points

### Why 4 channels?
"Each channel captures a different aspect of design similarity - content, relationships, structure, and patterns."

### Why 40% structural?
"Our analysis shows structural patterns are most discriminative for architectural designs."

### What are motifs?
"Recurring structural patterns like frame nodes (beam-column), wall-slab connections, and cores."

### System families?
"Classification of structural systems: Frame (post-beam), Wall (load-bearing), Dual (combined), Braced (lateral stability)."

### How validated?
"All matrices verified for symmetry, unit diagonal, and [0,1] range. Results reproducible from thesis bundle."

---

## 📞 Quick Reference

### File Locations
- **App:** `app.py`
- **Data:** `data/` (S1-S4 matrices, evidence, heatmaps)
- **Thesis Bundle:** `thesis_submission_bundle_ALL_2/`
- **Docs:** `DEMO_README.md`, `PROJECT_DIAGNOSTIC_REPORT.md`

### Important Numbers
- **Models:** 10 (ALL10 dataset)
- **Channels:** 4 (Content, Typed-Edge, Edge-Sets, Structural)
- **Sub-channels:** 4 (S1, S2, S3, S4)
- **Weights:** 0.3, 0.2, 0.1, 0.4

### Model Names (for reference)
1. 2_Floor_Haus_BuildingArabic05.rdf
2. 2_Floor_Haus_BuildingArabic06.rdf
3. 2_Floor_Haus_Peri.rdf
4. 2_Floor_RevitDemo_StructuralPlan_Building08.rdf
5. 2_Floor_SlopedRoof_Revit-2026.rdf
6. 7_Floor_Individualized Columns_Building04.rdf
7. 8_Floor_Pattern Freeform Columns_Building03.rdf
8. Building_05_DG.rdf
9. Building_06_DG.rdf
10. DFAB_Analog_Building07.rdf

---

## ✅ Pre-Presentation Checklist

- [ ] Test app locally: `streamlit run app.py`
- [ ] Verify all tabs load (S1-S4)
- [ ] Check heatmaps display correctly
- [ ] Test model selection dropdown
- [ ] Try model-pair comparison
- [ ] Open verification section (all ✅?)
- [ ] Practice demo flow (5-7 min)
- [ ] Prepare backup slides
- [ ] Charge laptop, test projector
- [ ] Have thesis PDF ready

---

**Good luck with your presentation! 🎉**

For detailed documentation, see `DEMO_README.md`  
For technical analysis, see `PROJECT_DIAGNOSTIC_REPORT.md`

