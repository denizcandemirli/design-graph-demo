# Streamlit Cloud Deployment Fix Guide 🚀

## 🎯 Quick Fix (3 Steps)

Your app works locally but not on Streamlit Cloud because **files are missing from GitHub**.

### **Step 1: Run the Diagnostic Script**

Open PowerShell in your project folder and run:

```powershell
.\DEPLOYMENT_FIX_COMPLETE.ps1
```

This will:
- ✅ Check what files Git is tracking
- ✅ Identify missing files
- ✅ Offer to fix everything automatically

**Say "y" when prompted** to execute the fix.

---

### **Step 2: Verify on GitHub**

After pushing, **check your GitHub repo in a browser**:

1. Go to: `https://github.com/YOUR_USERNAME/design-graph-demo`
2. Click on the **`data/`** folder
3. **Verify you see** these files:
   - `adjacency_evidence.csv`
   - `S1_adjacency_similarity.csv`
   - `S2_motif_similarity.csv`
   - `S3_system_similarity.csv`
   - `S4_functional_similarity.csv`
   - `total_similarity_heatmap_highlighted.png`
   - etc.

4. Click on **`thesis_submission_bundle_ALL_2/`** folder
5. **Verify it has** `CHANNEL_MATRICES/` and `STRUCTURAL_PIPELINE/` subfolders

**If you DON'T see these files on GitHub → that's your problem!**

---

### **Step 3: Check Streamlit Cloud**

1. Go to: `https://design-graph-demo-dcd.streamlit.app/`
2. Wait 2-3 minutes for auto-redeployment
3. **Look for the DEBUG section** at the top (I just added it)
4. It should show:
   ```
   ✅ data/ exists? True
   ✅ thesis_submission_bundle_ALL_2/ exists? True
   
   Found X files in data/:
     - adjacency_evidence.csv
     - S1_adjacency_similarity.csv
     ...
   ```

5. **If you see the files listed** → Success! The S1-S4 tabs should now work.
6. **If you DON'T see the files** → Copy the DEBUG output and share it with me.

---

## 🔍 What Was Changed

### **In `app.py`:**

I added a **DEBUG section** right after the data paths (lines 40-90) that shows:
- Current working directory
- Which folders exist
- What files are in each folder
- RDF files in root

This helps us see **exactly what Streamlit Cloud has access to**.

### **Why This Helps:**

- **Local (Windows)**: Case-insensitive, sees all your files
- **Streamlit Cloud (Linux)**: Case-sensitive, only sees files in Git

The DEBUG section reveals the discrepancy immediately.

---

## 🐛 Common Issues & Solutions

### **Issue 1: "data/ folder NOT FOUND" in DEBUG**

**Cause:** Files not in Git  
**Fix:**
```powershell
git add -f data/
git commit -m "Add data files"
git push origin main
```

### **Issue 2: "Found 0 items in data/"**

**Cause:** Folder exists but is empty (files ignored)  
**Fix:**
```powershell
# Check .gitignore
type .gitignore

# Force add despite .gitignore
git add -f data/*
git commit -m "Force add data files"
git push origin main
```

### **Issue 3: Some files visible, others missing**

**Cause:** Case sensitivity (e.g., `S1_Adjacency.csv` vs `S1_adjacency.csv`)  
**Fix:**
1. Check DEBUG output for exact filenames on cloud
2. Rename files locally to match exactly
3. Update paths in `app.py` if needed
4. Commit and push

### **Issue 4: Large files rejected (>100MB)**

**Cause:** GitHub doesn't accept files >100MB  
**Fix:**
```powershell
# Use Git LFS
git lfs install
git lfs track "*.rdf"
git add .gitattributes
git commit -m "Track large files with LFS"
git push origin main
```

---

## 📋 Verification Checklist

Before opening Streamlit Cloud, verify these **locally**:

```powershell
# 1. Check Git status
git status
# Should say "nothing to commit, working tree clean"

# 2. Check what's tracked
git ls-files data/
# Should list ~15 CSV/PNG/JSON files

git ls-files thesis_submission_bundle_ALL_2/
# Should list many files in CHANNEL_MATRICES and STRUCTURAL_PIPELINE

git ls-files *.rdf
# Should list 10 RDF files

# 3. Check on GitHub (in browser)
# Navigate to your repo and verify folders are visible

# 4. Push if needed
git push origin main

# 5. Wait 2-3 minutes for Streamlit Cloud to redeploy
```

---

## 🎯 After It Works

Once the DEBUG section shows all files and S1-S4 tabs work:

### **Disable DEBUG mode:**

1. Open `app.py`
2. Find line ~40: `DEBUG_MODE = True`
3. Change to: `DEBUG_MODE = False`
4. Commit and push:
   ```powershell
   git add app.py
   git commit -m "Disable debug mode"
   git push origin main
   ```

The DEBUG section will disappear, giving you a clean app.

---

## 🆘 Still Not Working?

**Share these 4 things with me:**

1. **Screenshot of DEBUG section** from Streamlit Cloud
2. **Output of this command:**
   ```powershell
   git ls-files | findstr /I "csv png json rdf"
   ```
3. **Your GitHub repo URL**
4. **Output of:**
   ```powershell
   Get-ChildItem data/ -Name
   ```

I'll give you the exact fix immediately.

---

## 📊 Expected Outcome

**After the fix, your app should show:**

✅ **S1: Adjacency tab**
- Adjacency evidence table (10 models)
- S1 similarity heatmap
- Dendrogram

✅ **S2: Motifs tab**
- Motif counts table
- S2 similarity heatmap
- Dendrogram

✅ **S3: System Families tab**
- System scores table
- Interactive radar chart
- S3 heatmap

✅ **S4: Functional Roles tab**
- Functional roles table
- S4 similarity heatmap
- Dendrogram

✅ **S_struct Fused tab**
- Fused matrix heatmap
- Dendrogram

✅ **Total Similarity section**
- Model selector working
- Top-N table with channel breakdown
- Highlighted heatmap
- Dendrogram

✅ **Model-Pair Comparison**
- Two dropdowns working
- All channel scores displayed
- Bar chart

---

## 🚀 Quick Commands

```powershell
# Run diagnostic
.\DEPLOYMENT_FIX_COMPLETE.ps1

# Or manual fix
git add -f data/ thesis_submission_bundle_ALL_2/ *.rdf
git commit -m "Add all files for Streamlit Cloud"
git push origin main

# Check what's tracked
git ls-files

# Force push (if desperate)
git push origin main --force
```

---

## 📞 Next Steps

1. **Run:** `.\DEPLOYMENT_FIX_COMPLETE.ps1`
2. **Wait:** 2-3 minutes for redeployment
3. **Check:** DEBUG section on Streamlit Cloud
4. **Test:** Navigate through S1-S4 tabs
5. **Share:** Screenshot if still broken

**You got this! 🎉**

