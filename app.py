# app.py — Design Graph Similarity Web App (ALL10 Dataset)
# TUM Master Thesis - Updated for Slide 26 Presentation

from __future__ import annotations
import os, json
from pathlib import Path
from typing import Optional, List

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from rdflib import Graph
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform
import plotly.graph_objects as go

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Design Graph Similarity - ALL10 Dataset", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# DATA PATHS (Updated for ALL10)
# =========================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BUNDLE_DIR = BASE_DIR / "thesis_submission_bundle_ALL_2"
CHANNEL_DIR = BUNDLE_DIR / "CHANNEL_MATRICES"
STRUCT_PIPELINE_DIR = BUNDLE_DIR / "STRUCTURAL_PIPELINE"

# Authoritative fusion weights (aligned with thesis)
FUSION_W = {"content": 0.30, "typed": 0.20, "edge": 0.10, "struct": 0.40}

# DEBUG MODE for deployment troubleshooting (set to False after cloud works)
DEBUG_MODE = True

# =========================================
# SIDEBAR
# =========================================
st.sidebar.header("🔧 Controls")
uploaded_rdf = st.sidebar.file_uploader(
    "Upload Current Design Graph (RDF)", 
    type=["rdf", "ttl", "nt"],
    help="Upload your RDF file for quick comparison"
)
top_n = st.sidebar.slider("Top-N Results", 3, 10, 5)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dataset Info")
st.sidebar.info("**ALL10 Models**\n\n10 architectural design graphs analyzed across 4 channels + 4 structural sub-channels")

# =========================================
# HELPER FUNCTIONS
# =========================================
def pick_first_present(cands: List[str], cols: List[str]) -> Optional[str]:
    """Find first matching column name (case-insensitive)"""
    cmap = {c.strip().lower(): c for c in cols}
    for cand in cands:
        key = cand.strip().lower()
        if key in cmap:
            return cmap[key]
    return None

@st.cache_data
def short_rdf_info(file) -> tuple[Optional[int], Optional[int]]:
    """Extract basic RDF statistics"""
    try:
        g = Graph()
        try:
            g.parse(file=file, format="turtle")
        except Exception:
            if hasattr(file, "seek"):
                file.seek(0)
            g.parse(file=file, format="xml")
        return len(g), len(set(g.subjects()))
    except Exception:
        return None, None

@st.cache_data
def load_csv_safe(path: Path) -> pd.DataFrame:
    """Load CSV with error handling"""
    if path.exists():
        try:
            df = pd.read_csv(path)
            if not df.empty:
                df.columns = [c.strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading {path.name}: {e}")
    return pd.DataFrame()

@st.cache_data
def load_matrix_safe(path: Path) -> pd.DataFrame:
    """Load similarity matrix with index column"""
    if path.exists():
        try:
            df = pd.read_csv(path, index_col=0)
            return df
        except Exception as e:
            st.error(f"Error loading {path.name}: {e}")
    return pd.DataFrame()

@st.cache_data
def load_json_safe(path: Path) -> dict:
    """Load JSON with error handling"""
    if path.exists():
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading {path.name}: {e}")
    return {}

def plot_heatmap_from_matrix(matrix_df: pd.DataFrame, title: str, cmap='viridis') -> None:
    """Plot heatmap from similarity matrix"""
    if matrix_df.empty:
        st.info("Matrix not available.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix_df.values, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    
    ax.set_xticks(range(len(matrix_df.columns)))
    ax.set_xticklabels(matrix_df.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(matrix_df.index)))
    ax.set_yticklabels(matrix_df.index, fontsize=8)
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    plt.colorbar(im, ax=ax, label="Similarity [0-1]")
    plt.tight_layout()
    st.pyplot(fig)

def plot_dendrogram_from_matrix(matrix_df: pd.DataFrame, title: str) -> None:
    """Plot hierarchical clustering dendrogram"""
    if matrix_df.empty:
        st.info("Matrix not available.")
        return
    
    D = 1.0 - matrix_df.values
    np.fill_diagonal(D, 0.0)
    condensed = squareform(D, checks=False)
    Z = linkage(condensed, method="average")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    dendrogram(Z, labels=matrix_df.index.tolist(), ax=ax, leaf_font_size=9)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_ylabel("Distance (1 - Similarity)")
    ax.set_xlabel("Model")
    plt.tight_layout()
    st.pyplot(fig)

def plot_radar_scores(df_scores: pd.DataFrame, selected: Optional[str] = None, 
                     axes_cols=["Frame", "Wall", "Dual", "Braced"]) -> None:
    """Plot radar chart for system scores"""
    if df_scores.empty:
        st.info("No system scores available.")
        return
    
    # Check if required columns exist
    missing_cols = [col for col in axes_cols if col not in df_scores.columns]
    if missing_cols:
        st.warning(f"⚠️ Radar chart unavailable: Missing columns {missing_cols}")
        st.write("**Available columns:**", list(df_scores.columns))
        return
    
    def mk_trace(row): 
        vals = [row[a] for a in axes_cols]
        return vals + [vals[0]]
    
    fig = go.Figure()
    
    if selected:
        row = df_scores[df_scores["model"] == selected].iloc[0]
        fig.add_trace(go.Scatterpolar(
            r=mk_trace(row), 
            theta=axes_cols + [axes_cols[0]], 
            fill="toself", 
            name=selected
        ))
    else:
        for _, row in df_scores.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=mk_trace(row), 
                theta=axes_cols + [axes_cols[0]], 
                fill="toself", 
                name=row["model"]
            ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 0.5])),
        title="System Family Scores (S3)",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

