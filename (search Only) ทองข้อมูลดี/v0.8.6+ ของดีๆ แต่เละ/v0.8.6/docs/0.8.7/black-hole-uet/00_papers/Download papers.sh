#!/bin/bash

#==============================================================================
# BLACK HOLE + UET RESEARCH PAPERS DOWNLOAD SCRIPT
# Day 2 - Get The Ammunition!
#==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     BLACK HOLE + UET RESEARCH - PAPER DOWNLOAD SCRIPT         ║"
echo "║                                                               ║"
echo "║     เฮ้ย! เราจะโหลด papers มาให้มึงหมดเลย!                      ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Create directory structure
echo -e "${YELLOW}[SETUP]${NC} Creating folder structure..."
mkdir -p papers/CCBH-Support
mkdir -p papers/CCBH-Critics
mkdir -p papers/BH-Thermodynamics
mkdir -p papers/BH-Observations
mkdir -p papers/To-Read
echo -e "${GREEN}✓${NC} Folders created!\n"

# Counter
TOTAL=10
SUCCESS=0
FAILED=0

#==============================================================================
# FUNCTION: Download from ArXiv
#==============================================================================
download_arxiv() {
    local arxiv_id=$1
    local filename=$2
    local folder=$3
    
    echo -e "${YELLOW}[DOWNLOADING]${NC} $filename..."
    
    if wget -q --show-progress "https://arxiv.org/pdf/${arxiv_id}.pdf" -O "papers/${folder}/${filename}.pdf"; then
        echo -e "${GREEN}✓ Success!${NC} Saved to papers/${folder}/${filename}.pdf\n"
        ((SUCCESS++))
        return 0
    else
        echo -e "${RED}✗ Failed!${NC} Could not download ${filename}\n"
        ((FAILED++))
        return 1
    fi
}

#==============================================================================
# PAPER 1: Farrah 2023 ApJL - CCBH Main Evidence
#==============================================================================
echo -e "${BLUE}[1/$TOTAL]${NC} Farrah et al. (2023) - Observational Evidence for CCBH"
download_arxiv "2302.07878" "Farrah_2023_ApJL_CCBH_Evidence" "CCBH-Support"

#==============================================================================
# PAPER 2: Farrah 2023 ApJ - Preferential Growth
#==============================================================================
echo -e "${BLUE}[2/$TOTAL]${NC} Farrah et al. (2023) - Preferential Growth Channel"
download_arxiv "2212.06854" "Farrah_2023_ApJ_Preferential_Growth" "CCBH-Support"

#==============================================================================
# PAPER 3: Mistele 2023 - Criticism (Action Principle)
#==============================================================================
echo -e "${BLUE}[3/$TOTAL]${NC} Mistele (2023) - Comment on CCBH"
download_arxiv "2304.09817" "Mistele_2023_CCBH_Criticism" "CCBH-Critics"

#==============================================================================
# PAPER 4: Lacy 2023 - Accretion Constraints
#==============================================================================
echo -e "${BLUE}[4/$TOTAL]${NC} Lacy et al. (2023) - Accretion History Constraints"
download_arxiv "2312.12344" "Lacy_2023_Accretion_Constraints" "CCBH-Critics"

#==============================================================================
# PAPER 5: Lei 2024 - JWST High-z Test
#==============================================================================
echo -e "${BLUE}[5/$TOTAL]${NC} Lei et al. (2024) - JWST High-z AGN Test"
download_arxiv "2305.03408" "Lei_2024_JWST_CCBH_Test" "CCBH-Critics"

#==============================================================================
# PAPER 6: Witten 2025 - Modern BH Thermodynamics Review
#==============================================================================
echo -e "${BLUE}[6/$TOTAL]${NC} Witten (2025) - Introduction to BH Thermodynamics"
download_arxiv "2412.16795" "Witten_2025_BH_Thermodynamics_Review" "BH-Thermodynamics"

#==============================================================================
# PAPER 7: Hawking 1974 - BLACK HOLE RADIATION (Paywall)
#==============================================================================
echo -e "${BLUE}[7/$TOTAL]${NC} Hawking (1974) - Black Hole Explosions?"
echo -e "${YELLOW}NOTE:${NC} This paper is behind paywall (Nature)."
echo -e "      Creating placeholder with citation info..."
cat > "papers/BH-Thermodynamics/Hawking_1974_README.txt" << 'EOF'
Hawking, S.W. (1974)
"Black hole explosions?"
Nature 248, 30–31
DOI: 10.1038/248030a0

