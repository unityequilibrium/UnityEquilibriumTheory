import os


class ReferenceRegistry:
    def __init__(self):
        self.topic = "0.29_Ocean_Recovery"
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.pdf_dir = os.path.join(self.base_dir, "PDF_Downloads")
        self.data_dir = os.path.join(self.base_dir, "Data_Source")

        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def get_references(self):
        return {
            "DATA_01": {
                "title": "NOAA Coral Reef Watch Daily Global 5km Satellite Coral Bleaching Heat Stress Monitoring",
                "author": "NOAA",
                "year": 2024,
                "url": "https://coralreefwatch.noaa.gov/product/5km/index.php",
                "category": "Dataset",
                "file": "NOAA_CRW_Global_Heat_Stress_2024.json",
            },
            "PAPER_01": {
                "title": "Thermal conductivity of graphene-based polymer composites",
                "author": "Huang et al.",
                "year": 2012,
                "journal": "Progress in Materials Science",
                "file": "Huang_2012_Graphene_Conductivity.pdf",
            },
            "PAPER_02": {
                "title": "Geopolymer concrete for structural use: Recent findings and limitations",
                "author": "Hassan et al.",
                "year": 2019,
                "journal": "Construction and Building Materials",
                "file": "Hassan_2019_Geopolymer_Structure.pdf",
            },
            "PAPER_03": {
                "title": "Valuing the ecosystem services of coral reefs",
                "author": "Costanza et al.",
                "year": 2014,
                "journal": "Global Environmental Change",
                "file": "Costanza_2014_Reef_Valuation.pdf",
            },
        }

    def mock_download(self):
        """
        Since we cannot actually access the internet for large files in this env,
        we generate 'Mock Data' that mimics the structure of real datasets.
        """
        import json

        # 1. Generate NOAA Mock Data (Global Heat Stress Map)
        # 20 Key Reef Locations with specific Lat/Lon and Max Annual Temp
        reef_data = [
            {
                "name": "Great Barrier Reef (North)",
                "lat": -10.5,
                "lon": 145.0,
                "max_temp": 32.5,
                "bleaching_risk": "Severe",
            },
            {
                "name": "Great Barrier Reef (South)",
                "lat": -23.5,
                "lon": 151.0,
                "max_temp": 29.8,
                "bleaching_risk": "Low",
            },
            {
                "name": "Andaman Sea (Thailand)",
                "lat": 7.5,
                "lon": 98.3,
                "max_temp": 32.2,
                "bleaching_risk": "Severe",
            },
            {
                "name": "Maldives (Indian Ocean)",
                "lat": 3.2,
                "lon": 73.2,
                "max_temp": 31.8,
                "bleaching_risk": "High",
            },
            {
                "name": "Red Sea (Egypt)",
                "lat": 27.0,
                "lon": 34.0,
                "max_temp": 30.5,
                "bleaching_risk": "Moderate",
            },
            {
                "name": "Hawaii (Kona)",
                "lat": 19.6,
                "lon": -156.0,
                "max_temp": 29.5,
                "bleaching_risk": "Low",
            },
            {
                "name": "Caribbean (Bahamas)",
                "lat": 24.0,
                "lon": -77.5,
                "max_temp": 30.8,
                "bleaching_risk": "Moderate",
            },
            {
                "name": "Florida Keys (USA)",
                "lat": 24.6,
                "lon": -81.5,
                "max_temp": 32.0,
                "bleaching_risk": "Severe",
            },
            {
                "name": "Persian Gulf (Qatar)",
                "lat": 25.3,
                "lon": 51.5,
                "max_temp": 35.0,
                "bleaching_risk": "Extreme",
            },
            {
                "name": "Coral Triangle (Indonesia)",
                "lat": -2.5,
                "lon": 125.0,
                "max_temp": 31.5,
                "bleaching_risk": "High",
            },
        ]

        target_path = os.path.join(self.data_dir, "NOAA_CRW_Global_Heat_Stress_2024.json")
        with open(target_path, "w") as f:
            json.dump(reef_data, f, indent=4)

        print(f"✅ Downloaded (Mock): {target_path}")

        # 2. Touch PDF Placeholders
        refs = self.get_references()
        for key, val in refs.items():
            if "pdf" in val["file"].lower():
                fpath = os.path.join(self.pdf_dir, val["file"])
                with open(fpath, "w") as f:
                    f.write("Placeholder PDF content")
                print(f"✅ Downloaded (Mock): {fpath}")


if __name__ == "__main__":
    reg = ReferenceRegistry()
    reg.mock_download()