def build_topn_from_matrix(matrix_df: pd.DataFrame, model_name: str, n: int = 5) -> pd.DataFrame:
    """Extract top-N similar models from matrix"""
    if matrix_df.empty or model_name not in matrix_df.index:
        return pd.DataFrame()
    
    s = matrix_df.loc[model_name].drop(labels=[model_name]).sort_values(ascending=False).head(n)
    df = s.reset_index()
    df.columns = ["Model", "Similarity"]
    return df

def verify_matrix(df: pd.DataFrame) -> dict:
    """Verify similarity matrix properties"""
    if df.empty:
        return {"ok": False, "msg": "matrix missing"}
    
    A = df.values.astype(float)
    sym = np.allclose(A, A.T, atol=1e-8)
    diag = np.allclose(np.diag(A), 1.0, atol=1e-8)
    rng = (A.min() >= -1e-9) and (A.max() <= 1 + 1e-9)
    
    return {"ok": sym and diag and rng, "sym": sym, "diag1": diag, "rangeOK": rng}

# --- Quick content features for uploaded RDF
PRED_KEYS = [
    "adjacentElement", "adjacentZone", "intersectingElement",
    "bfo_0000178", "hasFunction", "hasQuality"
]

def _parse_graph_any(file_or_path):
    g = Graph()
    try:
        g.parse(file=file_or_path, format="turtle")
    except Exception:
        try:
            if hasattr(file_or_path, "seek"):
                file_or_path.seek(0)
            g.parse(file=file_or_path, format="xml")
        except Exception:
            raise
    return g

def _pred_key_from_uri(uri: str) -> Optional[str]:
    low = uri.lower()
    for k in PRED_KEYS:
        if low.endswith(k.lower()):
            return k
    if low.endswith("#type") or low.endswith("/type"):
        return "rdf_type"
    return None

def rdf_to_feature_vector(file_or_path) -> dict:
    g = _parse_graph_any(file_or_path)
    feats = {k: 0.0 for k in PRED_KEYS + ["rdf_type"]}
    for _, p, _ in g.triples((None, None, None)):
        key = _pred_key_from_uri(str(p))
        if key:
            feats[key] += 1.0
    vec = np.array([feats[k] for k in sorted(feats.keys())], dtype=float)
    norm = np.linalg.norm(vec) or 1.0
    vec = vec / norm
    return dict(zip([f"feat__{k}" for k in sorted(feats.keys())], vec))

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def compare_uploaded_to_refs(uploaded_file, ref_models: List[str], topn: int = 5) -> pd.DataFrame:
    """Compare uploaded RDF to reference models using content similarity"""
    if uploaded_file is None or not ref_models:
        return pd.DataFrame()
    
    up_feats = rdf_to_feature_vector(uploaded_file)
    cols = sorted([c for c in up_feats.keys()])
    u = np.array([up_feats.get(c, 0.0) for c in cols], dtype=float)
    
    sims = []
    for model_path in ref_models:
        try:
            ref_feats = rdf_to_feature_vector(BASE_DIR / model_path)
            v = np.array([ref_feats.get(c, 0.0) for c in cols], dtype=float)
            sims.append((model_path, cosine(u, v)))
        except Exception:
            pass
    
    if not sims:
        return pd.DataFrame()
    
    out = pd.DataFrame(sims, columns=["Model", "Content_Cosine"]).sort_values(
        "Content_Cosine", ascending=False
    ).head(topn)
    return out.reset_index(drop=True)

