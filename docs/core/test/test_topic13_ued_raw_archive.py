import hashlib
import pytest
from docs.scripts.audit.audit_topic13_ued_raw_archive import verify_file


def test_source_bytes_and_hash_required(tmp_path):
    path = tmp_path/'raw'
    path.write_bytes(b'opaque payload')
    entry = {'size':14, 'checksum':'md5:'+hashlib.md5(b'opaque payload').hexdigest()}
    assert verify_file(path, entry) == hashlib.sha256(b'opaque payload').hexdigest()
    path.write_bytes(b'changed payload')
    with pytest.raises(ValueError): verify_file(path, entry)
