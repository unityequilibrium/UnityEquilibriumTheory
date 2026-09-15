"""Inspect a published UED archive without unpickling or executing notebooks."""

import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw'


def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def archive_inventory(path):
    # Central-directory inspection only. No extraction, pickle loading or CRC inflation.
    with zipfile.ZipFile(path) as archive:
        return [dict(name=i.filename, compressed_bytes=i.compress_size,
                     uncompressed_bytes=i.file_size, crc32=f'{i.CRC:08x}',
                     is_directory=i.is_dir()) for i in archive.infolist()]


def main():
    metadata_path = RAW/'ued_14760926_metadata.json'
    notebook_path = RAW/'ued_data_paper_7f7036b.ipynb'
    archive_path = RAW/'ued_14760926_processed.zip'
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    entry = next(f for f in metadata['files'] if f['key'] == 'UED_PROCESSED.zip')
    if metadata['metadata']['license']['id'] != 'cc-by-4.0':
        raise ValueError('license must be reviewed')
    if archive_path.stat().st_size != entry['size']:
        raise ValueError('download incomplete or source size differs')
    expected_md5 = entry['checksum'].removeprefix('md5:')
    if digest(archive_path, 'md5') != expected_md5:
        raise ValueError('published checksum mismatch')
    notebook = json.loads(notebook_path.read_text(encoding='utf-8'))
    cells = []
    for index, cell in enumerate(notebook['cells']):
        source = ''.join(cell.get('source', []))
        if cell['cell_type'] == 'code' and any(token in source for token in ('read_pickle', 'Time delay (ps)', 'imgON')):
            cells.append(dict(index=index, sha256=hashlib.sha256(source.encode()).hexdigest(),
                              reads_pickle='read_pickle' in source,
                              has_ps_label='Time delay (ps)' in source,
                              has_pump_pair='imgON' in source and 'imgOFF' in source))
    inventory = archive_inventory(archive_path)
    result = dict(
        major_result_id='T13_OPEN_UED_SOURCE_ACQUISITION', topic='0.13', closure_level='PARTIAL',
        verification_status='ARCHIVE_HASH_VERIFIED_NUMERIC_MAPPING_OPEN',
        what_is_closed=['Permitted processed experimental archive downloaded and checksum verified',
                        'Author processing notebook pinned and inspected as JSON only'],
        equation_or_mapping='Processed pump-on/off diffraction images versus delay; not phonon occupations yet',
        units={'delay': 'ps according to notebook axis label', 'momentum': 'inverse angstrom according to notebook axis label',
               'image_counts': 'UNVERIFIED_PAYLOAD_UNITS'},
        derivation_class='source_acquisition_not_physics_derivation', data_role='EXTERNAL_COMPARISON_CANDIDATE',
        observable='time- and momentum-dependent electron scattering',
        source={'doi': '10.5281/zenodo.14760926', 'license': 'CC-BY-4.0',
                'metadata_publication_date': metadata['metadata']['publication_date'],
                'archive_url': entry['links']['self'], 'publisher_md5': expected_md5},
        notebook={'repository': 'https://github.com/remiclaude/UED_processing',
                  'commit': '7f7036bfda28f9330f19b40e57f4edf464b67d64',
                  'path': 'UED_data_paper.ipynb', 'executed': False,
                  'code_redistribution_license': 'NOT_ESTABLISHED_LOCAL_ONLY', 'inspected_cells': cells},
        archive_members=inventory, pickle_deserialized=False, numeric_rows_extracted=False,
        payload_integrity='Published archive MD5 verified; member CRC metadata listed, not inflated/verified.',
        open_blockers=['safe numeric decoding', 'payload units/uncertainty/row identity',
                       'detector-to-mode inversion and unobserved modes', 'same-state pump/material map',
                       'independent Phi source coefficient'],
        dependency_unlocked=['safe payload inspection only'], full_core_unlock=False,
        claim_promotion=False, alpha_Phi_K=None,
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p)
                         for p in (metadata_path, notebook_path, archive_path, Path(__file__))},
        claim_boundary='Neither a mode lifetime nor TTG validation, physical occupation curve or Phi calibration.',
    )
    out = ROOT/'docs/core/07_artifacts/topic13/t13_ued_source_acquisition_audit.json'
    out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(dict(status=result['verification_status'], members=inventory, inspected_cells=cells), indent=2))


if __name__ == '__main__':
    main()