# =========================================
# LOAD ALL DATA
# =========================================
@st.cache_data
def load_all_data():
    """Load all data files for ALL10 dataset"""
    data = {}
    
    # From /data folder (new results)
    data['adjacency_evidence'] = load_csv_safe(DATA_DIR / "adjacency_evidence.csv")
    data['functional_roles'] = load_csv_safe(DATA_DIR / "functional_roles_evidence.csv")
    data['motif_evidence'] = load_json_safe(DATA_DIR / "motif_evidence.json")
    
    data['S1_adjacency'] = load_matrix_safe(DATA_DIR / "S1_adjacency_similarity.csv")
    data['S2_motif'] = load_matrix_safe(DATA_DIR / "S2_motif_similarity.csv")
    data['S3_system'] = load_matrix_safe(DATA_DIR / "S3_system_similarity.csv")
    data['S4_functional'] = load_matrix_safe(DATA_DIR / "S4_functional_similarity.csv")
    data['S_struct_fused'] = load_matrix_safe(DATA_DIR / "S_struct_fused_similarity.csv")
    
    # From thesis bundle
    data['total_matrix'] = load_matrix_safe(CHANNEL_DIR / "total_similarity_matrix.csv")
    data['content_matrix'] = load_matrix_safe(CHANNEL_DIR / "content_similarity_matrix.csv")
    data['typed_edge_matrix'] = load_matrix_safe(CHANNEL_DIR / "typed_edge_similarity_matrix.csv")
    data['edge_sets_matrix'] = load_matrix_safe(CHANNEL_DIR / "edge_sets_similarity_matrix.csv")
    data['structural_matrix'] = load_matrix_safe(CHANNEL_DIR / "structural_similarity_matrix.csv")
    
    data['pairwise_total'] = load_csv_safe(CHANNEL_DIR / "pairwise_total_summary.csv")
    data['pairwise_content'] = load_csv_safe(CHANNEL_DIR / "pairwise_content_summary.csv")
    data['pairwise_typed'] = load_csv_safe(CHANNEL_DIR / "pairwise_typed_edge_summary.csv")
    data['pairwise_edge'] = load_csv_safe(CHANNEL_DIR / "pairwise_edge_sets_summary.csv")
    data['pairwise_struct'] = load_csv_safe(CHANNEL_DIR / "pairwise_structural_summary.csv")
    
    # Structural pipeline
    data['s1_inventory'] = load_csv_safe(STRUCT_PIPELINE_DIR / "s1_inventory.csv")
    data['s2_motifs'] = load_csv_safe(STRUCT_PIPELINE_DIR / "s2_motifs.csv")
    data['s3_system_scores'] = load_csv_safe(STRUCT_PIPELINE_DIR / "s3_system_scores.csv")
    data['s4_motif_share'] = load_csv_safe(STRUCT_PIPELINE_DIR / "s4_motif_share_vectors.csv")
    
    # Get model list
    if not data['total_matrix'].empty:
        data['models'] = data['total_matrix'].index.tolist()
    else:
        data['models'] = []
    
    return data

# Load all data
with st.spinner("Loading ALL10 dataset..."):
    DATA = load_all_data()

# =========================================
# MAIN LAYOUT
# =========================================
st.title("🏗️ Design Graph Similarity Analysis")
st.markdown("### ALL10 Dataset - TUM Master Thesis")

st.markdown("""
This interactive demo presents the **4-channel similarity framework** applied to 10 architectural design graphs.
The framework combines **content**, **typed-edge**, **edge-set**, and **structural** channels to compute 
comprehensive design similarity.
""")

# Display uploaded RDF info
if uploaded_rdf is not None:
    triples, nodes = short_rdf_info(uploaded_rdf)
    st.info(f"📄 **Uploaded:** {uploaded_rdf.name}  |  Triples: {triples}  |  Unique subjects: {nodes}")

