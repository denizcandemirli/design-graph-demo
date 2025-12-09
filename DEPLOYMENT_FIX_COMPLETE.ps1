# Complete Deployment Fix for Streamlit Cloud
# Run this in PowerShell from your project root

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host "  STREAMLIT CLOUD DEPLOYMENT FIX - Complete Diagnostic & Repair" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# ============================================
# STEP 1: Check Current Git Status
# ============================================
Write-Host "[STEP 1] Checking Git repository status..." -ForegroundColor Yellow
Write-Host ""

$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  You have uncommitted changes:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
} else {
    Write-Host "✅ Repository is clean" -ForegroundColor Green
    Write-Host ""
}

# ============================================
# STEP 2: Check What Files Git Is Tracking
# ============================================
Write-Host "[STEP 2] Checking what files Git is tracking..." -ForegroundColor Yellow
Write-Host ""

Write-Host "2.1 Checking data/ folder..." -ForegroundColor Cyan
$dataTracked = git ls-files data/
if ($dataTracked) {
    Write-Host "✅ Git is tracking $($dataTracked.Count) files in data/" -ForegroundColor Green
    Write-Host "Files:" -ForegroundColor Gray
    $dataTracked | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
} else {
    Write-Host "❌ NO FILES in data/ are tracked by Git!" -ForegroundColor Red
    Write-Host "   This is likely your problem." -ForegroundColor Red
}
Write-Host ""

Write-Host "2.2 Checking thesis_submission_bundle_ALL_2/ folder..." -ForegroundColor Cyan
$bundleTracked = git ls-files thesis_submission_bundle_ALL_2/
if ($bundleTracked) {
    Write-Host "✅ Git is tracking $($bundleTracked.Count) files in thesis_submission_bundle_ALL_2/" -ForegroundColor Green
} else {
    Write-Host "❌ NO FILES in thesis_submission_bundle_ALL_2/ are tracked by Git!" -ForegroundColor Red
}
Write-Host ""

Write-Host "2.3 Checking RDF files..." -ForegroundColor Cyan
$rdfTracked = git ls-files *.rdf
if ($rdfTracked) {
    Write-Host "✅ Git is tracking $($rdfTracked.Count) RDF files" -ForegroundColor Green
    $rdfTracked | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
} else {
    Write-Host "❌ NO RDF files are tracked by Git!" -ForegroundColor Red
}
Write-Host ""

# ============================================
# STEP 3: Check .gitignore
# ============================================
Write-Host "[STEP 3] Checking .gitignore for problematic patterns..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path .gitignore) {
    $gitignore = Get-Content .gitignore -Raw
    $problems = @()
    
    if ($gitignore -match "\*\.csv") { $problems += "*.csv" }
    if ($gitignore -match "\*\.png") { $problems += "*.png" }
    if ($gitignore -match "\*\.json") { $problems += "*.json" }
    if ($gitignore -match "\*\.rdf") { $problems += "*.rdf" }
    if ($gitignore -match "data/") { $problems += "data/" }
    if ($gitignore -match "thesis_submission_bundle") { $problems += "thesis_submission_bundle*" }
    
    if ($problems.Count -gt 0) {
        Write-Host "⚠️  Found problematic patterns in .gitignore:" -ForegroundColor Yellow
        $problems | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
        Write-Host ""
        Write-Host "These patterns may be blocking your files from Git." -ForegroundColor Yellow
        Write-Host "We'll use 'git add -f' to force-add them." -ForegroundColor Yellow
    } else {
        Write-Host "✅ No problematic patterns in .gitignore" -ForegroundColor Green
    }
} else {
    Write-Host "ℹ️  No .gitignore file found" -ForegroundColor Cyan
}
Write-Host ""

# ============================================
# STEP 4: Check File Sizes
# ============================================
Write-Host "[STEP 4] Checking for large files (>100MB - GitHub limit)..." -ForegroundColor Yellow
Write-Host ""

$largeFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.Length -gt 100MB -and $_.FullName -notmatch '\.git' }

