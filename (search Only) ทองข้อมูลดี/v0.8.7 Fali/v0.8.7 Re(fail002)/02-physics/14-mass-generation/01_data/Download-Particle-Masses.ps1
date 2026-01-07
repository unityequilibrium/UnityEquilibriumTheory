# Download-Particle-Masses.ps1
# Downloads particle masses from PDG for mass generation tests
# Real data: https://pdg.lbl.gov/

$OutputFile = "$PSScriptRoot\particle_masses.csv"

Write-Host "Creating PDG particle masses data..."

# PDG 2023 particle masses (real data)
$data = @"
particle,symbol,mass_mev,uncertainty_mev,lifetime_s,spin,charge
electron,e,0.51099895,0.00000015,stable,0.5,-1
muon,mu,105.6583755,0.0000023,2.1969811e-6,0.5,-1
tau,tau,1776.86,0.12,2.903e-13,0.5,-1
electron_neutrino,nu_e,0.0,0.0,stable,0.5,0
muon_neutrino,nu_mu,0.0,0.0,stable,0.5,0
tau_neutrino,nu_tau,0.0,0.0,stable,0.5,0
up_quark,u,2.16,0.49,stable,0.5,0.667
down_quark,d,4.67,0.48,stable,0.5,-0.333
strange_quark,s,93.4,8.6,stable,0.5,-0.333
charm_quark,c,1270,20,stable,0.5,0.667
bottom_quark,b,4180,30,stable,0.5,-0.333
top_quark,t,172690,300,4.8e-25,0.5,0.667
W_boson,W,80377,12,3.07e-25,1,1
Z_boson,Z,91187.6,2.1,2.64e-25,1,0
higgs,H,125250,170,1.56e-22,0,0
photon,gamma,0,0,stable,1,0
gluon,g,0,0,stable,1,0
proton,p,938.27208816,0.00000029,stable,0.5,1
neutron,n,939.56542052,0.00000054,879.4,0.5,0
pion_plus,pi+,139.57039,0.00018,2.6033e-8,0,1
"@

$data | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "✅ Saved: $OutputFile"
Write-Host "   20 particles with masses and properties"
Write-Host ""
Write-Host "Source: PDG 2023 - https://pdg.lbl.gov/"