# DEBUG section for deployment troubleshooting
if DEBUG_MODE:
    with st.expander("🔍 DEBUG: Deployment Check", expanded=False):
        st.write("**Working Dir:**", os.getcwd())
        st.write("**data/ exists?**", DATA_DIR.exists())
        st.write("**bundle exists?**", BUNDLE_DIR.exists())
        st.write("**CHANNEL_MATRICES/ exists?**", CHANNEL_DIR.exists())
        st.write("**STRUCTURAL_PIPELINE/ exists?**", STRUCT_PIPELINE_DIR.exists())
        
        if DATA_DIR.exists():
            files = list(DATA_DIR.iterdir())
            st.write(f"**Files in data/:** {len(files)}")
            st.write("**Sample files:**", [f.name for f in list(DATA_DIR.iterdir())[:5]])
        
        if CHANNEL_DIR.exists():
            files = list(CHANNEL_DIR.iterdir())
            st.write(f"**Files in CHANNEL_MATRICES/:** {len(files)}")
            st.write("**total_similarity_matrix.csv exists?**", (CHANNEL_DIR / "total_similarity_matrix.csv").exists())
        else:
            st.error("❌ CHANNEL_MATRICES folder NOT FOUND!")
        
        if STRUCT_PIPELINE_DIR.exists():
            files = list(STRUCT_PIPELINE_DIR.iterdir())
            st.write(f"**Files in STRUCTURAL_PIPELINE/:** {len(files)}")
        else:
            st.error("❌ STRUCTURAL_PIPELINE folder NOT FOUND!")
        
        st.markdown("---")
        st.markdown("### 📊 Data Loading Status")
        st.write(f"**Model list (DATA['models']):** {len(DATA['models'])} models")
        if DATA['models']:
            st.write("**Models:**", DATA['models'][:3], "..." if len(DATA['models']) > 3 else "")
        
        st.write(f"**total_matrix loaded?** {not DATA['total_matrix'].empty} (shape: {DATA['total_matrix'].shape if not DATA['total_matrix'].empty else 'empty'})")
        st.write(f"**S1_adjacency loaded?** {not DATA['S1_adjacency'].empty} (shape: {DATA['S1_adjacency'].shape if not DATA['S1_adjacency'].empty else 'empty'})")
        st.write(f"**S2_motif loaded?** {not DATA['S2_motif'].empty}")
        st.write(f"**S3_system loaded?** {not DATA['S3_system'].empty}")
        st.write(f"**S4_functional loaded?** {not DATA['S4_functional'].empty}")
        st.write(f"**s3_system_scores loaded?** {not DATA['s3_system_scores'].empty}")
        
        st.markdown("---")
        st.markdown("### 🔬 Direct Load Test (total_similarity_matrix.csv)")
        test_path = CHANNEL_DIR / "total_similarity_matrix.csv"
        st.write(f"**Path:** `{test_path}`")
        st.write(f"**Exists?** {test_path.exists()}")
        if test_path.exists():
            st.write(f"**File size:** {test_path.stat().st_size} bytes")
            try:
                test_df = pd.read_csv(test_path, index_col=0)
                st.success(f"✅ Manual load SUCCESSFUL! Shape: {test_df.shape}")
                st.write("**First 2 index values:**", list(test_df.index[:2]))
                st.write("**First 2 column values:**", list(test_df.columns[:2]))
            except Exception as e:
                st.error(f"❌ Manual load FAILED: {type(e).__name__}: {str(e)}")

st.markdown("---")

# =========================================
# SECTION 1: STRUCTURAL CHANNEL DEEP DIVE (S1→S4)
# =========================================
st.header("🔬 Structural Channel Deep Dive (S1 → S4)")
st.markdown("""
The **structural channel** (weight: 0.40) is decomposed into four sub-channels:
- **S1**: Adjacency-based similarity
- **S2**: Motif-based similarity  
- **S3**: System family similarity
- **S4**: Functional role similarity
""")

struct_tabs = st.tabs(["S1: Adjacency", "S2: Motifs", "S3: System Families", "S4: Functional Roles", "S_struct Fused"])

# TAB 1: S1 - Adjacency
with struct_tabs[0]:
    st.subheader("S1: Adjacency Evidence")
    st.markdown("Topological relationships between elements (adjacentElement, adjacentZone, etc.)")
    
    if not DATA['adjacency_evidence'].empty:
        st.dataframe(DATA['adjacency_evidence'], use_container_width=True)
    else:
        st.warning("Adjacency evidence not available")
    
    st.markdown("#### S1 Similarity Matrix")
    if not DATA['S1_adjacency'].empty:
        col1, col2 = st.columns(2)
        with col1:
            plot_heatmap_from_matrix(DATA['S1_adjacency'], "S1: Adjacency Similarity", cmap='YlOrRd')
        with col2:
            plot_dendrogram_from_matrix(DATA['S1_adjacency'], "S1: Adjacency Dendrogram")
    else:
        st.warning("S1 matrix not available")

