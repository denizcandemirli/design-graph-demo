# app.py — Design Graph Similarity Web App (deploy-ready)

from __future__ import annotations
import os, glob, json
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
# PAGE & (optional) simple access gate
# =========================================
st.set_page_config(page_title="Design Graph Similarity Web App", layout="wide")

# If you set APP_TOKEN in Streamlit Cloud “Secrets”, uncomment below to require it.
# if "APP_TOKEN" in st.secrets:
#     token = st.text_input("Access token", type="password")
#     if token != st.secrets["APP_TOKEN"]:
#         st.stop()

# =========================================
# DATA PATHS (relative to repo)
# =========================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

TOTAL_DIR     = str(DATA_DIR / "06 - Total_Similarity")
TOTAL_VIS_DIR = str(DATA_DIR / "06b - Total_Similarity_Visuals")
STRUCT_DIR    = str(DATA_DIR / "07 - Structural_Extension_v25p2")
PAIRWISE_DIR  = str(DATA_DIR / "04 - Pairwise_Diffs" / "Typed_Edge")

# Optional local samples; not required in the cloud
SAMPLES_DIR   = str(BASE_DIR / "samples")
WORKSPACE_DIR = str(BASE_DIR)

# Authoritative fusion weights (A–D channels)
FUSION_W = {"content": 0.30, "typed": 0.20, "edge": 0.10, "struct": 0.40}

# =========================================
# SIDEBAR
# =========================================
st.sidebar.header("Inputs")
uploaded_rdf = st.sidebar.file_uploader("Current design graph (RDF)", type=["rdf", "ttl", "nt"])
top_n = st.sidebar.slider("Top-N results", 3, 10, 5)

# =========================================
# HELPERS
# =========================================
def pick_first_present(cands: List[str], cols: List[str]) -> Optional[str]:
    cmap = {c.strip().lower(): c for c in cols}
    for cand in cands:
        key = cand.strip().lower()
        if key in cmap:
            return cmap[key]
    return None

@st.cache_data
def short_rdf_info(file) -> tuple[Optional[int], Optional[int]]:
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
def load_total_similarity(total_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    pairwise = os.path.join(total_dir, "pairwise_total_summary.csv")
    matrix   = os.path.join(total_dir, "total_similarity_matrix.csv")
    df_pairs  = pd.read_csv(pairwise) if os.path.exists(pairwise) else pd.DataFrame()
    df_matrix = pd.read_csv(matrix, index_col=0) if os.path.exists(matrix) else pd.DataFrame()
    if not df_pairs.empty:
        df_pairs.columns = [c.strip() for c in df_pairs.columns]
    return df_pairs, df_matrix

@st.cache_data
def load_total_visuals(vis_dir: str) -> tuple[Optional[str], Optional[str]]:
    heatmap_png = os.path.join(vis_dir, "total_heatmap.png")
    dendro_png  = os.path.join(vis_dir, "total_dendrogram.png")
    return (heatmap_png if os.path.exists(heatmap_png) else None,
            dendro_png  if os.path.exists(dendro_png)  else None)

@st.cache_data
def load_structural(struct_dir: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scores = os.path.join(struct_dir, "struct_system_scores.csv")
    matrix = os.path.join(struct_dir, "struct_similarity_matrix.csv")
    df_scores = pd.read_csv(scores) if os.path.exists(scores) else pd.DataFrame()
    df_struct = pd.read_csv(matrix, index_col=0) if os.path.exists(matrix) else pd.DataFrame()
    pairwise_sum = os.path.join(struct_dir, "pairwise_structural_summary.csv")
    df_pair = pd.read_csv(pairwise_sum) if os.path.exists(pairwise_sum) else pd.DataFrame()
    if not df_pair.empty:
        df_pair.columns = [c.strip() for c in df_pair.columns]
    return df_scores, df_struct, df_pair

def build_topn_from_matrix(matrix_df: pd.DataFrame, model_name: str, n: int = 5) -> pd.DataFrame:
    if matrix_df.empty or model_name not in matrix_df.index:
        return pd.DataFrame()
    s = matrix_df.loc[model_name].drop(labels=[model_name]).sort_values(ascending=False).head(n)
    df = s.reset_index()
    df.columns = ["other", "S_total"]
    return df

def filter_topn_for_model(pairs_df: pd.DataFrame, model_name: str, n: int = 5) -> pd.DataFrame:
    if pairs_df.empty or not model_name:
        return pd.DataFrame()
    cols = [c.strip() for c in pairs_df.columns.tolist()]
    a_col = pick_first_present(["model_a","model_A","A","left","source","model1","name_a","file_a"], cols)
    b_col = pick_first_present(["model_b","model_B","B","right","target","model2","name_b","file_b"], cols)
    score_col = pick_first_present(
        ["total_similarity","final_similarity","S_total","S_final","score_total","score","similarity","S","total"], cols
    )
    if not a_col or not b_col or not score_col:
        return pd.DataFrame()
    df = pairs_df[(pairs_df[a_col] == model_name) | (pairs_df[b_col] == model_name)].copy()
    if df.empty:
        return pd.DataFrame()
    df["other"] = np.where(df[a_col] == model_name, df[b_col], df[a_col])

    keep = ["other", score_col]
    for cand in [
        "S_content","S_typed","S_edge","S_struct",
        "content_cos","typed_edge_cos","edge_sets_jaccard","motif_final",
        "content_cosine","typed_edge_cosine","edge_jaccard_combined","structural_similarity"
    ]:
        col = pick_first_present([cand], cols)
        if col:
            keep.append(col)

    df = df[[c for c in keep if c in df.columns]].copy()
    df = df.sort_values(score_col, ascending=False).head(n).reset_index(drop=True)
    return df

def plot_heatmap_from_matrix(matrix_df: pd.DataFrame, title: str) -> None:
    if matrix_df.empty:
        st.info("Matrix not found.")
        return
    fig, ax = plt.subplots()
    im = ax.imshow(matrix_df.values, aspect="auto")
    ax.set_xticks(range(len(matrix_df.columns)))
    ax.set_xticklabels(matrix_df.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matrix_df.index)))
    ax.set_yticklabels(matrix_df.index)
    ax.set_title(title)
    plt.colorbar(im, ax=ax)
    st.pyplot(fig)

