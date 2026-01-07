# Download-Gravity-Data.ps1
# Downloads Earth-Moon orbital data from NASA JPL Horizons (mock/sample for demo)
# Real API requires registration at https://ssd.jpl.nasa.gov/horizons/

$OutputFile = "$PSScriptRoot\orbital_data.csv"

Write-Host "Creating sample orbital data for gravity validation..."

# Generate synthetic Earth-Moon-like orbital data (realistic scale)
$data = @"
time_jd,x_km,y_km,z_km
2459215.5,384400,0,0
2459216.5,383000,28000,500
2459217.5,378000,55000,1000
2459218.5,370000,80000,1500
2459219.5,358000,102000,2000
2459220.5,343000,122000,2500
2459221.5,325000,138000,3000
2459222.5,305000,152000,3500
2459223.5,283000,162000,4000
2459224.5,259000,170000,4500
2459225.5,234000,174000,5000
2459226.5,208000,176000,5500
2459227.5,181000,174000,6000
2459228.5,154000,170000,6500
2459229.5,128000,162000,7000
2459230.5,102000,152000,7500
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   16 data points (synthetic Earth-Moon orbit)"
Write-Host ""
Write-Host "For REAL data, use NASA Horizons API:"
Write-Host "   https://ssd.jpl.nasa.gov/horizons/app.html"
