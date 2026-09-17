"""Verify raw-sorted source package, never unpickle its contents."""
import json
from pathlib import Path
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest, archive_inventory

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw'


def verify_file(path, entry):
    if path.stat().st_size != entry['size'] or digest(path, 'md5') != entry['checksum'].removeprefix('md5:'):
        raise ValueError('source byte count or checksum mismatch')
    return digest(path)


def main():
    metadata_path = RAW/'ued_14760926_metadata.json'
    metadata = json.loads(metadata_path.read_text())
    if metadata['metadata']['license']['id'] != 'cc-by-4.0':
        raise ValueError('license needs review')
    paths = {'UED_RAW_sorted.zip': RAW/'ued_14760926_raw_sorted.zip', 'README.txt': RAW/'ued_14760926_readme.txt'}
    hashes = {}
    for key, path in paths.items():
        entry = next(f for f in metadata['files'] if f['key'] == key)
        hashes[str(path.relative_to(ROOT)).replace('\\', '/')] = verify_file(path, entry)
    inventory = archive_inventory(paths['UED_RAW_sorted.zip'])
    for path in (metadata_path, Path(__file__), ROOT/'docs/scripts/audit/audit_topic13_ued_source_acquisition.py',
                 ROOT/'docs/core/test/test_topic13_ued_raw_archive.py'):
        hashes[str(path.relative_to(ROOT)).replace('\\', '/')] = digest(path)
    result = dict(major_result_id='T13_RAW_SORTED_SOURCE_ACQUIRED', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Published raw-sorted archive and README acquired with size/MD5/SHA256 checks'],
        equation_or_mapping='Raw-sorted image archive before published rotation/averaging pipeline; payload meaning still unverified',
        units={'payload':'UNVERIFIED'}, derivation_class='SOURCE_ACQUISITION', observable='candidate pre-processing detector records',
        data_role='EXTERNAL_SOURCE_NOT_CALIBRATION', verification_status='ARCHIVE_VERIFIED_REPEAT_STRUCTURE_OPEN',
        source={'doi':'10.5281/zenodo.14760926', 'license':'CC-BY-4.0',
                'url':'https://zenodo.org/api/records/14760926/files/UED_RAW_sorted.zip/content'},
        archive_members=inventory, evidence_hashes=hashes, full_core_unlock=False, claim_promotion=False,
        numeric_payload_decoded=False, member_crc_verified=False,
        open_blockers=['repeat/exposure structure', 'count units', 'safe numeric decoding', 'processed covariance propagation', 'Phi coupling'],
        dependency_unlocked=['safe pre-processing payload inspection only'],
        claim_boundary='Raw-sorted label does not prove shot-level or independent repeat availability. No pickle execution, fitted covariance, holdout or physical calibration.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_archive_audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(inventory, indent=2))


if __name__ == '__main__':
    main()
