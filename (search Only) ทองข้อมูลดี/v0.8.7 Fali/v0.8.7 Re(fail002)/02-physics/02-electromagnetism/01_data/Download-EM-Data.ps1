# Download-EM-Data.ps1
# Creates sample Coulomb force data for EM validation
# Real data: Laboratory measurements or NIST constants

$OutputFile = "$PSScriptRoot\coulomb_data.csv"

Write-Host "Creating sample Coulomb force data for EM validation..."

# Generate synthetic Coulomb force data (inverse-square law)
# F = k * q1 * q2 / r^2, with k=8.99e9 N·m²/C², q=1e-6 C
$data = @"
distance_m,force_n
0.01,89.9
0.02,22.475
0.03,9.989
0.04,5.619
0.05,3.596
0.06,2.497
0.07,1.835
0.08,1.405
0.09,1.110
0.10,0.899
0.12,0.624
0.14,0.458
0.16,0.351
0.18,0.277
0.20,0.225
0.25,0.144
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   16 data points (synthetic Coulomb force)"
Write-Host ""
Write-Host "For REAL data, use laboratory measurements or NIST:"
Write-Host "   https://physics.nist.gov/cuu/Constants/"
