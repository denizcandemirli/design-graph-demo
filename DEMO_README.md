# Design Graph Similarity Demo - ALL10 Dataset

## 📋 Overview

This Streamlit web application demonstrates the **4-channel similarity framework** applied to 10 architectural design graphs (ALL10 dataset) for a TUM Master Thesis.

The framework computes comprehensive design similarity by combining:
- **Content Channel** (30%): Semantic content distribution
- **Typed-Edge Channel** (20%): Predicate-specific relationships
- **Edge-Sets Channel** (10%): Structural overlap
- **Structural Channel** (40%): Decomposed into 4 sub-channels (S1-S4)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip or conda

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd design-graph-demo
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser:**
   The app will automatically open at `http://localhost:8501`

---

## 📁 Project Structure

```
design-graph-demo/
├── app.py                              # Main Streamlit application (UPDATED)
├── requirements.txt                    # Python dependencies
├── DEMO_README.md                      # This file
│
├── data/                               # NEW ALL10 analysis results
│   ├── adjacency_evidence.csv          # S1: Adjacency counts
│   ├── functional_roles_evidence.csv   # S4: Functional roles
│   ├── motif_evidence.json             # S2: Motif detection
│   ├── S1_adjacency_similarity.csv     # S1 similarity matrix
│   ├── S2_motif_similarity.csv         # S2 similarity matrix
│   ├── S3_system_similarity.csv        # S3 similarity matrix
│   ├── S4_functional_similarity.csv    # S4 similarity matrix
│   ├── S_struct_fused_similarity.csv   # Fused structural similarity
│   ├── total_similarity_heatmap.png    # Final heatmap
│   ├── total_similarity_heatmap_highlighted.png
│   ├── S3_system_similarity_heatmap.png
│   └── S4_functional_similarity_heatmap.png
│
├── thesis_submission_bundle_ALL_2/     # Authoritative thesis results
│   ├── CHANNEL_MATRICES/               # Per-channel similarity matrices
│   │   ├── total_similarity_matrix.csv
│   │   ├── content_similarity_matrix.csv
│   │   ├── typed_edge_similarity_matrix.csv
│   │   ├── edge_sets_similarity_matrix.csv
│   │   ├── structural_similarity_matrix.csv
│   │   ├── pairwise_total_summary.csv
│   │   └── weights_used.json
│   │
│   ├── STRUCTURAL_PIPELINE/            # S1-S4 sub-channel results
│   │   ├── s1_inventory.csv
│   │   ├── s2_motifs.csv
│   │   ├── s3_system_scores.csv
│   │   ├── s4_motif_share_vectors.csv
│   │   └── struct_similarity_s1s4.csv
│   │
│   ├── FIGURES/                        # Visualizations
│   ├── FUSION/                         # Model list
│   └── README_FOR_SUPERVISOR_ALL10.md
│
└── *.rdf                               # RDF design graph models (10 models)
    ├── 2_Floor_Haus_BuildingArabic05.rdf
    ├── 2_Floor_Haus_BuildingArabic06.rdf
    ├── 2_Floor_Haus_Peri.rdf
    ├── 2_Floor_RevitDemo_StructuralPlan_Building08.rdf
    ├── 2_Floor_SlopedRoof_Revit-2026.rdf
    ├── 7_Floor_Individualized Columns_Building04.rdf
    ├── 8_Floor_Pattern Freeform Columns_Building03.rdf
    ├── Building_05_DG.rdf
    ├── Building_06_DG.rdf
    └── DFAB_Analog_Building07.rdf
```

---

## 🎯 Features & Usage

### 1. **Structural Channel Deep Dive (S1→S4)**

Navigate through tabs to explore each structural sub-channel:

- **S1: Adjacency** - Topological relationships (adjacentElement, adjacentZone)
- **S2: Motifs** - Structural patterns (frame nodes, wall-slab, cores, braces)
- **S3: System Families** - Frame, Wall, Dual, Braced system scores with radar charts
- **S4: Functional Roles** - LoadBearing, Shear, Moment, Bracing annotations
- **S_struct Fused** - Combined structural similarity

Each tab displays:
- Evidence tables (counts, scores)
- Similarity matrices (heatmaps)
- Dendrograms (hierarchical clustering)

### 2. **Total Similarity (Final Fusion)**

- Select a model to view its top-N most similar models
- View channel breakdown (Content, Typed-Edge, Edge-Sets, Structural)
- Explore total similarity heatmap (highlighted version)
- Analyze hierarchical clustering dendrogram

### 3. **Model-Pair Comparison**

- Select two models (A and B)
- Compare across all channels and sub-channels
- View similarity scores in table and bar chart format

### 4. **Quick Compare (Content-Only)**

- Upload a new RDF file
- Get instant content-based similarity ranking
- Fast approximation without full graph analysis

### 5. **Verification & Diagnostics**

- Matrix validation (symmetry, unit diagonal, [0,1] range)
- Health check for all similarity matrices

### 6. **Downloads**

Download all data files:
- Similarity matrices (CSV)
- Evidence tables (CSV)
- Visualizations (PNG)
- Structural pipeline outputs

---

## 📊 Data Sources

### Primary Data (`/data` folder)
Contains the **latest ALL10 analysis results** used by the demo:
- Generated from the updated structural pipeline
- Includes all S1-S4 sub-channels
- Pre-rendered heatmaps for performance

### Thesis Bundle (`/thesis_submission_bundle_ALL_2`)
Contains the **authoritative thesis submission results**:
- Used as ground truth reference
- Includes all channel matrices
- Contains pairwise summaries and weights

**The demo prioritizes `/data` for visualization but validates against the thesis bundle.**

---

## 🔧 Configuration

### Fusion Weights

The framework uses these weights (defined in `app.py`):

