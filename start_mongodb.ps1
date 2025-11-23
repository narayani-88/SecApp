# Script to start MongoDB using Docker

Write-Host "Checking Docker status..." -ForegroundColor Yellow

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first, then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or use MongoDB Atlas (cloud) - see setup_mongodb.md" -ForegroundColor Cyan
    exit 1
}

# Check if MongoDB container exists and is running
$container = docker ps -a --filter "name=secapp-mongodb" --format "{{.Names}}"
if ($container -eq "secapp-mongodb") {
    Write-Host "MongoDB container exists. Starting..." -ForegroundColor Yellow
    docker start secapp-mongodb
} else {
    Write-Host "Creating MongoDB container..." -ForegroundColor Yellow
    docker-compose up -d mongodb
}

# Wait a moment for MongoDB to start
Start-Sleep -Seconds 3

# Check if MongoDB is running
$running = docker ps --filter "name=secapp-mongodb" --format "{{.Names}}"
if ($running -eq "secapp-mongodb") {
    Write-Host ""
    Write-Host "✓ MongoDB is running on localhost:27017" -ForegroundColor Green
    Write-Host ""
    Write-Host "Create a .env file with:" -ForegroundColor Cyan
    Write-Host "MONGO_URI=mongodb://localhost:27017/" -ForegroundColor White
    Write-Host ""
    Write-Host "Then restart your Flask app!" -ForegroundColor Yellow
} else {
    Write-Host "✗ Failed to start MongoDB" -ForegroundColor Red
}

