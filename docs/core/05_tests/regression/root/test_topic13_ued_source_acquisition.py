import hashlib
import zipfile

from docs.scripts.audit.audit_topic13_ued_source_acquisition import archive_inventory, digest


def test_lists_opaque_payload_without_decoding(tmp_path):
    path = tmp_path/'sample.zip'
    opaque = b'not even a valid pickle'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('PROCESSED/', b'')
        archive.writestr('PROCESSED/PROC_800nm', opaque)
    rows = archive_inventory(path)
    assert rows[0]['is_directory']
    assert rows[1]['uncompressed_bytes'] == len(opaque)
    assert not (tmp_path/'PROCESSED').exists()


def test_streaming_hash(tmp_path):
    path = tmp_path/'sample.bin'
    content = b'source check'*200000
    path.write_bytes(content)
    assert digest(path) == hashlib.sha256(content).hexdigest()
    assert digest(path, 'md5') == hashlib.md5(content).hexdigest()
