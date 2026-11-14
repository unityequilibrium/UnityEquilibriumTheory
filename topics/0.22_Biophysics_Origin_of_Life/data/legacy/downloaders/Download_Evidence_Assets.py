import os
import requests


def download_research_assets():
    print("📥 UET ASSET GATHERING: DOWNLOADING ACADEMIC EVIDENCE")
    print("=" * 60)

    # Target directory
    target_dir = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics\0.22_Biophysics_Origin_of_Life\Ref\03_Research"

    # Assets to download (Using known open access or summary links where available)
    # Note: Direct PDF download depends on server permissions.
    assets = {
        "Davies_Walker_2016_InfoTheory.pdf": "https://royalsocietypublishing.org/doi/pdf/10.1098/rsif.2016.0351",
        "TCGA_Data_Portal_Guide.pdf": "https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Data_Portal_Users_Guide.pdf",
    }

    for filename, url in assets.items():
        filepath = os.path.join(target_dir, filename)
        print(f"Attempting to download: {filename}...")
        try:
            response = requests.get(url, stream=True, timeout=15)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  ✅ SUCCESS: Saved to {filepath}")
            else:
                print(f"  ❌ FAILED: Status code {response.status_code}")
        except Exception as e:
            print(f"  ⚠️ ERROR: {str(e)}")


if __name__ == "__main__":
    download_research_assets()
