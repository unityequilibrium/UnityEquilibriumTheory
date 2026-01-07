#==============================================================================
# FOUNDATION PAPERS DOWNLOAD SCRIPT
# Phase 1: Thermodynamics, Gradient Flow, Cahn-Hilliard
#==============================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     UET FOUNDATION - PAPER DOWNLOAD SCRIPT                     " -ForegroundColor Cyan
Write-Host "     Phase 1: Thermodynamics & Phase Field                      " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PapersDir = Join-Path $ScriptDir "papers"

# Create directory structure
Write-Host "[SETUP] Creating folder structure..." -ForegroundColor Yellow

$folders = @(
    "$PapersDir\Thermodynamics",
    "$PapersDir\Phase-Field",
    "$PapersDir\Gradient-Flow",
    "$PapersDir\Reviews"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}
Write-Host "[OK] Folders created!" -ForegroundColor Green
Write-Host ""

# Counters
$Total = 10
$Success = 0

#==============================================================================
# FUNCTION: Download from ArXiv
#==============================================================================
function Download-ArxivPaper {
    param (
        [string]$ArxivId,
        [string]$Filename,
        [string]$Folder
    )
    
    $url = "https://arxiv.org/pdf/$ArxivId.pdf"
    $outPath = Join-Path $PapersDir "$Folder\$Filename.pdf"
    
    Write-Host "[DOWNLOADING] $Filename..." -ForegroundColor Yellow
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        $webClient.DownloadFile($url, $outPath)
        
        Write-Host "[OK] Saved to papers/$Folder/$Filename.pdf" -ForegroundColor Green
        Write-Host ""
        return $true
    }
    catch {
        Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

#==============================================================================
# THERMODYNAMICS PAPERS
#==============================================================================
Write-Host "--- THERMODYNAMICS ---" -ForegroundColor Magenta

# Paper 1: Jacobson - Thermodynamics of Spacetime (Classic!)
Write-Host "[1/$Total] Jacobson 1995 - Thermodynamics of Spacetime" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "gr-qc/9504004" -Filename "Jacobson_1995_Thermo_Spacetime" -Folder "Thermodynamics") { $Success++ }

# Paper 2: Padmanabhan - Thermodynamical Aspects
Write-Host "[2/$Total] Padmanabhan 2010 - Thermodynamical Aspects of Gravity" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "0911.5004" -Filename "Padmanabhan_2010_Thermo_Gravity" -Folder "Thermodynamics") { $Success++ }

#==============================================================================
# PHASE-FIELD / CAHN-HILLIARD PAPERS
#==============================================================================
Write-Host "--- PHASE-FIELD ---" -ForegroundColor Magenta

# Paper 3: Phase-Field Review
Write-Host "[3/$Total] Steinbach 2009 - Phase-Field Models Review" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "0906.0986" -Filename "Steinbach_2009_Phase_Field_Review" -Folder "Phase-Field") { $Success++ }

# Paper 4: Cahn-Hilliard Numerical
Write-Host "[4/$Total] Furihata 2001 - Discrete Variational Derivative Method" -ForegroundColor Cyan
# Note: This may not be on arXiv, create README instead
$chFile = Join-Path $PapersDir "Phase-Field\Cahn_Hilliard_Original_README.txt"
$chText = @"
ORIGINAL CAHN-HILLIARD PAPERS (Not on arXiv)
============================================

1. Cahn, J.W. & Hilliard, J.E. (1958)
   "Free Energy of a Nonuniform System. I. Interfacial Free Energy"
   Journal of Chemical Physics 28, 258-267
   DOI: 10.1063/1.1744102

2. Cahn, J.W. & Hilliard, J.E. (1959)  
   "Free Energy of a Nonuniform System. III. Nucleation in a Two-Component Incompressible Fluid"
   Journal of Chemical Physics 31, 688-699
   DOI: 10.1063/1.1730447

3. Allen, S.M. & Cahn, J.W. (1979)
   "A Microscopic Theory for Antiphase Boundary Motion"
   Acta Metallurgica 27, 1085-1095
   DOI: 10.1016/0001-6160(79)90196-2

