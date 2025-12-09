#!/bin/bash
# Quick fix script for Streamlit Cloud deployment issues

echo "🔍 Diagnosing deployment issues..."
echo ""

# Check if files are tracked by Git
echo "1️⃣ Checking if data files are tracked by Git..."
git ls-files data/ | wc -l
if [ $(git ls-files data/ | wc -l) -eq 0 ]; then
    echo "❌ No files in /data are tracked by Git!"
else
    echo "✅ Found $(git ls-files data/ | wc -l) files in /data tracked by Git"
fi
echo ""

git ls-files thesis_submission_bundle_ALL_2/ | wc -l
if [ $(git ls-files thesis_submission_bundle_ALL_2/ | wc -l) -eq 0 ]; then
    echo "❌ No files in thesis_submission_bundle_ALL_2/ are tracked by Git!"
else
    echo "✅ Found $(git ls-files thesis_submission_bundle_ALL_2/ | wc -l) files in thesis bundle tracked by Git"
fi
echo ""

# Check .gitignore
echo "2️⃣ Checking .gitignore..."
if [ -f .gitignore ]; then
    echo "Found .gitignore, checking for problematic patterns..."
    if grep -q "*.csv" .gitignore; then
        echo "⚠️  Found '*.csv' in .gitignore - CSVs might be ignored!"
    fi
    if grep -q "*.png" .gitignore; then
        echo "⚠️  Found '*.png' in .gitignore - images might be ignored!"
    fi
    if grep -q "data/" .gitignore; then
        echo "⚠️  Found 'data/' in .gitignore - data folder might be ignored!"
    fi
else
    echo "✅ No .gitignore found"
fi
echo ""

# Check for large files
echo "3️⃣ Checking for large files (>50MB)..."
find . -type f -size +50M 2>/dev/null | while read file; do
    size=$(du -h "$file" | cut -f1)
    echo "⚠️  Large file: $file ($size)"
done
echo ""

# Propose fix
echo "🔧 Proposed fix:"
echo "1. Force add all data files:"
echo "   git add -f data/"
echo "   git add -f thesis_submission_bundle_ALL_2/"
echo "   git add -f *.rdf"
echo ""
echo "2. Commit and push:"
echo "   git commit -m 'Add data files for deployment'"
echo "   git push origin main"
echo ""
echo "3. Restart Streamlit Cloud app (it will auto-redeploy on push)"
echo ""

read -p "Do you want to execute the fix now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Adding files..."
    git add -f data/
    git add -f thesis_submission_bundle_ALL_2/
    git add -f *.rdf
    git add -f *.md
    git add -f requirements.txt
    git add -f app.py
    
    echo "Committing..."
    git commit -m "Add all data files for Streamlit Cloud deployment"
    
    echo "Pushing..."
    git push origin main
    
    echo "✅ Done! Check Streamlit Cloud in a few minutes."
else
    echo "Skipped. You can run the commands manually."
fi