def plot_dendrogram_from_matrix(matrix_df: pd.DataFrame, title: str) -> None:
    if matrix_df.empty:
        st.info("Matrix not found.")
        return
    D = 1.0 - matrix_df.values
    np.fill_diagonal(D, 0.0)
    condensed = squareform(D, checks=False)
    Z = linkage(condensed, method="average")
    fig, ax = plt.subplots()
    dendrogram(Z, labels=matrix_df.index.tolist(), ax=ax)
    ax.set_title(title)
    ax.set_ylabel("distance")
    st.pyplot(fig)

def plot_radar_scores(df_scores: pd.DataFrame, selected: Optional[str] = None) -> None:
    if df_scores.empty:
        st.info("No structural system scores.")
        return
    axes = ["frame", "wall", "braced", "dual"]
    def mk(row): return [row[a] for a in axes] + [row[axes[0]]]
    fig = go.Figure()
    if selected:
        row = df_scores[df_scores["model"] == selected].iloc[0]
        fig.add_trace(go.Scatterpolar(r=mk(row), theta=axes+[axes[0]], fill="toself", name=selected))
    else:
        for _, row in df_scores.iterrows():
            fig.add_trace(go.Scatterpolar(r=mk(row), theta=axes+[axes[0]], fill="toself", name=row["model"]))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])))
    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def list_pairwise_files(pairwise_dir: str) -> List[str]:
    files = []
    for root, _, fnames in os.walk(pairwise_dir):
        for f in fnames:
            if f.lower().endswith(".csv") and "typededge_predicate_contrib" in f.lower():
                files.append(os.path.join(root, f))
    return files

@st.cache_data
def load_pairwise_manifest(pairwise_dir: str) -> tuple[pd.DataFrame, Optional[str]]:
    candidates = ["typededge_pairwise_manifest.csv", "typededge_predicate_contrib_manifest.csv"]
    for cand in candidates:
        p = os.path.join(pairwise_dir, cand)
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                df.columns = [c.strip() for c in df.columns]
                return df, p
            except Exception:
                pass
    return pd.DataFrame(), None

