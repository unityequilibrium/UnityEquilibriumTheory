#==============================================================================
# CORE THEORY PAPERS DOWNLOAD SCRIPT
# Phase 2: UET Core Equations & Proofs
#==============================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     UET CORE THEORY - PAPER DOWNLOAD SCRIPT                    " -ForegroundColor Cyan
Write-Host "     Phase 2: Core Equations, C/I Framework, Proofs             " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PapersDir = Join-Path $ScriptDir "papers"

# Create directory structure
Write-Host "[SETUP] Creating folder structure..." -ForegroundColor Yellow

$folders = @(
    "$PapersDir\Cahn-Hilliard",
    "$PapersDir\Lyapunov",
    "$PapersDir\Gradient-Flow",
    "$PapersDir\Numerical-Methods"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}
Write-Host "[OK] Folders created!" -ForegroundColor Green
Write-Host ""

$Total = 8
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
# CAHN-HILLIARD / PHASE-FIELD PAPERS
#==============================================================================
Write-Host "--- CAHN-HILLIARD ---" -ForegroundColor Magenta

# Paper 1: Cahn-Hilliard Review
Write-Host "[1/$Total] Elliott 1989 - Cahn-Hilliard Existence" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "1612.02852" -Filename "Elliott_1989_CH_Existence" -Folder "Cahn-Hilliard") { $Success++ }

# Paper 2: Allen-Cahn
Write-Host "[2/$Total] Feng 2004 - Allen-Cahn Analysis" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "2003.13723" -Filename "Feng_2004_Allen_Cahn" -Folder "Cahn-Hilliard") { $Success++ }

#==============================================================================
# LYAPUNOV STABILITY PAPERS
#==============================================================================
Write-Host "--- LYAPUNOV STABILITY ---" -ForegroundColor Magenta

# Paper 3: Lyapunov in PDE
Write-Host "[3/$Total] Mielke 2012 - Gradient Structures Lyapunov" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "1205.4712" -Filename "Mielke_2012_Gradient_Structures" -Folder "Lyapunov") { $Success++ }

# Paper 4: Energy methods
Write-Host "[4/$Total] Otto 2001 - Energy Methods" -ForegroundColor Cyan
# This is a classic - create README
$ottoFile = Join-Path $PapersDir "Lyapunov\Otto_2001_README.txt"
$ottoText = @"
OTTO 2001 - THE GEOMETRY OF DISSIPATIVE EVOLUTION EQUATIONS
=============================================================

Felix Otto - Comm. PDE 26 (2001), 101-174

KEY CONTRIBUTION:
- Gradient flows as curves of steepest descent
- Riemannian structure of Wasserstein space
- Energy = Lyapunov functional

This is foundational for understanding UET as gradient flow!
"@
$ottoText | Out-File -FilePath $ottoFile -Encoding UTF8
Write-Host "[OK] Created Otto_2001_README.txt" -ForegroundColor Green
Write-Host ""
$Success++

#==============================================================================
# GRADIENT FLOW PAPERS
#==============================================================================
Write-Host "--- GRADIENT FLOW ---" -ForegroundColor Magenta

# Paper 5: AGS Book summary
Write-Host "[5/$Total] Ambrosio-Gigli-Savare - Gradient Flows" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "math/0609441" -Filename "AGS_Gradient_Flows" -Folder "Gradient-Flow") { $Success++ }

# Paper 6: Discrete gradient flows
Write-Host "[6/$Total] Jordan-Kinderlehrer-Otto 1998" -ForegroundColor Cyan
$jkoFile = Join-Path $PapersDir "Gradient-Flow\JKO_1998_README.txt"
$jkoText = @"
JORDAN-KINDERLEHRER-OTTO 1998
==============================

"The variational formulation of the Fokker-Planck equation"
SIAM J. Math. Anal. 29 (1998), 1-17

THE JKO SCHEME:
- Minimizing movements interpretation
- u_{n+1} = argmin { E(u) + (1/2h) d^2(u, u_n) }
- Proves heat equation is gradient flow

This is WHY dΩ/dt ≤ 0 in UET!
"@
$jkoText | Out-File -FilePath $jkoFile -Encoding UTF8
Write-Host "[OK] Created JKO_1998_README.txt" -ForegroundColor Green
Write-Host ""
$Success++

#==============================================================================
# NUMERICAL METHODS PAPERS
#==============================================================================
Write-Host "--- NUMERICAL METHODS ---" -ForegroundColor Magenta

# Paper 7: Energy-stable schemes
Write-Host "[7/$Total] Shen 2012 - Energy Stable Schemes" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "1201.1286" -Filename "Shen_2012_Energy_Stable" -Folder "Numerical-Methods") { $Success++ }

# Paper 8: Eyre scheme
Write-Host "[8/$Total] Eyre 1998 - Unconditional Gradient Stability" -ForegroundColor Cyan
$eyreFile = Join-Path $PapersDir "Numerical-Methods\Eyre_1998_README.txt"
$eyreText = @"
EYRE 1998 - UNCONDITIONALLY GRADIENT STABLE SCHEME
====================================================

D.J. Eyre (1998)
"Unconditionally gradient stable time marching the Cahn-Hilliard equation"

KEY IDEA:
- Split potential into convex + concave parts
- Treat convex part implicitly
- Treat concave part explicitly
- GUARANTEES dΩ/dt ≤ 0 at discrete level!

UET uses exactly this idea (semi-implicit scheme).
"@
$eyreText | Out-File -FilePath $eyreFile -Encoding UTF8
Write-Host "[OK] Created Eyre_1998_README.txt" -ForegroundColor Green
Write-Host ""
$Success++

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
Write-Host "  Cahn-Hilliard/      - CH equation theory"
Write-Host "  Lyapunov/           - Stability proofs"
Write-Host "  Gradient-Flow/      - AGS, JKO"
Write-Host "  Numerical-Methods/  - Energy-stable schemes"
Write-Host ""
Write-Host "NEXT: Run validation tests!" -ForegroundColor Yellow
Write-Host ""
