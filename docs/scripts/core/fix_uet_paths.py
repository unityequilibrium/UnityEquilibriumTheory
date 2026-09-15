
# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP
import os
from pathlib import Path
import re

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. The Standard Replacement Block
    replacement_block = """import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)
"""

    # 2. Match patterns for deletion (Aggressive)
    # This matches the old block headers and their typical logic structure
    patterns_to_remove = [
        # Original multi-line block with PathFinder comment
        r"# --- ROBUST PATH FINDER.*?if str\(ROOT\) not in sys\.path:.*?sys\.exit\(1\)",
        # Improperly patched block from previous run (dangling else)
        r"# --- ROBUST UET BOOTSTRAP ---.*?ROOT = _bootstrap\(\)\s+else:.*?sys\.exit\(1\)",
        # Generic sys.path injection blocks
        r"import sys\s+from pathlib import Path\s+current_path = Path\(__file__\).*?if ROOT:.*?sys\.path\.insert\(0, str\(ROOT\)\)",
    ]
    
    new_content = content
    modified = False
    
    for pattern in patterns_to_remove:
        if re.search(pattern, new_content, re.DOTALL):
            new_content = re.sub(pattern, replacement_block, new_content, flags=re.DOTALL)
            modified = True
            break # Stop after first successful replacement of the block
            
    # 3. Fallback: If no block found but it tries to import docs, insert at top
    if not modified and ("from docs.core" in new_content or "import docs" in new_content):
        # Insert after docstring or at very top
        if new_content.startswith('"""'):
            end_doc = new_content.find('"""', 3)
            if end_doc != -1:
                new_content = new_content[:end_doc+3] + "\n\n" + replacement_block + new_content[end_doc+3:]
                modified = True
        else:
            new_content = replacement_block + "\n" + new_content
            modified = True

    # 4. Global string replacements
    old_strings = [
        ('uet_research', 'docs/topics'),
        ('research_uet', 'docs/topics'),
    ]
    
    for old, new in old_strings:
        if old in new_content:
            new_content = new_content.replace(old, new)
            modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    root_dir = _UET_REPO_ROOT / "docs" / "topics"
    fixed_count = 0
    checked_count = 0
    
    for root, dirs, files in os.walk(root_dir):
        if "_Logs" in root or "__pycache__" in root or ".venv" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                checked_count += 1
                if fix_file(Path(root) / file):
                    fixed_count += 1
    
    print(f"Finished! Checked {checked_count} files, fixed {fixed_count} files.")

if __name__ == "__main__":
    main()