def base_name_noext(name: str) -> str:
    return os.path.splitext(name)[0] if name else name

def file_contains_both(fname: str, a: str, b: str) -> bool:
    fl = fname.lower()
    return base_name_noext(a).lower() in fl and base_name_noext(b).lower() in fl

def load_pairwise_predicate_contrib(a: str, b: str) -> pd.DataFrame:
    dfm, _ = load_pairwise_manifest(PAIRWISE_DIR)
    if not dfm.empty:
        cols = dfm.columns.tolist()
        a_col = pick_first_present(["A","model_a","Model_A","left","source"], cols)
        b_col = pick_first_present(["B","model_b","Model_B","right","target"], cols)
        p_col = pick_first_present(["path","file","filepath"], cols)
        if a_col and b_col and p_col:
            row = dfm[
                ((dfm[a_col] == a) & (dfm[b_col] == b)) |
                ((dfm[a_col] == b) & (dfm[b_col] == a))
            ]
            if row.empty:
                row = dfm[dfm[p_col].astype(str).apply(lambda x: file_contains_both(x, a, b))]
            if not row.empty:
                p = row.iloc[0][p_col]
                if not os.path.isabs(p):
                    p = os.path.join(PAIRWISE_DIR, p)
                if os.path.exists(p):
                    try:
                        return pd.read_csv(p)
                    except Exception:
                        pass
    for f in list_pairwise_files(PAIRWISE_DIR):
        if file_contains_both(os.path.basename(f), a, b):
            try:
                return pd.read_csv(f)
            except Exception:
                continue
    return pd.DataFrame()

# --- quick content features for uploaded RDF
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

def build_ref_features_from_paths(paths: List[str]) -> pd.DataFrame:
    rows = []
    for p in paths:
        try:
            feats = rdf_to_feature_vector(p)
            feats["model"] = os.path.basename(p)
            rows.append(feats)
        except Exception:
            pass
    return pd.DataFrame(rows)

def compare_uploaded_to_refs(uploaded_file, ref_df: pd.DataFrame, topn: int = 5) -> pd.DataFrame:
    if uploaded_file is None or ref_df.empty:
        return pd.DataFrame()
    up_feats = rdf_to_feature_vector(uploaded_file)
    cols = [c for c in ref_df.columns if c.startswith("feat__")]
    u = np.array([up_feats.get(c, 0.0) for c in cols], dtype=float)
    sims = []
    for _, row in ref_df.iterrows():
        v = np.array([row[c] for c in cols], dtype=float)
        sims.append((row["model"], cosine(u, v)))
    out = pd.DataFrame(sims, columns=["other", "content_only_cosine"]).sort_values(
        "content_only_cosine", ascending=False
    ).head(topn)
    return out.reset_index(drop=True)

# ---- fusion recompute helpers
def _canon_pairs(df: pd.DataFrame, a_cands=None, b_cands=None):
    if df.empty:
        return df, None, None
    a_cands = a_cands or ["model_a","model_A","A","left","source","model1","name_a","file_a"]
    b_cands = b_cands or ["model_b","model_B","B","right","target","model2","name_b","file_b"]
    a = pick_first_present(a_cands, df.columns)
    b = pick_first_present(b_cands, df.columns)
    if not a or not b:
        return df, None, None
    out = df.copy()
    out["__A__"] = out[[a, b]].min(axis=1)
    out["__B__"] = out[[a, b]].max(axis=1)
    return out, "__A__", "__B__"

