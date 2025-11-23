# MongoDB Atlas Setup Helper Script
# This script helps you configure your .env file with MongoDB Atlas

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  MongoDB Atlas Configuration Helper" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env -ErrorAction SilentlyContinue
}

Write-Host "Current MONGO_URI setting:" -ForegroundColor Yellow
$currentUri = (Get-Content .env -ErrorAction SilentlyContinue | Select-String "MONGO_URI").ToString()
Write-Host $currentUri -ForegroundColor Gray
Write-Host ""

Write-Host "To update your .env file with MongoDB Atlas:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Get your MongoDB Atlas connection string:" -ForegroundColor White
Write-Host "   - Go to MongoDB Atlas dashboard" -ForegroundColor Gray
Write-Host "   - Click 'Connect' on your cluster" -ForegroundColor Gray
Write-Host "   - Choose 'Connect your application'" -ForegroundColor Gray
Write-Host "   - Copy the connection string" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Format: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Open .env file and replace the MONGO_URI line" -ForegroundColor White
Write-Host ""
Write-Host "4. Generate keys if needed:" -ForegroundColor White
Write-Host "   python generate_keys.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Test connection:" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor Cyan
Write-Host ""

$atlasUri = Read-Host "Enter your MongoDB Atlas connection string (or press Enter to skip)"
if ($atlasUri) {
    # Update .env file
    $envContent = Get-Content .env
    $newContent = $envContent | ForEach-Object {
        if ($_ -match "^MONGO_URI=") {
            "MONGO_URI=$atlasUri"
        } else {
            $_
        }
    }
    $newContent | Set-Content .env -Encoding UTF8
    Write-Host ""
    Write-Host "✓ Updated MONGO_URI in .env file!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Don't forget to:" -ForegroundColor Yellow
    Write-Host "  - Add FLASK_SECRET_KEY and FERNET_KEY (run: python generate_keys.py)" -ForegroundColor White
    Write-Host "  - Whitelist your IP in MongoDB Atlas Network Access" -ForegroundColor White
    Write-Host ""
}