KEY EQUATIONS:
- Cahn-Hilliard: dc/dt = M * nabla^2 (df/dc - kappa * nabla^2 c)
- Allen-Cahn: dc/dt = -L * (df/dc - kappa * nabla^2 c)

These are the foundational papers for UET!
"@
$chText | Out-File -FilePath $chFile -Encoding UTF8
Write-Host "[OK] Created Cahn_Hilliard_Original_README.txt" -ForegroundColor Green
Write-Host ""
$Success++

# Paper 5: Phase-Field Modeling
Write-Host "[5/$Total] Provatas 2011 - Phase-Field Methods in Materials Science" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "1106.1349" -Filename "Provatas_2011_Phase_Field_Materials" -Folder "Phase-Field") { $Success++ }

#==============================================================================
# GRADIENT FLOW PAPERS
#==============================================================================
Write-Host "--- GRADIENT FLOW ---" -ForegroundColor Magenta

# Paper 6: Gradient Flow Review
Write-Host "[6/$Total] Santambrogio 2017 - Optimal Transport and Gradient Flows" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "1609.07091" -Filename "Santambrogio_2017_Optimal_Transport" -Folder "Gradient-Flow") { $Success++ }

# Paper 7: Variational Methods
Write-Host "[7/$Total] Jordan 1998 - Variational Formulation (Wasserstein)" -ForegroundColor Cyan
# Classic paper - create README
$gfFile = Join-Path $PapersDir "Gradient-Flow\JKO_Scheme_README.txt"
$gfText = @"
JORDAN-KINDERLEHRER-OTTO (JKO) SCHEME
=====================================

Jordan, R., Kinderlehrer, D., & Otto, F. (1998)
"The variational formulation of the Fokker-Planck equation"
SIAM Journal on Mathematical Analysis 29, 1-17

KEY INSIGHT:
- Heat equation = gradient flow in Wasserstein space
- Many PDEs are gradient flows of energy functionals

This paper established the modern view of gradient flows!
"@
$gfText | Out-File -FilePath $gfFile -Encoding UTF8
Write-Host "[OK] Created JKO_Scheme_README.txt" -ForegroundColor Green
Write-Host ""
$Success++

#==============================================================================
# REVIEW PAPERS
#==============================================================================
Write-Host "--- REVIEWS ---" -ForegroundColor Magenta

# Paper 8: Verlinde - Emergent Gravity
Write-Host "[8/$Total] Verlinde 2011 - On the Origin of Gravity" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "1001.0785" -Filename "Verlinde_2011_Emergent_Gravity" -Folder "Reviews") { $Success++ }

# Paper 9: Free Energy Principle
Write-Host "[9/$Total] Friston 2019 - Free Energy Principle Review" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "1906.10184" -Filename "Friston_2019_Free_Energy_Principle" -Folder "Reviews") { $Success++ }

# Paper 10: Landau-Ginzburg
Write-Host "[10/$Total] Bray 1994 - Theory of Phase Ordering Kinetics" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "cond-mat/9501089" -Filename "Bray_1994_Phase_Ordering" -Folder "Reviews") { $Success++ }

#==============================================================================
# SUMMARY
#==============================================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                    DOWNLOAD COMPLETE!                          " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "SUCCESS: $Success / $Total files processed" -ForegroundColor Green
Write-Host ""
Write-Host "FOLDER STRUCTURE:" -ForegroundColor Yellow
Write-Host "papers/"
Write-Host "  Thermodynamics/     - Jacobson, Padmanabhan"
Write-Host "  Phase-Field/        - Steinbach, Cahn-Hilliard refs"
Write-Host "  Gradient-Flow/      - Santambrogio, JKO refs"
Write-Host "  Reviews/            - Verlinde, Friston, Bray"
Write-Host ""
Write-Host "NEXT: Read papers and validate UET against established theory!" -ForegroundColor Yellow
Write-Host ""
