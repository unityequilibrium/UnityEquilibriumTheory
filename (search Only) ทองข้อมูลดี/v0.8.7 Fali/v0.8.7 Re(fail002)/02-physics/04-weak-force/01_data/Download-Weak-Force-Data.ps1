# Download-Weak-Force-Data.ps1
# Creates sample beta decay half-life data for weak force validation
# Real data: NNDC or IAEA Nuclear Data

$OutputFile = "$PSScriptRoot\beta_decay.csv"

Write-Host "Creating sample beta decay data for weak force validation..."

# Generate synthetic beta decay half-lives (seconds)
$data = @"
isotope,half_life_s,decay_type
H-3,3.89e8,beta_minus
C-14,1.80e11,beta_minus
Na-22,8.21e7,beta_plus
P-32,1.23e6,beta_minus
S-35,7.54e6,beta_minus
K-40,3.94e16,beta_minus
Ca-45,1.41e7,beta_minus
Fe-59,3.84e6,beta_minus
Co-60,1.66e8,beta_minus
Sr-90,9.09e8,beta_minus
I-131,6.95e5,beta_minus
Cs-137,9.50e8,beta_minus
Pb-210,7.01e8,beta_minus
Ra-228,1.81e8,beta_minus
Th-234,2.08e6,beta_minus
U-234,7.75e12,alpha
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   16 isotopes with half-lives"
Write-Host ""
Write-Host "For REAL data, use NNDC:"
Write-Host "   https://www.nndc.bnl.gov/nudat3/"