```python
FUSION_W = {
    "content": 0.30,
    "typed": 0.20,
    "edge": 0.10,
    "struct": 0.40
}
```

These match the thesis submission bundle (`weights_used.json`).

### Top-N Results

Adjustable via sidebar slider (default: 5, range: 3-10)

---

## 🎓 Thesis Context

### Research Question
How can we quantify similarity between architectural design graphs to support design space exploration and retrieval?

### Approach
A **4-channel similarity framework** that combines:
1. Semantic content (predicates)
2. Typed relationships (predicate-specific edges)
3. Structural overlap (edge sets)
4. Structural patterns (adjacency, motifs, systems, roles)

### Dataset (ALL10)
10 architectural models varying in:
- Complexity (2-8 floors)
- Structural systems (frame, wall, dual, braced)
- Design tools (Revit, Grasshopper, custom)
- Semantic richness (functional annotations)

### Key Findings
- **High structural similarity** across models (S_struct > 0.80)
- **Adjacency patterns** highly consistent (S1 > 0.95)
- **System families** dominated by wall systems
- **Functional roles** present in 9/10 models
- **Total similarity** reveals meaningful clusters

---

## 🔄 Updating the Demo

### Adding New Models

1. **Add RDF files** to the root directory
2. **Run the analysis pipeline** (see thesis scripts)
3. **Update data files** in `/data` folder:
   - Regenerate all S1-S4 matrices
   - Update evidence tables
   - Regenerate total similarity matrix
4. **Restart the Streamlit app**

### Modifying Weights

1. **Edit `FUSION_W`** in `app.py` (line 26)
2. **Recompute total similarity** using the pipeline
3. **Update** `thesis_submission_bundle_ALL_2/CHANNEL_MATRICES/weights_used.json`
4. **Restart the app**

### Adding New Visualizations

1. **Generate images** (PNG format recommended)
2. **Save to** `/data` folder
3. **Add display code** in relevant section of `app.py`
4. **Use `st.image()` or matplotlib/plotly**

---

## 🐛 Troubleshooting

### App won't start
- **Check Python version:** `python --version` (requires 3.9+)
- **Reinstall dependencies:** `pip install -r requirements.txt --upgrade`
- **Check port availability:** Default is 8501

### Data not loading
- **Verify file paths:** Check that `/data` and `/thesis_submission_bundle_ALL_2` exist
- **Check CSV format:** Ensure no corruption, proper encoding (UTF-8)
- **Clear cache:** In app, press 'C' to clear cache and reload

### Heatmaps not displaying
- **Check image paths:** Verify PNG files exist in `/data`
- **Check file permissions:** Ensure read access
- **Fallback to matplotlib:** App will generate heatmaps if images missing

### Matrix verification fails
- **Check matrix properties:** Must be symmetric, unit diagonal, [0,1] range
- **Regenerate matrices:** Run pipeline again if corrupted
- **Check for NaN/Inf:** Clean data before loading

---

## 📚 Dependencies

Core libraries (see `requirements.txt`):
- `streamlit>=1.37` - Web framework
- `pandas>=2.2` - Data manipulation
- `numpy>=1.26` - Numerical computing
- `matplotlib>=3.8` - Static visualizations
- `plotly>=5.22` - Interactive visualizations
- `scipy>=1.11` - Clustering and distance metrics
- `networkx>=3.3` - Graph analysis (optional)
- `rdflib>=6.3` - RDF parsing

---

## 🎨 Presentation Tips (Slide 26)

### Live Demo Flow

1. **Start with overview** - Explain the 4-channel framework
2. **Dive into structural channel** - Show S1→S4 tabs
3. **Highlight S3 radar chart** - Visual system family comparison
4. **Show total similarity** - Heatmap + dendrogram
5. **Pick interesting pair** - E.g., Building03 vs Building04
6. **Compare channels** - Show breakdown
7. **Quick compare demo** - Upload a new RDF (if available)

### Key Talking Points

- **Why 4 channels?** - Captures different aspects of design similarity
- **Why 40% structural?** - Structural patterns most discriminative
- **What are motifs?** - Recurring structural patterns (frame nodes, cores)
- **System families?** - Classification: Frame, Wall, Dual, Braced
- **Validation?** - Matrix properties verified, results reproducible

### Visual Highlights

- **S3 Radar Chart** - Shows system family profiles at a glance
- **Total Similarity Heatmap** - Reveals clusters and outliers
- **Dendrogram** - Hierarchical relationships
- **Channel Breakdown** - Transparency in fusion

---

## 📞 Support

For questions or issues:
- **Thesis supervisor:** [Contact via TUM]
- **Repository:** Check for updates in project folder
- **Documentation:** See `thesis_submission_bundle_ALL_2/README_FOR_SUPERVISOR_ALL10.md`

---

## 📄 License & Citation

This demo is part of a TUM Master Thesis. If you use this framework or code:

**Please cite:**
```
[Your Name] (2025). Design Graph Similarity Analysis: A Multi-Channel Framework
for Architectural Design Comparison. Master Thesis, Technical University of Munich.
```

---

## ✅ Checklist for Presentation

- [ ] Test app locally before presentation
- [ ] Ensure all data files are present
- [ ] Check internet connection (if deploying to cloud)
- [ ] Prepare backup slides (in case of technical issues)
- [ ] Test "Quick Compare" with sample RDF
- [ ] Verify all heatmaps render correctly
- [ ] Practice navigation flow (5-7 minutes)
- [ ] Prepare answers for expected questions:
  - Why these weights?
  - How to handle new models?
  - Computational complexity?
  - Validation approach?

---

**Last Updated:** December 2025  
**Version:** 2.0 (ALL10 Dataset)  
**Status:** ✅ Ready for Thesis Presentation (Slide 26)