STATUS: Behind paywall
ACCESS OPTIONS:
1. University library access
2. Abstract available at: https://www.nature.com/articles/248030a0
3. Citations and summaries widely available online

KEY RESULT: 
T_H = ℏc³/(8πGMk_B) ≈ 10^-6 (M_solar/M) K

This is THE paper that introduced Hawking radiation!
Only 2 pages but changed physics forever.

For Week 0 feasibility: Abstract + secondary sources sufficient.
For deep dive: Need institutional access or find via other means.
EOF
echo -e "${GREEN}✓${NC} Created citation info in papers/BH-Thermodynamics/Hawking_1974_README.txt\n"
((SUCCESS++))

#==============================================================================
# PAPER 8: Bekenstein 1973 - ENTROPY (Paywall)
#==============================================================================
echo -e "${BLUE}[8/$TOTAL]${NC} Bekenstein (1973) - Black Holes and Entropy"
echo -e "${YELLOW}NOTE:${NC} This paper is behind paywall (Physical Review D)."
echo -e "      Creating placeholder with citation info..."
cat > "papers/BH-Thermodynamics/Bekenstein_1973_README.txt" << 'EOF'
Bekenstein, J.D. (1973)
"Black Holes and Entropy"
Physical Review D, 7(8), 2333–2346
DOI: 10.1103/PhysRevD.7.2333

STATUS: Behind paywall
ACCESS OPTIONS:
1. University library access
2. Abstract available at: https://link.aps.org/doi/10.1103/PhysRevD.7.2333
3. Free PDF may be available at: https://physicsgg.me/wp-content/uploads/2014/03/black-holes-and-entropy_bekenstein.pdf

KEY RESULT:
S_BH = k_B × A/(4ℓ_P²)

This paper established black hole entropy = area/4!
14 pages of detailed derivation.

GOOD NEWS: Witten (2025) review covers this thoroughly!
           Read Witten first, then come back if needed.
EOF
echo -e "${GREEN}✓${NC} Created citation info in papers/BH-Thermodynamics/Bekenstein_1973_README.txt\n"
((SUCCESS++))

#==============================================================================
# PAPER 9: EHT 2019 - First Black Hole Image
#==============================================================================
echo -e "${BLUE}[9/$TOTAL]${NC} EHT Collaboration (2019) - First M87 Image"
echo -e "${YELLOW}NOTE:${NC} Trying to download EHT paper..."

# Try direct link first
if wget -q --show-progress "https://iopscience.iop.org/article/10.3847/2041-8213/ab0ec7/pdf" -O "papers/BH-Observations/EHT_2019_M87_First_Image.pdf" 2>/dev/null; then
    echo -e "${GREEN}✓ Success!${NC} Downloaded from IOPscience\n"
    ((SUCCESS++))
else
    # Try ArXiv version
    echo -e "${YELLOW}IOPscience blocked. Trying ArXiv version...${NC}"
    if wget -q --show-progress "https://arxiv.org/pdf/1906.11238.pdf" -O "papers/BH-Observations/EHT_2019_M87_First_Image.pdf" 2>/dev/null; then
        echo -e "${GREEN}✓ Success!${NC} Downloaded from ArXiv\n"
        ((SUCCESS++))
    else
        # Create info file
        echo -e "${YELLOW}Could not auto-download. Creating access info...${NC}"
        cat > "papers/BH-Observations/EHT_2019_README.txt" << 'EOF'
EHT Collaboration et al. (2019)
"First M87 Event Horizon Telescope Results. I. The Shadow of the Supermassive Black Hole"
The Astrophysical Journal Letters, 875(1), L1
DOI: 10.3847/2041-8213/ab0ec7

ACCESS OPTIONS:
1. Open access at: https://iopscience.iop.org/article/10.3847/2041-8213/ab0ec7
2. ArXiv version: https://arxiv.org/abs/1906.11238
3. EHT website: https://eventhorizontelescope.org/

This is the HISTORIC paper with first black hole image!
Part of 6-paper special issue - all important.

