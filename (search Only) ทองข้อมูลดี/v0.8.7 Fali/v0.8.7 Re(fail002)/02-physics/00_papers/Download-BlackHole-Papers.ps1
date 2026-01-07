#==============================================================================
# BLACK HOLE + UET RESEARCH PAPERS DOWNLOAD SCRIPT (POWERSHELL VERSION)
# Day 2 - Get The Ammunition!
#==============================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     BLACK HOLE + UET RESEARCH - PAPER DOWNLOAD SCRIPT          " -ForegroundColor Cyan
Write-Host "     Windows PowerShell Edition                                 " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PapersDir = Join-Path $ScriptDir "papers"

# Create directory structure
Write-Host "[SETUP] Creating folder structure..." -ForegroundColor Yellow

$folders = @(
    "$PapersDir\CCBH-Support",
    "$PapersDir\CCBH-Critics", 
    "$PapersDir\BH-Thermodynamics",
    "$PapersDir\BH-Observations"
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
# PAPER 1: Farrah 2023 ApJL - CCBH Main Evidence
#==============================================================================
Write-Host "[1/$Total] Farrah et al. 2023 - Observational Evidence for CCBH" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "2302.07878" -Filename "Farrah_2023_ApJL_CCBH_Evidence" -Folder "CCBH-Support") { $Success++ }

#==============================================================================
# PAPER 2: Farrah 2023 ApJ - Preferential Growth
#==============================================================================
Write-Host "[2/$Total] Farrah et al. 2023 - Preferential Growth Channel" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "2212.06854" -Filename "Farrah_2023_ApJ_Preferential_Growth" -Folder "CCBH-Support") { $Success++ }

#==============================================================================
# PAPER 3: Mistele 2023 - Criticism
#==============================================================================
Write-Host "[3/$Total] Mistele 2023 - Comment on CCBH" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "2304.09817" -Filename "Mistele_2023_CCBH_Criticism" -Folder "CCBH-Critics") { $Success++ }

#==============================================================================
# PAPER 4: Lacy 2023 - Accretion Constraints
#==============================================================================
Write-Host "[4/$Total] Lacy et al. 2023 - Accretion History Constraints" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "2312.12344" -Filename "Lacy_2023_Accretion_Constraints" -Folder "CCBH-Critics") { $Success++ }

#==============================================================================
# PAPER 5: Lei 2024 - JWST High-z Test
#==============================================================================
Write-Host "[5/$Total] Lei et al. 2024 - JWST High-z AGN Test" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "2305.03408" -Filename "Lei_2024_JWST_CCBH_Test" -Folder "CCBH-Critics") { $Success++ }

#==============================================================================
# PAPER 6: Witten 2025 - Modern BH Thermodynamics Review (THE BIG ONE!)
#==============================================================================
Write-Host "[6/$Total] Witten 2025 - Introduction to BH Thermodynamics (150 pages!)" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "2412.16795" -Filename "Witten_2025_BH_Thermodynamics_Review" -Folder "BH-Thermodynamics") { $Success++ }

#==============================================================================
# PAPER 7: Hawking 1974 - BLACK HOLE RADIATION (Paywall - Create README)
#==============================================================================
Write-Host "[7/$Total] Hawking 1974 - Black Hole Explosions (Paywall)" -ForegroundColor Cyan
Write-Host "[INFO] Creating citation info for paywalled paper..." -ForegroundColor Yellow

$hawkingFile = Join-Path $PapersDir "BH-Thermodynamics\Hawking_1974_README.txt"
$hawkingText = "Hawking S.W. 1974 - Black hole explosions - Nature 248 30-31`r`nDOI: 10.1038/248030a0`r`n`r`nSTATUS: Behind paywall`r`n`r`nKEY RESULT: T_H = hbar c^3 / 8 pi G M k_B`r`n`r`nThis is THE paper that introduced Hawking radiation!"
$hawkingText | Out-File -FilePath $hawkingFile -Encoding UTF8
Write-Host "[OK] Created Hawking_1974_README.txt" -ForegroundColor Green
Write-Host ""
$Success++

#==============================================================================
# PAPER 8: Bekenstein 1973 - ENTROPY (Paywall - Create README)
#==============================================================================
Write-Host "[8/$Total] Bekenstein 1973 - Black Holes and Entropy (Paywall)" -ForegroundColor Cyan
Write-Host "[INFO] Creating citation info for paywalled paper..." -ForegroundColor Yellow

$bekensteinFile = Join-Path $PapersDir "BH-Thermodynamics\Bekenstein_1973_README.txt"
$bekensteinText = "Bekenstein J.D. 1973 - Black Holes and Entropy - Phys Rev D 7 2333-2346`r`nDOI: 10.1103/PhysRevD.7.2333`r`n`r`nSTATUS: Behind paywall`r`n`r`nKEY RESULT: S_BH = k_B A / 4 L_Planck^2`r`n`r`nGOOD NEWS: Witten 2025 review covers this thoroughly!"
$bekensteinText | Out-File -FilePath $bekensteinFile -Encoding UTF8
Write-Host "[OK] Created Bekenstein_1973_README.txt" -ForegroundColor Green
Write-Host ""
$Success++

#==============================================================================
# PAPER 9: EHT 2019 - First Black Hole Image
#==============================================================================
Write-Host "[9/$Total] EHT Collaboration 2019 - First M87 Image" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "1906.11238" -Filename "EHT_2019_M87_First_Image" -Folder "BH-Observations") { $Success++ }

#==============================================================================
# PAPER 10: Wang & Wang 2023 - Decoupling Argument
#==============================================================================
Write-Host "[10/$Total] Wang and Wang 2023 - Decoupling Argument" -ForegroundColor Cyan
if (Download-ArxivPaper -ArxivId "2304.01059" -Filename "Wang_Wang_2023_Decoupling" -Folder "CCBH-Critics") { 
    $Success++ 
}
else {
    Write-Host "[INFO] Creating search info..." -ForegroundColor Yellow
    $wangFile = Join-Path $PapersDir "CCBH-Critics\Wang_Wang_2023_README.txt"
    $wangText = "Wang and Wang 2023 - Decoupling argument`r`n`r`nMAIN CLAIM: Black holes decouple from cosmic expansion (Birkhoff theorem)`r`nTherefore CCBH impossible within GR.`r`n`r`nSearch on Google Scholar if needed."
    $wangText | Out-File -FilePath $wangFile -Encoding UTF8
    Write-Host "[OK] Created Wang_Wang_2023_README.txt" -ForegroundColor Green
    Write-Host ""
    $Success++
}

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
Write-Host "  CCBH-Support/       - Farrah papers (pro-CCBH)"
Write-Host "  CCBH-Critics/       - Mistele, Lacy, Lei, Wang (anti-CCBH)"
Write-Host "  BH-Thermodynamics/  - Witten, Hawking, Bekenstein"
Write-Host "  BH-Observations/    - EHT 2019"
Write-Host ""
Write-Host "NEXT: Start with Witten 2025 - comprehensive review!" -ForegroundColor Yellow
Write-Host ""
Write-Host "GOOD LUCK!" -ForegroundColor Green
Write-Host ""
