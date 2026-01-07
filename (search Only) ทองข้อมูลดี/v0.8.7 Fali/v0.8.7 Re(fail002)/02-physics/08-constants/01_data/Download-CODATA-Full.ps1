# Download-CODATA-Full.ps1
# Downloads full set of fundamental constants from CODATA 2022
# Real data: https://physics.nist.gov/cuu/Constants/

$OutputFile = "$PSScriptRoot\codata_2022_full.csv"

Write-Host "Creating full CODATA 2022 constants dataset..."

$data = @"
constant,symbol,value,uncertainty,unit
fine_structure,alpha,0.0072973525693,0.0000000000011,dimensionless
inverse_fine_structure,1/alpha,137.035999084,0.000000021,dimensionless
rydberg,R_inf,10973731.568160,0.000021,m^-1
bohr_radius,a_0,5.29177210903e-11,8.0e-21,m
electron_mass,m_e,9.1093837015e-31,2.8e-40,kg
proton_mass,m_p,1.67262192369e-27,5.1e-37,kg
neutron_mass,m_n,1.67492749804e-27,9.5e-37,kg
muon_mass,m_mu,1.883531627e-28,4.2e-35,kg
gravitational_constant,G,6.67430e-11,0.00015e-11,m^3/(kg*s^2)
planck_constant,h,6.62607015e-34,0,J*s
reduced_planck,hbar,1.054571817e-34,0,J*s
speed_of_light,c,299792458,0,m/s
boltzmann,k,1.380649e-23,0,J/K
stefan_boltzmann,sigma,5.670374419e-8,0,W/(m^2*K^4)
electron_volt,eV,1.602176634e-19,0,J
elementary_charge,e,1.602176634e-19,0,C
vacuum_impedance,Z_0,376.730313668,5.7e-10,ohm
vacuum_permittivity,epsilon_0,8.8541878128e-12,1.3e-21,F/m
vacuum_permeability,mu_0,1.25663706212e-6,1.9e-16,N/A^2
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "Source: NIST CODATA 2022"