# TAB 2: S2 - Motifs
with struct_tabs[1]:
    st.subheader("S2: Motif Detection")
    st.markdown("Structural motifs: M2 (frame node), M3 (wall-slab), M4 (core), M2b (brace node)")
    
    if not DATA['s2_motifs'].empty:
        st.dataframe(DATA['s2_motifs'], use_container_width=True)
    else:
        st.warning("Motif data not available")
    
    st.markdown("#### S2 Similarity Matrix")
    if not DATA['S2_motif'].empty:
        col1, col2 = st.columns(2)
        with col1:
            plot_heatmap_from_matrix(DATA['S2_motif'], "S2: Motif Similarity", cmap='YlGnBu')
        with col2:
            plot_dendrogram_from_matrix(DATA['S2_motif'], "S2: Motif Dendrogram")
    else:
        st.warning("S2 matrix not available")

# TAB 3: S3 - System Families
with struct_tabs[2]:
    st.subheader("S3: System Family Scores")
    st.markdown("Normalized scores for Frame, Wall, Dual, and Braced systems")
    
    if not DATA['s3_system_scores'].empty:
        st.dataframe(DATA['s3_system_scores'], use_container_width=True)
        
        st.markdown("#### Radar Chart Visualization")
        mode = st.radio("Display mode", ["Overlay (all models)", "Single model"], horizontal=True, key="s3_radar")
        
        if mode == "Single model":
            msel = st.selectbox("Select model", options=DATA['s3_system_scores']["model"].tolist())
            plot_radar_scores(DATA['s3_system_scores'], selected=msel)
        else:
            plot_radar_scores(DATA['s3_system_scores'], selected=None)
    else:
        st.warning("System scores not available")
    
    st.markdown("#### S3 Similarity Matrix")
    if not DATA['S3_system'].empty:
        col1, col2 = st.columns(2)
        with col1:
            plot_heatmap_from_matrix(DATA['S3_system'], "S3: System Similarity", cmap='Greens')
        with col2:
            # Also show pre-rendered heatmap if available
            s3_heatmap = DATA_DIR / "S3_system_similarity_heatmap.png"
            if s3_heatmap.exists():
                st.image(str(s3_heatmap), caption="S3 System Similarity (Pre-rendered)")
    else:
        st.warning("S3 matrix not available")

# TAB 4: S4 - Functional Roles
with struct_tabs[3]:
    st.subheader("S4: Functional Role Evidence")
    st.markdown("Structural roles: LoadBearing, Shear, Moment, Bracing")
    
    if not DATA['functional_roles'].empty:
        st.dataframe(DATA['functional_roles'], use_container_width=True)
    else:
        st.warning("Functional roles evidence not available")
    
    st.markdown("#### S4 Similarity Matrix")
    if not DATA['S4_functional'].empty:
        col1, col2 = st.columns(2)
        with col1:
            plot_heatmap_from_matrix(DATA['S4_functional'], "S4: Functional Similarity", cmap='Purples')
        with col2:
            # Also show pre-rendered heatmap if available
            s4_heatmap = DATA_DIR / "S4_functional_similarity_heatmap.png"
            if s4_heatmap.exists():
                st.image(str(s4_heatmap), caption="S4 Functional Similarity (Pre-rendered)")
    else:
        st.warning("S4 matrix not available")

# TAB 5: S_struct Fused
with struct_tabs[4]:
    st.subheader("S_struct: Fused Structural Similarity")
    st.markdown("Combined structural channel (S1 + S2 + S3 + S4)")
    
    if not DATA['S_struct_fused'].empty:
        col1, col2 = st.columns(2)
        with col1:
            plot_heatmap_from_matrix(DATA['S_struct_fused'], "S_struct: Fused Structural Similarity", cmap='RdYlGn')
        with col2:
            plot_dendrogram_from_matrix(DATA['S_struct_fused'], "S_struct: Fused Dendrogram")
    else:
        st.warning("Fused structural matrix not available")

st.markdown("---")

# =========================================
# SECTION 2: TOTAL SIMILARITY (FINAL FUSION)
# =========================================
st.header("🎯 Total Similarity (Final Fusion)")
st.markdown(f"""
**Fusion formula:**  
`S_total = {FUSION_W['content']}·S_content + {FUSION_W['typed']}·S_typed + {FUSION_W['edge']}·S_edge + {FUSION_W['struct']}·S_struct`

This combines all four channels into a single comprehensive similarity score.
""")

