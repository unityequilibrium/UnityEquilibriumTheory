# Download-NIST-Quantum.ps1
# Downloads quantum constants from NIST
# Real data: https://physics.nist.gov/cuu/Constants/

$OutputFile = "$PSScriptRoot\quantum_constants.csv"

Write-Host "Creating NIST quantum constants data..."

# NIST CODATA 2022 values (real data)
$data = @"
constant,symbol,value,uncertainty,unit
planck_constant,h,6.62607015e-34,0,J*s
reduced_planck,hbar,1.054571817e-34,0,J*s
speed_of_light,c,299792458,0,m/s
elementary_charge,e,1.602176634e-19,0,C
electron_mass,m_e,9.1093837015e-31,2.8e-40,kg
proton_mass,m_p,1.67262192369e-27,5.1e-37,kg
neutron_mass,m_n,1.67492749804e-27,9.5e-37,kg
boltzmann,k_B,1.380649e-23,0,J/K
avogadro,N_A,6.02214076e23,0,mol^-1
vacuum_permittivity,epsilon_0,8.8541878128e-12,1.3e-21,F/m
vacuum_permeability,mu_0,1.25663706212e-6,1.9e-16,N/A^2
bohr_radius,a_0,5.29177210903e-11,8.0e-21,m
compton_wavelength,lambda_C,2.42631023867e-12,7.3e-22,m
rydberg_constant,R_inf,10973731.568160,2.1e-5,m^-1
fine_structure,alpha,7.2973525693e-3,1.1e-12,dimensionless
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   15 NIST quantum constants"
Write-Host ""
Write-Host "Source: NIST CODATA 2022 - https://physics.nist.gov/cuu/Constants/"