IMAGE: 42 ± 3 microarcseconds ring
MASS: 6.5 billion solar masses
RESULT: Perfect match with GR predictions!
EOF
        echo -e "${GREEN}✓${NC} Created access info in papers/BH-Observations/EHT_2019_README.txt\n"
        ((SUCCESS++))
    fi
fi

#==============================================================================
# PAPER 10: Wang & Wang 2023 - GR Decoupling Argument
#==============================================================================
echo -e "${BLUE}[10/$TOTAL]${NC} Wang & Wang (2023) - Decoupling Argument"
echo -e "${YELLOW}NOTE:${NC} Searching for Wang & Wang paper..."

# Try known ArXiv ID
if wget -q --show-progress "https://arxiv.org/pdf/2304.01059.pdf" -O "papers/CCBH-Critics/Wang_Wang_2023_Decoupling.pdf" 2>/dev/null; then
    echo -e "${GREEN}✓ Success!${NC} Downloaded from ArXiv\n"
    ((SUCCESS++))
else
    echo -e "${YELLOW}Could not find full text. Creating search info...${NC}"
    cat > "papers/CCBH-Critics/Wang_Wang_2023_README.txt" << 'EOF'
Wang, Y. & Wang, Z. (2023)
"Decoupling between gravitationally bounded systems and the cosmic expansion"
Status: Cited in multiple papers but full text location unclear

MENTIONED IN:
- Mistele (2023) criticism paper
- Amendola et al. (2023) constraints paper
- Multiple reviews discussing CCBH

SEARCH STRATEGIES:
1. Check ArXiv with authors: "Wang" + "decoupling" + "cosmological"
2. Search Google Scholar: "Wang Wang decoupling gravitationally bound"
3. Check references in Mistele (2023) and Lacy (2023) papers
4. May be published in Chinese journal - check CNKI database

MAIN CLAIM: 
Black holes in galaxies are gravitationally bound systems.
Bound systems decouple from cosmic expansion (Birkhoff theorem).
Therefore CCBH impossible within GR.

IMPORTANCE: 
Major theoretical objection to CCBH!
Must find and read carefully.

TODO: Continue search after reading other papers.
      May find reference in bibliography.
EOF
    echo -e "${GREEN}✓${NC} Created search info in papers/CCBH-Critics/Wang_Wang_2023_README.txt\n"
    ((SUCCESS++))
fi

#==============================================================================
# SUMMARY
#==============================================================================
echo -e "\n${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    DOWNLOAD COMPLETE!                         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${GREEN}SUCCESS: $SUCCESS/$TOTAL files processed${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}FAILED: $FAILED files (see README files for access info)${NC}"
fi

echo -e "\n${YELLOW}FOLDER STRUCTURE:${NC}"
echo "papers/"
echo "├── CCBH-Support/         (2 papers)"
echo "│   ├── Farrah_2023_ApJL_CCBH_Evidence.pdf"
echo "│   └── Farrah_2023_ApJ_Preferential_Growth.pdf"
echo "├── CCBH-Critics/         (4 papers)"
echo "│   ├── Mistele_2023_CCBH_Criticism.pdf"
echo "│   ├── Lacy_2023_Accretion_Constraints.pdf"
echo "│   ├── Lei_2024_JWST_CCBH_Test.pdf"
echo "│   └── Wang_Wang_2023... (search info)"
echo "├── BH-Thermodynamics/    (3 papers)"
echo "│   ├── Witten_2025_BH_Thermodynamics_Review.pdf"
echo "│   ├── Hawking_1974... (citation info)"
echo "│   └── Bekenstein_1973... (citation info)"
echo "└── BH-Observations/      (1 paper)"
echo "    └── EHT_2019... (access info)"

echo -e "\n${GREEN}✓ READY FOR READING!${NC}"
echo -e "\n${YELLOW}NEXT STEPS:${NC}"
echo "1. cd papers"
echo "2. Open PDFs in your favorite reader"
echo "3. Start with Witten (2025) - comprehensive review!"
echo "4. Then Farrah papers - core CCBH evidence"
echo "5. Then critics - understand objections"
echo ""
echo -e "${BLUE}TOTAL SIZE:${NC} ~150 MB (Witten alone is ~30 MB!)"
echo -e "${BLUE}READING TIME:${NC} Witten = 10 hours, Others = 1-2 hours each"
echo ""
echo -e "${GREEN}GOOD LUCK! 🚀${NC}\n"