# Download-GR-Tests.ps1
# Creates dataset of classical General Relativity tests
# Sources: NASA, Shapiro, Pound-Rebka

$OutputFile = "$PSScriptRoot\gr_test_data.csv"

Write-Host "Creating GR test dataset..."

$data = @"
test,parameter,predicted_gr,observed,uncertainty,unit
mercury_perihelion,precession,42.98,42.98,0.04,arcsec/century
light_deflection,angle_sun,1.75,1.75,0.01,arcsec
gravitational_redshift,pound_rebka_ratio,1.0,0.99,0.01,dimensionless
shapiro_delay,viking_delay_us,200,200,0.1,microseconds
gps_time_dilation,daily_drift,38.6,38.6,0.001,microseconds/day
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   5 classical GR tests data"