if DATA['models']:
    target_model = st.selectbox("Select a model to view its top-N similar models", options=DATA['models'])
    
    if target_model and not DATA['total_matrix'].empty:
        topn_df = build_topn_from_matrix(DATA['total_matrix'], target_model, top_n)
        
        if not topn_df.empty:
            st.markdown(f"#### Top {top_n} Similar Models to **{target_model}**")
            st.dataframe(topn_df, use_container_width=True)
            
            # Show detailed breakdown if pairwise data available
            if not DATA['pairwise_total'].empty:
                st.markdown("##### Channel Breakdown")
                # Try to find matching rows in pairwise data
                pair_df = DATA['pairwise_total']
                cols = pair_df.columns.tolist()
                a_col = pick_first_present(["model_a", "model_A", "A"], cols)
                b_col = pick_first_present(["model_b", "model_B", "B"], cols)
                
                if a_col and b_col:
                    matches = pair_df[
                        ((pair_df[a_col] == target_model) | (pair_df[b_col] == target_model))
                    ].copy()
                    
                    if not matches.empty:
                        matches["other"] = np.where(matches[a_col] == target_model, matches[b_col], matches[a_col])
                        # Filter to top-N models
                        top_models = topn_df["Model"].tolist()
                        matches = matches[matches["other"].isin(top_models)]
                        
                        display_cols = ["other"]
                        for col in ["S_total", "S_content", "S_typed", "S_edge", "S_struct"]:
                            col_match = pick_first_present([col, col.replace("S_", "")], cols)
                            if col_match:
                                display_cols.append(col_match)
                        
                        if len(display_cols) > 1:
                            st.dataframe(matches[display_cols].sort_values(display_cols[1], ascending=False), 
                                       use_container_width=True)
        else:
            st.info("No similar models found")
else:
    st.warning("No models available in dataset")

st.markdown("#### Total Similarity Visualization")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Heatmap**")
    # Try to show pre-rendered highlighted version
    total_heatmap = DATA_DIR / "total_similarity_heatmap_highlighted.png"
    if total_heatmap.exists():
        st.image(str(total_heatmap), use_container_width=True)
    elif not DATA['total_matrix'].empty:
        plot_heatmap_from_matrix(DATA['total_matrix'], "Total Similarity", cmap='RdYlGn')
    else:
        st.info("Total similarity heatmap not available")

with col2:
    st.markdown("**Dendrogram**")
    if not DATA['total_matrix'].empty:
        plot_dendrogram_from_matrix(DATA['total_matrix'], "Hierarchical Clustering (Total)")
    else:
        st.info("Total similarity matrix not available")

st.markdown("---")

# =========================================
# SECTION 3: MODEL-PAIR COMPARISON
# =========================================
st.header("🔍 Model-Pair Comparison")
st.markdown("Compare two models across all channels")

if DATA['models']:
    col_a, col_b = st.columns(2)
    with col_a:
        model_a = st.selectbox("Model A", options=DATA['models'], key="pair_a")
    with col_b:
        model_b = st.selectbox("Model B", options=[m for m in DATA['models'] if m != model_a], key="pair_b")
    
    if model_a and model_b:
        st.markdown(f"### Comparing: **{model_a}** ↔ **{model_b}**")
        
        # Extract similarities from matrices
        comparison = {}
        
        if not DATA['total_matrix'].empty and model_a in DATA['total_matrix'].index and model_b in DATA['total_matrix'].columns:
            comparison['Total'] = DATA['total_matrix'].loc[model_a, model_b]
        
        if not DATA['content_matrix'].empty and model_a in DATA['content_matrix'].index:
            comparison['Content'] = DATA['content_matrix'].loc[model_a, model_b]
        
        if not DATA['typed_edge_matrix'].empty and model_a in DATA['typed_edge_matrix'].index:
            comparison['Typed-Edge'] = DATA['typed_edge_matrix'].loc[model_a, model_b]
        
        if not DATA['edge_sets_matrix'].empty and model_a in DATA['edge_sets_matrix'].index:
            comparison['Edge-Sets'] = DATA['edge_sets_matrix'].loc[model_a, model_b]
        
        if not DATA['structural_matrix'].empty and model_a in DATA['structural_matrix'].index:
            comparison['Structural'] = DATA['structural_matrix'].loc[model_a, model_b]
        
        if not DATA['S1_adjacency'].empty and model_a in DATA['S1_adjacency'].index:
            comparison['S1_Adjacency'] = DATA['S1_adjacency'].loc[model_a, model_b]
        
        if not DATA['S2_motif'].empty and model_a in DATA['S2_motif'].index:
            comparison['S2_Motif'] = DATA['S2_motif'].loc[model_a, model_b]
        
        if not DATA['S3_system'].empty and model_a in DATA['S3_system'].index:
            comparison['S3_System'] = DATA['S3_system'].loc[model_a, model_b]
        
        if not DATA['S4_functional'].empty and model_a in DATA['S4_functional'].index:
            comparison['S4_Functional'] = DATA['S4_functional'].loc[model_a, model_b]
        
        if comparison:
            comp_df = pd.DataFrame(list(comparison.items()), columns=["Channel", "Similarity"])
            comp_df["Similarity"] = comp_df["Similarity"].round(4)
            
            col1, col2 = st.columns([2, 3])
            with col1:
                st.dataframe(comp_df, use_container_width=True)
            with col2:
                # Bar chart
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.barh(comp_df["Channel"], comp_df["Similarity"], color='steelblue')
                ax.set_xlabel("Similarity")
                ax.set_xlim(0, 1)
                ax.set_title(f"Channel Comparison: {model_a} vs {model_b}")
                plt.tight_layout()
                st.pyplot(fig)
        else:
            st.info("No comparison data available for this pair")
