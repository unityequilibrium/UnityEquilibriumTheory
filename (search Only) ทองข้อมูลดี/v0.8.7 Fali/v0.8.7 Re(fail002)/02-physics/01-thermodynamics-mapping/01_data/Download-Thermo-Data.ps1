# Download-Thermo-Data.ps1
# Creates sample climate data for thermodynamics mapping validation
# Real data: NOAA Global Summary of Day (GSOD)

$OutputFile = "$PSScriptRoot\climate_data.csv"

Write-Host "Creating sample climate data for thermodynamics validation..."

# Generate synthetic temperature/pressure data (realistic Bangkok climate)
$data = @"
date,temperature_c,pressure_hpa
2024-01-01,28.5,1012.3
2024-01-15,29.2,1011.8
2024-02-01,30.1,1010.5
2024-02-15,31.5,1009.2
2024-03-01,33.2,1008.1
2024-03-15,34.8,1006.5
2024-04-01,35.5,1005.2
2024-04-15,34.2,1006.8
2024-05-01,32.8,1008.5
2024-05-15,31.5,1010.2
2024-06-01,30.2,1011.5
2024-06-15,29.5,1012.1
2024-07-01,29.0,1012.8
2024-07-15,28.8,1013.2
2024-08-01,28.5,1013.5
2024-08-15,28.2,1013.8
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   16 data points (synthetic Bangkok climate)"
Write-Host ""
Write-Host "For REAL data, use NOAA GSOD:"
Write-Host "   https://www.ncei.noaa.gov/access/search/data-search/global-summary-of-the-day"
