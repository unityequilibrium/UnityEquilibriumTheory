
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
import asyncio
import os
import sys
from pathlib import Path

# Ensure docs is in path
sys.path.append(str(_UET_REPO_ROOT))

from docs.knowledge_base.vector_store import VectorStore, VectorDocument


async def test_crud():
    print("--- Starting MCP CRUD Verification ---")

    try:
        store = VectorStore(db_path="./test_vectors", backend="mcp")
    except Exception as e:
        print(f"Failed to initialize VectorStore: {e}")
        return

    import uuid

    test_doc_id = str(uuid.uuid4())
    test_path = "test_doc_crud.md"
    test_content = "This is a test document for CRUD operations."
    test_metadata = {"topic_id": "test_topic", "source": "verification_script"}

    # Create VectorDocument
    doc = VectorDocument(
        doc_id=test_doc_id,
        file_path=test_path,
        text=test_content,
        semantic_vec=[0.1] * 1024,  # Dummy vector
        uet_vec=[0.1] * 20,  # Dummy vector
    )
    # Attach metadata dict for MCP backend to pick up
    doc.metadata = test_metadata

    print(f"\n1. Testing Ingestion (ID: {test_doc_id})...")
    try:
        store.add(doc)
        print(f"✅ Ingestion command sent.")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return

    print("\n2. Testing Get Document...")
    try:
        # Give a small delay for async processing if needed, though MCP is sync-over-pipe usually
        retrieved_doc = store.get(test_doc_id)
        if retrieved_doc:
            print(f"✅ Retrieved document: {retrieved_doc.file_path}")
            # Check metadata if possible.
            # Note: VectorStore.get() returns a VectorDocument.
            # We need to see if metadata came back.
            meta = getattr(retrieved_doc, "metadata", {})
            print(f"   Metadata: {meta}")

            # The metadata coming back might be in the 'metadata' attribute or fields
            if meta.get("topic_id") == "test_topic":
                print("✅ Metadata verified.")
            else:
                print(f"⚠️ Metadata verify warning: Got {meta}")

        else:
            print("❌ Document not found!")
    except Exception as e:
        print(f"❌ Get Document failed: {e}")

    print("\n3. Testing Count...")
    try:
        count = store.count()
        print(f"✅ Document count: {count}")
        assert count >= 1
    except Exception as e:
        print(f"❌ Count failed: {e}")

    print("\n4. Testing List Topics...")
    try:
        topics = store.list_topics()
        print(f"✅ Topics: {topics}")
        # Note: 'topic_id' in metadata might not automatically become a 'topic' in the list
        # unless logic extracts it. But let's check.
    except Exception as e:
        print(f"❌ List Topics failed: {e}")

    print("\n5. Testing Deletion...")
    try:
        success = store.delete(test_doc_id)
        if success:
            print("✅ Deleted document.")
        else:
            print("❌ Deletion reported failure.")

        # Verify deletion
        doc_check = store.get(test_doc_id)
        if doc_check is None:
            print("✅ Verification: Document is gone.")
        else:
            print("❌ Verification: Document still exists!")

    except Exception as e:
        print(f"❌ Deletion failed: {e}")

    print("\n--- Verification Complete ---")


if __name__ == "__main__":
    asyncio.run(test_crud())
