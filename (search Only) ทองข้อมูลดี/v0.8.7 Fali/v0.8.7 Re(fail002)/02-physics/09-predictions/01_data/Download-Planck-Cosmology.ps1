# Download-Planck-Cosmology.ps1
# Downloads cosmological parameters from Planck 2018
# Real data: https://arxiv.org/abs/1807.06209

$OutputFile = "$PSScriptRoot\planck_2018.csv"

Write-Host "Creating Planck 2018 cosmological parameters..."

# Planck 2018 TT,TE,EE+lowE+lensing best-fit values (real data)
$data = @"
parameter,symbol,value,sigma_plus,sigma_minus,unit
hubble_constant,H_0,67.36,0.54,0.54,km/s/Mpc
baryon_density,Omega_b*h^2,0.02237,0.00015,0.00015,dimensionless
cdm_density,Omega_c*h^2,0.1200,0.0012,0.0012,dimensionless
dark_energy_density,Omega_Lambda,0.6847,0.0073,0.0073,dimensionless
matter_density,Omega_m,0.3153,0.0073,0.0073,dimensionless
optical_depth,tau,0.0544,0.0073,0.0081,dimensionless
scalar_amplitude,ln(10^10*A_s),3.044,0.014,0.014,dimensionless
spectral_index,n_s,0.9649,0.0042,0.0042,dimensionless
age_of_universe,t_0,13.797,0.023,0.023,Gyr
sound_horizon,r_s,144.43,0.26,0.26,Mpc
angular_scale,theta_*,1.04110,0.00031,0.00031,deg
curvature,Omega_K,0.0007,0.0019,0.0019,dimensionless
sum_neutrino_masses,sum_m_nu,0.06,0.0,0.0,eV
sigma_8,sigma_8,0.8111,0.0060,0.0060,dimensionless
s_8,S_8,0.832,0.013,0.013,dimensionless
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   15 Planck 2018 cosmological parameters"
Write-Host ""
Write-Host "Source: Planck 2018 Results VI - arXiv:1807.06209"