def recompute_total_from_components(pairs_df: pd.DataFrame, pair_struct_df: pd.DataFrame, w=FUSION_W) -> pd.DataFrame:
    if pairs_df.empty or pair_struct_df.empty:
        return pd.DataFrame()
    p, pa, pb = _canon_pairs(pairs_df)
    s, sa, sb = _canon_pairs(pair_struct_df)
    if not pa or not sa:
        return pd.DataFrame()
    content_col = pick_first_present(["content_cos","content_cosine"], p.columns)
    typed_col   = pick_first_present(["typed_edge_cos","typed_edge_cosine"], p.columns)
    edge_col    = pick_first_present(["edge_sets_jaccard","edge_jaccard_combined"], p.columns)
    struct_col  = pick_first_present(["structural_similarity","S_struct"], s.columns)
    if not all([content_col, typed_col, edge_col, struct_col]):
        return pd.DataFrame()
    m = pd.merge(
        p[[pa, pb, content_col, typed_col, edge_col]],
        s[[sa, sb, struct_col]],
        left_on=[pa, pb], right_on=[sa, sb], how="inner"
    )
    m["S_total_fused"] = (
        w["content"]*m[content_col] +
        w["typed"]  *m[typed_col]   +
        w["edge"]   *m[edge_col]    +
        w["struct"] *m[struct_col]
    )
    m = m.rename(columns={pa: "A", pb: "B",
                          content_col: "S_content", typed_col: "S_typed",
                          edge_col: "S_edge", struct_col: "S_struct"})
    return m

def verify_matrix(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"ok": False, "msg": "matrix missing"}
    A = df.values.astype(float)
    sym = np.allclose(A, A.T, atol=1e-8)
    diag = np.allclose(np.diag(A), 1.0, atol=1e-8)
    rng = (A.min() >= -1e-9) and (A.max() <= 1 + 1e-9)
    return {"ok": sym and diag and rng, "sym": sym, "diag1": diag, "rangeOK": rng}

def download_button(path: str, label: Optional[str] = None) -> None:
    if not path or not os.path.exists(path):
        return
    with open(path, "rb") as f:
        data = f.read()
    st.download_button(label or os.path.basename(path), data, file_name=os.path.basename(path))

# =========================================
# MAIN LAYOUT
# =========================================
st.title("Design Graph Similarity Web App")

# Uploaded RDF quick info
if uploaded_rdf is not None:
    triples, nodes = short_rdf_info(uploaded_rdf)
    st.info(f"Uploaded RDF: {uploaded_rdf.name}  |  triples: {triples}  |  unique subjects: {nodes}")

# Quick Compare (content-only)
with st.expander("Quick Compare (content-only)"):
    st.caption("Compare an uploaded RDF against a small reference set using a predicate histogram and cosine. This does not update the fused matrices.")
    ref_files = st.file_uploader("Reference RDFs (multi-upload)", type=["rdf","ttl","nt"], accept_multiple_files=True)
    ref_df = pd.DataFrame()
    if ref_files:
        rows = []
        for f in ref_files:
            try:
                feats = rdf_to_feature_vector(f)
                feats["model"] = f.name
                rows.append(feats)
            except Exception:
                pass
        if rows:
            ref_df = pd.DataFrame(rows)
    else:
        search_paths = []
        if SAMPLES_DIR and os.path.isdir(SAMPLES_DIR):
            search_paths.extend(glob.glob(os.path.join(SAMPLES_DIR, "*.rdf")))
        if not search_paths:
            search_paths.extend(glob.glob(os.path.join(WORKSPACE_DIR, "*.rdf")))
        if search_paths:
            ref_df = build_ref_features_from_paths(search_paths)
            if not ref_df.empty:
                st.write("Using reference set from:", [os.path.basename(p) for p in search_paths])

    if uploaded_rdf is None:
        st.info("Upload a current design graph on the left.")
    elif ref_df.empty:
        st.info("The reference set is empty. Upload a few RDFs above or place them in the project folder.")
    else:
        qc_topn = compare_uploaded_to_refs(uploaded_rdf, ref_df, top_n)
        if not qc_topn.empty:
            st.dataframe(qc_topn, use_container_width=True)
        else:
            st.info("Could not compute comparison (empty feature vectors).")

# Load data for the rest of the app
pair_total, mat_total = load_total_similarity(TOTAL_DIR)
heatmap_png, dendro_png = load_total_visuals(TOTAL_VIS_DIR)
struct_scores, struct_matrix, pair_struct = load_structural(STRUCT_DIR)