else:
    st.warning("No models available")

st.markdown("---")

# =========================================
# SECTION 4: QUICK COMPARE (CONTENT-ONLY)
# =========================================
with st.expander("🚀 Quick Compare (Content-Only)", expanded=False):
    st.markdown("""
    Upload a new RDF file to quickly compare it against the ALL10 reference set using 
    **content similarity only** (predicate histogram + cosine). This is a fast approximation 
    that does not require full graph analysis.
    """)
    
    if uploaded_rdf is None:
        st.info("Upload a design graph in the sidebar to use Quick Compare")
    elif not DATA['models']:
        st.warning("Reference model list not available")
    else:
        qc_result = compare_uploaded_to_refs(uploaded_rdf, DATA['models'], top_n)
        
        if not qc_result.empty:
            st.markdown(f"#### Top {top_n} Similar Models (Content-Only)")
            st.dataframe(qc_result, use_container_width=True)
            st.caption("⚠️ This is a content-only approximation. For full similarity, run the complete pipeline.")
        else:
            st.info("Could not compute comparison (empty feature vectors)")

st.markdown("---")

# =========================================
# SECTION 5: VERIFICATION & DIAGNOSTICS
# =========================================
with st.expander("✅ Verification & Diagnostics", expanded=False):
    st.markdown("### Matrix Verification")
    st.markdown("Checking symmetry, unit diagonal, and [0,1] range for all similarity matrices")
    
    matrices_to_verify = {
        "Total": DATA['total_matrix'],
        "Content": DATA['content_matrix'],
        "Typed-Edge": DATA['typed_edge_matrix'],
        "Edge-Sets": DATA['edge_sets_matrix'],
        "Structural": DATA['structural_matrix'],
        "S1_Adjacency": DATA['S1_adjacency'],
        "S2_Motif": DATA['S2_motif'],
        "S3_System": DATA['S3_system'],
        "S4_Functional": DATA['S4_functional'],
        "S_struct_Fused": DATA['S_struct_fused']
    }
    
    verification_results = []
    for name, matrix in matrices_to_verify.items():
        if not matrix.empty:
            v = verify_matrix(matrix)
            verification_results.append({
                "Matrix": name,
                "Symmetric": "✅" if v["sym"] else "❌",
                "Unit Diagonal": "✅" if v["diag1"] else "❌",
                "Range [0,1]": "✅" if v["rangeOK"] else "❌",
                "Overall": "✅" if v["ok"] else "❌"
            })
        else:
            verification_results.append({
                "Matrix": name,
                "Symmetric": "N/A",
                "Unit Diagonal": "N/A",
                "Range [0,1]": "N/A",
                "Overall": "Missing"
            })
    
    verify_df = pd.DataFrame(verification_results)
    st.dataframe(verify_df, use_container_width=True)

st.markdown("---")

# =========================================
# SECTION 6: DOWNLOADS
# =========================================
st.header("📥 Downloads")
st.markdown("Download all data files and visualizations")

download_cols = st.columns(3)

with download_cols[0]:
    st.markdown("**Similarity Matrices**")
    for name, path in [
        ("Total Similarity", CHANNEL_DIR / "total_similarity_matrix.csv"),
        ("Content Similarity", CHANNEL_DIR / "content_similarity_matrix.csv"),
        ("Typed-Edge Similarity", CHANNEL_DIR / "typed_edge_similarity_matrix.csv"),
        ("Edge-Sets Similarity", CHANNEL_DIR / "edge_sets_similarity_matrix.csv"),
        ("Structural Similarity", CHANNEL_DIR / "structural_similarity_matrix.csv"),
    ]:
        if path.exists():
            with open(path, "rb") as f:
                st.download_button(name, f, file_name=path.name, key=f"dl_{path.name}")