if ($largeFiles) {
    Write-Host "⚠️  WARNING: Found files larger than 100MB:" -ForegroundColor Yellow
    $largeFiles | ForEach-Object {
        $sizeMB = [math]::Round($_.Length / 1MB, 2)
        Write-Host "  - $($_.Name) ($sizeMB MB)" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "GitHub rejects files >100MB. You'll need to:" -ForegroundColor Yellow
    Write-Host "  1. Use Git LFS (git lfs track '*.rdf')" -ForegroundColor Yellow
    Write-Host "  2. Or compress/split large files" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✅ No files larger than 100MB" -ForegroundColor Green
}
Write-Host ""

# ============================================
# STEP 5: Verify Physical Files Exist
# ============================================
Write-Host "[STEP 5] Verifying physical files exist on disk..." -ForegroundColor Yellow
Write-Host ""

$criticalFiles = @(
    "data/adjacency_evidence.csv",
    "data/functional_roles_evidence.csv",
    "data/motif_evidence.json",
    "data/S1_adjacency_similarity.csv",
    "data/S2_motif_similarity.csv",
    "data/S3_system_similarity.csv",
    "data/S4_functional_similarity.csv",
    "data/S_struct_fused_similarity.csv",
    "data/total_similarity_heatmap.png",
    "data/total_similarity_heatmap_highlighted.png",
    "thesis_submission_bundle_ALL_2/CHANNEL_MATRICES/total_similarity_matrix.csv",
    "thesis_submission_bundle_ALL_2/STRUCTURAL_PIPELINE/s3_system_scores.csv"
)

$missingFiles = @()
$existingFiles = @()

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        $existingFiles += $file
    } else {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "❌ CRITICAL: Missing files on disk:" -ForegroundColor Red
    $missingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "You need to generate these files first!" -ForegroundColor Red
    Write-Host ""
} else {
    Write-Host "✅ All critical files exist on disk" -ForegroundColor Green
    Write-Host ""
}

# ============================================
# DIAGNOSIS SUMMARY
# ============================================
Write-Host "=" -NoNewline -ForegroundColor Magenta
Write-Host "=" * 79 -ForegroundColor Magenta
Write-Host "  DIAGNOSIS SUMMARY" -ForegroundColor Magenta
Write-Host "=" -NoNewline -ForegroundColor Magenta
Write-Host "=" * 79 -ForegroundColor Magenta
Write-Host ""

$issues = @()
$fixes = @()

if (-not $dataTracked) {
    $issues += "data/ folder files not tracked by Git"
    $fixes += "git add -f data/"
}

if (-not $bundleTracked) {
    $issues += "thesis_submission_bundle_ALL_2/ files not tracked by Git"
    $fixes += "git add -f thesis_submission_bundle_ALL_2/"
}

if (-not $rdfTracked) {
    $issues += "RDF files not tracked by Git"
    $fixes += "git add -f *.rdf"
}

if ($missingFiles.Count -gt 0) {
    $issues += "$($missingFiles.Count) critical files missing from disk"
    $fixes += "Regenerate missing data files"
}

if ($issues.Count -eq 0) {
    Write-Host "✅ NO ISSUES DETECTED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your files are tracked by Git. The issue might be:" -ForegroundColor Yellow
    Write-Host "  1. Case sensitivity (Windows vs Linux)" -ForegroundColor Yellow
    Write-Host "  2. Files not pushed to GitHub yet" -ForegroundColor Yellow
    Write-Host "  3. Streamlit Cloud cache issue" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "❌ ISSUES FOUND:" -ForegroundColor Red
    $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host ""
}

# ============================================
# STEP 6: Propose Fix
# ============================================
Write-Host "[STEP 6] Proposed Fix Commands" -ForegroundColor Yellow
Write-Host ""

