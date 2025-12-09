# Quick fix script for Streamlit Cloud deployment issues (Windows PowerShell)

Write-Host "🔍 Diagnosing deployment issues..." -ForegroundColor Cyan
Write-Host ""

# Check if files are tracked by Git
Write-Host "1️⃣ Checking if data files are tracked by Git..." -ForegroundColor Yellow
$dataFiles = git ls-files data/
if ($dataFiles.Count -eq 0) {
    Write-Host "❌ No files in /data are tracked by Git!" -ForegroundColor Red
} else {
    Write-Host "✅ Found $($dataFiles.Count) files in /data tracked by Git" -ForegroundColor Green
}
Write-Host ""

$bundleFiles = git ls-files thesis_submission_bundle_ALL_2/
if ($bundleFiles.Count -eq 0) {
    Write-Host "❌ No files in thesis_submission_bundle_ALL_2/ are tracked by Git!" -ForegroundColor Red
} else {
    Write-Host "✅ Found $($bundleFiles.Count) files in thesis bundle tracked by Git" -ForegroundColor Green
}
Write-Host ""

# Check .gitignore
Write-Host "2️⃣ Checking .gitignore..." -ForegroundColor Yellow
if (Test-Path .gitignore) {
    Write-Host "Found .gitignore, checking for problematic patterns..."
    $gitignore = Get-Content .gitignore
    if ($gitignore -match "\*\.csv") {
        Write-Host "⚠️  Found '*.csv' in .gitignore - CSVs might be ignored!" -ForegroundColor Yellow
    }
    if ($gitignore -match "\*\.png") {
        Write-Host "⚠️  Found '*.png' in .gitignore - images might be ignored!" -ForegroundColor Yellow
    }
    if ($gitignore -match "data/") {
        Write-Host "⚠️  Found 'data/' in .gitignore - data folder might be ignored!" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ No .gitignore found" -ForegroundColor Green
}
Write-Host ""

# Check for large files
Write-Host "3️⃣ Checking for large files (>50MB)..." -ForegroundColor Yellow
$largeFiles = Get-ChildItem -Recurse -File | Where-Object {$_.Length -gt 50MB}
if ($largeFiles) {
    foreach ($file in $largeFiles) {
        $sizeMB = [math]::Round($file.Length/1MB, 2)
        Write-Host "⚠️  Large file: $($file.FullName) ($sizeMB MB)" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ No large files (>50MB) found" -ForegroundColor Green
}
Write-Host ""

# Propose fix
Write-Host "🔧 Proposed fix:" -ForegroundColor Cyan
Write-Host "1. Force add all data files:"
Write-Host "   git add -f data/"
Write-Host "   git add -f thesis_submission_bundle_ALL_2/"
Write-Host "   git add -f *.rdf"
Write-Host ""
Write-Host "2. Commit and push:"
Write-Host "   git commit -m 'Add data files for deployment'"
Write-Host "   git push origin main"
Write-Host ""
Write-Host "3. Streamlit Cloud will auto-redeploy (takes 2-3 minutes)"
Write-Host ""

$response = Read-Host "Do you want to execute the fix now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "Adding files..." -ForegroundColor Cyan
    git add -f data/
    git add -f thesis_submission_bundle_ALL_2/
    git add -f *.rdf
    git add -f *.md
    git add -f requirements.txt
    git add -f app.py
    
    Write-Host "Committing..." -ForegroundColor Cyan
    git commit -m "Add all data files for Streamlit Cloud deployment"
    
    Write-Host "Pushing..." -ForegroundColor Cyan
    git push origin main
    
    Write-Host "✅ Done! Check Streamlit Cloud in 2-3 minutes." -ForegroundColor Green
    Write-Host "Your app will automatically redeploy." -ForegroundColor Green
} else {
    Write-Host "Skipped. You can run the commands manually." -ForegroundColor Yellow
}

