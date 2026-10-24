Set-Location -Path $PSScriptRoot
Write-Host "Installing dependencies..."
pip install -r requirements.txt
Write-Host "Starting MSIP Label Scanner..."
Write-Host "Open http://127.0.0.1:5000 in your browser"
python app.py
Read-Host -Prompt "Press Enter to exit"
