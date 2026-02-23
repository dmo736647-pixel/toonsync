# Start Backend Server
Write-Host "Starting Backend Server..."
$backendCmd = "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process cmd -ArgumentList "/k", "$backendCmd" -WindowStyle Normal

# Start Frontend Server
Write-Host "Starting Frontend Server..."
Set-Location frontend
$frontendCmd = "npm run dev"
Start-Process cmd -ArgumentList "/k", "$frontendCmd" -WindowStyle Normal
Set-Location ..

Write-Host "========================================"
Write-Host "Services Started Successfully!"
Write-Host "========================================"
Write-Host "Backend API: http://localhost:8000/docs"
Write-Host "Frontend UI: http://localhost:5173"
Write-Host "Please check the two new terminal windows."
Write-Host "========================================"
