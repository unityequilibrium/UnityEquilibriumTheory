"""
UET Truth Auditor
=================
Verifies that UET research topics are actually driven by the physical core.
Method: Runs engines with the INTEGRITY_KILL_SWITCH=TRUE. 
If simulation metrics remain valid, the topic is using SHADOW MATH.
"""

import os
import sys
import importlib
import importlib.util
import numpy as np
from pathlib import Path

# Ensure project root is in path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def audit_topic(topic_path: str, engine_class_name: str):
    print(f"\n🔍 AUDITING: {topic_path} ({engine_class_name})")
    
    # 1. Set Kill Switch
    os.environ["UET_KILL_ENGINE"] = "TRUE"
    
    try:
        # Import the engine dynamically from file path to handle dots in folder names
        abs_path = os.path.abspath(topic_path)
        spec = importlib.util.spec_from_file_location("dynamic_topic_module", abs_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {abs_path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        engine_class = getattr(module, engine_class_name)
        
        # 2. Run simulation
        engine = engine_class()
        engine.run(steps=10, verbose=False)
        report_path = engine.save_results()
        
        # If path is a directory, look for the analysis JSON inside it
        if os.path.isdir(report_path):
            json_files = list(Path(report_path).glob("*.json"))
            # Prioritize "analysis" files
            analysis_files = [f for f in json_files if "analysis" in f.name]
            if analysis_files:
                report_path = str(analysis_files[0])
            elif json_files:
                report_path = str(json_files[0])
            else:
                raise FileNotFoundError(f"No JSON report found in directory {report_path}")
        
        # 3. Analyze Results
        import json
        with open(report_path, "r") as f:
            report = json.load(f)
        
        # Determine the final state (handle List or Dict)
        if isinstance(report, list):
            if len(report) == 0:
                final_state = {}
            else:
                final_state = report[-1]
        else:
            final_state = report.get("final_state", report)

        # Check for ANY non-zero numeric indicators of work
        # If the kill switch is on, everything should be 0.0 or NaN
        evidence = []
        for key, val in final_state.items():
            if isinstance(val, (int, float)):
                if not np.isnan(val) and abs(val) > 1e-12:
                    evidence.append(f"{key}={val}")

        if not evidence:
            print(f"✅ TRUTH VERIFIED: Core dependency confirmed. (Outputs were 0/NaN)")
            return True
        else:
            print(f"❌ SHADOW MATH DETECTED: System produced results without core parameters!")
            print(f"   Evidence: {', '.join(evidence[:5])}...")
            return False
            
    except Exception as e:
        print(f"⚠️ AUDIT ERROR: {e}")
        return None
    finally:
        os.environ["UET_KILL_ENGINE"] = "FALSE"

if __name__ == "__main__":
    print("="*60)
    print("        UET RESEARCH INTEGRITY AUDIT (TRUTH PURGE)        ")
    print("="*60)
    
    results = []
    
    # Sample Topics to Audit
    topics = [
        ("docs/topics/0.3_Cosmology_Hubble_Tension/Code/01_Engine/Engine_Cosmology.py", "UETCosmologyEngine"),
        ("docs/topics/0.32_Micro_Nuclear_Fusion/Code/01_Engine/Engine_Nuclear_Fusion.py", "UETNuclearFusionEngine"),
        ("docs/topics/0.34_Information_Centric_Nanofabrication/Code/01_Engine/Engine_ICN_Deposition.py", "ICNEngine"),
    ]
    
    for path, name in topics:
        res = audit_topic(path, name)
        results.append((path, res))
        
    print("\n" + "="*60)
    print("FINAL AUDIT SUMMARY")
    print("="*60)
    for path, res in results:
        status = "PASSED (HONEST)" if res else "FAILED (FRAUD/ERROR)"
        print(f"[{status}] {path}")
