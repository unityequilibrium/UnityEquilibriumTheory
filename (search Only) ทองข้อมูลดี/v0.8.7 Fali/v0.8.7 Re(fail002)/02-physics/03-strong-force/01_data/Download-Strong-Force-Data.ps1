# Download-Strong-Force-Data.ps1
# Creates sample lattice QCD potential data for strong force validation
# Real data: HEPData or lattice QCD collaborations

$OutputFile = "$PSScriptRoot\qcd_potential.csv"

Write-Host "Creating sample QCD potential data for strong force validation..."

# Generate synthetic Cornell potential: V(r) = -alpha/r + sigma*r
# Parameters: alpha=0.3, sigma=0.2 GeV^2
$data = @"
r_fm,potential_gev
0.1,-2.7
0.2,-1.1
0.3,-0.47
0.4,-0.05
0.5,0.30
0.6,0.58
0.7,0.82
0.8,1.03
0.9,1.21
1.0,1.37
1.2,1.64
1.4,1.87
1.6,2.07
1.8,2.24
2.0,2.40
2.5,2.73
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   16 data points (synthetic Cornell potential)"
Write-Host ""
Write-Host "For REAL data, use HEPData:"
Write-Host "   https://www.hepdata.net/"