# Verification
with st.expander("Verification"):
    colA, colB = st.columns(2)
    with colA:
        st.write("Total matrix:", "OK" if not mat_total.empty else "missing")
        if not mat_total.empty:
            v = verify_matrix(mat_total)
            if v["ok"]:
                st.success(f"total_similarity_matrix: sym={v['sym']} diag1={v['diag1']} rangeOK={v['rangeOK']}")
            else:
                st.warning(f"total_similarity_matrix: sym={v['sym']} diag1={v['diag1']} rangeOK={v['rangeOK']}")
    with colB:
        st.write("Structural matrix:", "OK" if not struct_matrix.empty else "missing")
        if not struct_matrix.empty:
            v = verify_matrix(struct_matrix)
            if v["ok"]:
                st.success(f"struct_similarity_matrix: sym={v['sym']} diag1={v['diag1']} rangeOK={v['rangeOK']}")
            else:
                st.warning(f"struct_similarity_matrix: sym={v['sym']} diag1={v['diag1']} rangeOK={v['rangeOK']}")

# Results Overview (Total)
st.header("Results overview: Total similarity")

total_source = st.radio(
    "Source",
    ["Pairwise CSV (use the total column if present)", "Recompute fusion (0.30, 0.20, 0.10, 0.40)"],
    horizontal=True
)

target_model = st.selectbox(
    "Select a model",
    options=(mat_total.columns.tolist() if not mat_total.empty else [])
)

if target_model:
    if total_source.startswith("Pairwise"):
        topn_df = filter_topn_for_model(pair_total, target_model, top_n)
        if topn_df.empty and not mat_total.empty:
            topn_df = build_topn_from_matrix(mat_total, target_model, top_n)
            st.caption("Pairwise CSV columns did not match expected names; Top-N is derived from the matrix.")
        if not topn_df.empty:
            st.dataframe(topn_df, use_container_width=True)
        else:
            st.info("Could not build Top-N (CSV/matrix not available).")
    else:
        fused = recompute_total_from_components(pair_total, pair_struct, FUSION_W)
        if fused.empty:
            st.info("Recompute requires content/typed/edge pairwise CSV columns and a structural pairwise CSV.")
        else:
            sel = fused[(fused["A"] == target_model) | (fused["B"] == target_model)].copy()
            if sel.empty:
                st.info("No pair found for the selected model.")
            else:
                sel["other"] = np.where(sel["A"] == target_model, sel["B"], sel["A"])
                view = sel[["other","S_total_fused","S_content","S_typed","S_edge","S_struct"]] \
                        .sort_values("S_total_fused", ascending=False).head(top_n) \
                        .reset_index(drop=True)
                st.dataframe(view, use_container_width=True)
                st.caption(f"Fusion weights: content={FUSION_W['content']}  typed={FUSION_W['typed']}  edge={FUSION_W['edge']}  struct={FUSION_W['struct']}.")

# Visualizations (Total)
st.header("Visualizations: Total similarity")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Heatmap")
    if heatmap_png: st.image(heatmap_png, use_container_width=True)
    elif not mat_total.empty: plot_heatmap_from_matrix(mat_total, "Total similarity (0–1)")
    else: st.info("Heatmap image or matrix not found.")
with c2:
    st.subheader("Dendrogram")
    if dendro_png: st.image(dendro_png, use_container_width=True)
    elif not mat_total.empty: plot_dendrogram_from_matrix(mat_total, "Hierarchical clustering (distance = 1 − S_total)")
    else: st.info("Dendrogram image or matrix not found.")

# Structural Profiles (S3)
st.header("Structural profiles (S3)")
if not struct_scores.empty:
    mode = st.radio("Radar mode", ["Overlay (all models)", "Single model"], horizontal=True)
    if mode == "Single model":
        msel = st.selectbox("Model", options=struct_scores["model"].tolist())
        plot_radar_scores(struct_scores, selected=msel)
    else:
        plot_radar_scores(struct_scores, selected=None)
else:
    st.info("struct_system_scores.csv not found.")

# Structural similarity (matrix view)
with st.expander("Structural similarity (matrix view)"):
    if not struct_matrix.empty:
        plot_heatmap_from_matrix(struct_matrix, "Structural similarity (cosine)")
        plot_dendrogram_from_matrix(struct_matrix, "Structural dendrogram")
    else:
        st.info("struct_similarity_matrix.csv not found.")