with download_cols[1]:
    st.markdown("**Structural Sub-Channels**")
    for name, path in [
        ("S1 Adjacency", DATA_DIR / "S1_adjacency_similarity.csv"),
        ("S2 Motif", DATA_DIR / "S2_motif_similarity.csv"),
        ("S3 System", DATA_DIR / "S3_system_similarity.csv"),
        ("S4 Functional", DATA_DIR / "S4_functional_similarity.csv"),
        ("S_struct Fused", DATA_DIR / "S_struct_fused_similarity.csv"),
    ]:
        if path.exists():
            with open(path, "rb") as f:
                st.download_button(name, f, file_name=path.name, key=f"dl_{path.name}")

with download_cols[2]:
    st.markdown("**Evidence Tables**")
    for name, path in [
        ("Adjacency Evidence", DATA_DIR / "adjacency_evidence.csv"),
        ("Functional Roles", DATA_DIR / "functional_roles_evidence.csv"),
        ("System Scores", STRUCT_PIPELINE_DIR / "s3_system_scores.csv"),
        ("Motif Data", STRUCT_PIPELINE_DIR / "s2_motifs.csv"),
    ]:
        if path.exists():
            with open(path, "rb") as f:
                st.download_button(name, f, file_name=path.name, key=f"dl_{path.name}")

st.markdown("---")

# =========================================
# SECTION 7: INTERPRETATION & METHODS
# =========================================
with st.expander("📖 Interpretation Notes", expanded=False):
    st.markdown("""
    ### Key Findings (ALL10 Dataset)
    
    **High Structural Similarity:**
    - Most models show very high structural similarity (S_struct > 0.80)
    - This indicates shared structural patterns despite geometric differences
    
    **Adjacency Channel (S1):**
    - Very high similarity across most models (> 0.95)
    - Models with more floors show higher adjacency counts
    
    **Motif Channel (S2):**
    - Consistent motif patterns across models
    - M2 (frame node), M3 (wall-slab), M4 (core) detected in most models
    
    **System Families (S3):**
    - Wall systems dominate in most models
    - Building03 (8-floor) shows highest wall system score
    - Frame, Dual, and Braced systems present but less dominant
    
    **Functional Roles (S4):**
    - Binary similarity: models either have functional roles or don't
    - Building04 (7-floor) lacks functional role annotations
    
    **Total Similarity Patterns:**
    - Tight clusters: BuildingArabic05/06, Building05/06
    - Building04 and Building03 (high-rise models) form distinct cluster
    - Building08 shows unique structural characteristics
    """)

with st.expander("🔬 Methods & Technical Details", expanded=False):
    st.markdown(f"""
    ### Similarity Framework
    
    **Four-Channel Architecture:**
    
    1. **Content Channel (weight: {FUSION_W['content']}):**
       - Predicate histogram + cosine similarity
       - Captures semantic content distribution
    
    2. **Typed-Edge Channel (weight: {FUSION_W['typed']}):**
       - Predicate-specific edge comparison
       - Normalized by predicate type
    
    3. **Edge-Sets Channel (weight: {FUSION_W['edge']}):**
       - Jaccard similarity of edge sets
       - Captures structural overlap
    
    4. **Structural Channel (weight: {FUSION_W['struct']}):**
       - **S1**: Adjacency-based (topological relationships)
       - **S2**: Motif-based (structural patterns)
       - **S3**: System families (Frame, Wall, Dual, Braced)
       - **S4**: Functional roles (LoadBearing, Shear, Moment, Bracing)
       - Fused using weighted combination
    
    **Fusion Formula:**
    ```
    S_total = 0.30·S_content + 0.20·S_typed + 0.10·S_edge + 0.40·S_struct
    ```
    
    **Matrix Properties:**
    - All similarity matrices are symmetric
    - Unit diagonal (self-similarity = 1.0)
    - Range: [0, 1]
    
    **Dataset:**
    - 10 architectural design graphs
    - RDF/OWL format with BFO/IFC ontologies
    - Varying complexity (2-8 floors)
    """)

# =========================================
# FOOTER
# =========================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p><strong>Design Graph Similarity Analysis - ALL10 Dataset</strong></p>
    <p>TUM Master Thesis | Chair of Computational Modeling and Simulation</p>
    <p>Framework: 4-channel similarity (Content + Typed-Edge + Edge-Sets + Structural)</p>
</div>
""", unsafe_allow_html=True)
