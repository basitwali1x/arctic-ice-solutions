
$keystoreName = "yourchoiceice.jks"
$keystorePass = "ArcticIce2025!Secure"
$keyAlias = "yourchoiceice-key"
$keyPass = "ArcticIce2025!Secure"
$dname = "CN=Arctic Ice Solutions, OU=Mobile, O=Arctic Ice, L=Seattle, ST=WA, C=US"

$rootDir = Get-Location
$keystorePath = Join-Path $rootDir $keystoreName

# Check if keytool is available
if (-not (Get-Command "keytool" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: keytool command not found. Please ensure Java JDK is installed and in your PATH." -ForegroundColor Red
    exit 1
}

# Generate Keystore if it doesn't exist
if (-not (Test-Path $keystorePath)) {
    Write-Host "Generating new keystore at $keystorePath..."
    & keytool -genkeypair -v -keystore $keystorePath -alias $keyAlias -keyalg RSA -keysize 2048 -validity 10000 -storepass $keystorePass -keypass $keyPass -dname $dname
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to generate keystore." -ForegroundColor Red
        exit 1
    }
    Write-Host "Keystore generated successfully." -ForegroundColor Green
} else {
    Write-Host "Keystore already exists at $keystorePath." -ForegroundColor Yellow
}

# Function to create keystore.properties
function Create-PropertiesFile($targetDir) {
    if (-not (Test-Path $targetDir)) {
        Write-Host "Directory not found: $targetDir" -ForegroundColor Red
        return
    }
    
    $propsPath = Join-Path $targetDir "keystore.properties"
    # Essential: Escape backslashes in Windows paths for property files
    $escapedKeystorePath = $keystorePath -replace "\\", "\\" 
    
    $content = @"
storeFile=$escapedKeystorePath
storePassword=$keystorePass
keyAlias=$keyAlias
keyPassword=$keyPass
"@
    
    Set-Content -Path $propsPath -Value $content
    Write-Host "Created $propsPath" -ForegroundColor Green
}

# Create properties for Staff App
Create-PropertiesFile (Join-Path $rootDir "frontend-staff\android")

# Create properties for Customer App
Create-PropertiesFile (Join-Path $rootDir "frontend-customer\android")

Write-Host "`nSetup complete! You can now run the build commands." -ForegroundColor Cyan