Write-Host "Run these commands to fix the issues:" -ForegroundColor Cyan
Write-Host ""
Write-Host "# Force add all necessary files" -ForegroundColor Gray
Write-Host "git add -f data/" -ForegroundColor White
Write-Host "git add -f thesis_submission_bundle_ALL_2/" -ForegroundColor White
Write-Host "git add -f *.rdf" -ForegroundColor White
Write-Host "git add -f *.md" -ForegroundColor White
Write-Host "git add -f app.py" -ForegroundColor White
Write-Host "git add -f requirements.txt" -ForegroundColor White
Write-Host ""
Write-Host "# Commit" -ForegroundColor Gray
Write-Host 'git commit -m "Add all data files for Streamlit Cloud deployment"' -ForegroundColor White
Write-Host ""
Write-Host "# Push to GitHub" -ForegroundColor Gray
Write-Host "git push origin main" -ForegroundColor White
Write-Host ""

# ============================================
# STEP 7: Execute Fix (Optional)
# ============================================
Write-Host ""
$response = Read-Host "Do you want to execute the fix now? (y/n)"

if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host "=" * 79 -ForegroundColor Green
    Write-Host "  EXECUTING FIX" -ForegroundColor Green
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host "=" * 79 -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Adding files..." -ForegroundColor Cyan
    git add -f data/
    git add -f thesis_submission_bundle_ALL_2/
    git add -f *.rdf
    git add -f *.md
    git add -f app.py
    git add -f requirements.txt
    git add -f *.ps1
    git add -f *.sh
    
    Write-Host ""
    Write-Host "Files staged. Current status:" -ForegroundColor Cyan
    git status --short
    
    Write-Host ""
    $commitResponse = Read-Host "Commit these changes? (y/n)"
    
    if ($commitResponse -eq "y" -or $commitResponse -eq "Y") {
        Write-Host ""
        Write-Host "Committing..." -ForegroundColor Cyan
        git commit -m "Add all data files for Streamlit Cloud deployment (forced)"
        
        Write-Host ""
        Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
        git push origin main
        
        Write-Host ""
        Write-Host "=" -NoNewline -ForegroundColor Green
        Write-Host "=" * 79 -ForegroundColor Green
        Write-Host "  ✅ DONE!" -ForegroundColor Green
        Write-Host "=" -NoNewline -ForegroundColor Green
        Write-Host "=" * 79 -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "  1. Wait 2-3 minutes for Streamlit Cloud to redeploy" -ForegroundColor Yellow
        Write-Host "  2. Open your app: https://design-graph-demo-dcd.streamlit.app/" -ForegroundColor Yellow
        Write-Host "  3. Check the DEBUG section at the top" -ForegroundColor Yellow
        Write-Host "  4. Verify all folders and files are listed" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "If it still doesn't work, share the DEBUG output with ChatGPT." -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "Commit cancelled." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Fix not executed. Run the commands manually when ready." -ForegroundColor Yellow
    Write-Host ""
}

# ============================================
# FINAL INSTRUCTIONS
# ============================================
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host "  FINAL CHECKLIST" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host ""
Write-Host "After pushing:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. ✅ Check GitHub repo in browser" -ForegroundColor White
Write-Host "     - Navigate to your repo" -ForegroundColor Gray
Write-Host "     - Click into data/ folder" -ForegroundColor Gray
Write-Host "     - Verify you can see CSV files" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. ✅ Open Streamlit Cloud app" -ForegroundColor White
Write-Host "     https://design-graph-demo-dcd.streamlit.app/" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. ✅ Check DEBUG section" -ForegroundColor White
Write-Host "     - Should show all folders exist" -ForegroundColor Gray
Write-Host "     - Should list all CSV files" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. ✅ Test S1-S4 tabs" -ForegroundColor White
Write-Host "     - Should now show evidence tables" -ForegroundColor Gray
Write-Host "     - Should show heatmaps" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. ✅ After it works, disable DEBUG" -ForegroundColor White
Write-Host "     - In app.py, set DEBUG_MODE = False" -ForegroundColor Gray
Write-Host "     - Commit and push again" -ForegroundColor Gray
Write-Host ""

Write-Host "Good luck! 🚀" -ForegroundColor Green
Write-Host ""