# Pairwise Explain (predicate-level)
st.header("Pairwise explain (predicate-level)")
if not mat_total.empty:
    cpa, cpb = st.columns(2)
    with cpa:
        a = st.selectbox("Model A", options=mat_total.columns.tolist(), key="pa")
    with cpb:
        b = st.selectbox("Model B", options=[x for x in mat_total.columns if x != a], key="pb")
    if a and b:
        dfp = load_pairwise_predicate_contrib(a, b)
        cols = dfp.columns.tolist() if not dfp.empty else []
        pred_col  = pick_first_present(["predicate","relation","pred"], cols)
        share_col = pick_first_present(["product_contrib_share","share","contrib_share"], cols)
        diff_col  = pick_first_present(["abs_pct_diff_sum","diff_sum","abs_diff"], cols)
        if dfp.empty:
            st.info("Predicate-level contribution file not found for this pair.")
        else:
            c1, c2 = st.columns(2)
            if share_col and pred_col:
                top_share = dfp.sort_values(share_col, ascending=False).head(6).set_index(pred_col)[share_col]
                c1.subheader("Similarity drivers (contribution share)")
                c1.bar_chart(top_share)
            else:
                c1.info("No contribution share column found.")
            if diff_col and pred_col:
                top_diff = dfp.sort_values(diff_col, ascending=False).head(6).set_index(pred_col)[diff_col]
                c2.subheader("Differences (abs % diff sum)")
                c2.bar_chart(top_diff)
            else:
                c2.info("No difference column found.")
else:
    st.info("Load the total similarity matrix first to select models.")

# Downloads
st.header("Downloads")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Total**")
    download_button(os.path.join(TOTAL_DIR, "pairwise_total_summary.csv"), "pairwise_total_summary.csv")
    download_button(os.path.join(TOTAL_DIR, "total_similarity_matrix.csv"), "total_similarity_matrix.csv")
    download_button(os.path.join(TOTAL_VIS_DIR, "total_heatmap.png"), "total_heatmap.png")
    download_button(os.path.join(TOTAL_VIS_DIR, "total_dendrogram.png"), "total_dendrogram.png")
with col2:
    st.markdown("**Structural**")
    download_button(os.path.join(STRUCT_DIR, "struct_system_scores.csv"), "struct_system_scores.csv")
    download_button(os.path.join(STRUCT_DIR, "struct_similarity_matrix.csv"), "struct_similarity_matrix.csv")
    download_button(os.path.join(STRUCT_DIR, "pairwise_structural_summary.csv"), "pairwise_structural_summary.csv")
    download_button(os.path.join(STRUCT_DIR, "weights_used.json"), "weights_used.json")
with col3:
    st.markdown("**Typed-edge (predicate) – if present**")
    for f in sorted(glob.glob(os.path.join(PAIRWISE_DIR, "**", "*.csv"), recursive=True))[:6]:
        download_button(f, os.path.basename(f))

# Interpretation notes
with st.expander("Interpretation notes"):
    st.markdown("""
**Heatmap & dendrogram.**
Two tight pairs are visible: Building_05 with Building_06, and Option03_Revising with Option04_Rev03.
Freiform_Haus is the most distinct one among the five.

**What drives the ranking.**
The structural channel is high for all pairs, so separation mostly comes from the typed-edge channel, with content as a secondary contributor. Edge-set overlap is near zero except for near-duplicates.

**How to read the radar.**
System scores (frame, wall, braced, dual) are normalized to [0,1]; dual is capped by min(frame, wall) for a conservative interpretation.
""")

# Methods / About
with st.expander("About / methods"):
    st.markdown(f"""
**Fusion**  
`S_total = 0.30*S_content + 0.20*S_typed + 0.10*S_edge + 0.40*S_struct`.

**Files**  
Total: pairwise_total_summary.csv, total_similarity_matrix.csv, total_heatmap.png, total_dendrogram.png  
Structural: struct_system_scores.csv, struct_similarity_matrix.csv, pairwise_structural_summary.csv  
Predicate-level: CSV files under *04 - Pairwise_Diffs/Typed_Edge*  

**Verification**  
This app checks symmetry, unit diagonal, and [0,1] ranges for similarity matrices.
""")
