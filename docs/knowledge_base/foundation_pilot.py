"""Reproducible local comparison; optional text-only OpenRouter pairs capped at $2.

Run once with --live after inspecting the local report. Private run data stays in tmp/.
The legacy module is the pre-edit copy saved before this pilot, never the live index.
"""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
from decimal import Decimal

from . import personal_kb as kb
from .api_client import OpenRouterClient, CostTracker, BudgetExceeded, UnresolvedCost

ROOT = kb.REPO_ROOT
RUN = ROOT / 'tmp/research-foundation-pilot'
EXPERIMENT = 'research-foundation-pilot-v1'
TASKS = [
    ('claim', 'What limits apply when writing a research claim?'),
    ('evidence', 'What evidence is required before changing a claim?'),
    ('provenance', 'What source identity must be retained?'),
    ('units', 'How must units and physical correspondence be checked?'),
    ('ontology', 'What must be defined before promoting a core equation?'),
    ('blocker', 'What controls the next hardening wave?'),
    ('baseline', 'What should a baseline comparison establish?'),
    ('verification', 'How should verification and validation be distinguished?'),
]
SOURCES = [
    'docs/topics/For Work/04_Claim_and_Evidence_Rubric.md',
    'docs/topics/For Work/12_Data_Standard.md',
    'docs/topics/For Work/18_Research_Hardening_Workflow.md',
    'docs/topics/For Work/EQUATION_RESEARCH_AND_PHYSICAL_CORRESPONDENCE_STANDARD.md',
]
SYSTEM = ('Answer only from supplied evidence. Preserve scope and uncertainty. '
          'Do not promote fit to prediction or internal rerun to external validation. '
          'Cite the supplied source path and available line locator. Say unknown if evidence is missing.')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_legacy(path):
    spec = importlib.util.spec_from_file_location('pilot_frozen_legacy', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def prepare():
    RUN.mkdir(parents=True, exist_ok=True)
    old = load_legacy(RUN / 'legacy_personal_kb.py')
    records = []
    hashes = {path:digest(ROOT/path) for path in SOURCES}
    for label, module in [('before',old),('after',kb)]:
        db = RUN / (label+'-corpus.sqlite3')
        # Reject changed sources rather than comparing different corpora on a rerun.
        manifest = RUN / 'corpus-snapshot.json'
        if manifest.exists() and json.loads(manifest.read_text()) != hashes:
            raise ValueError('Corpus changed since snapshot; use a new pilot identity')
        if not db.exists():
            with redirect_stdout(io.StringIO()):
                module.cmd_ingest(argparse.Namespace(db=db,paths=SOURCES,all=False,dry_run=False))
        for index,(query,question) in enumerate(TASKS):
            out = io.StringIO()
            start = time.perf_counter()
            with redirect_stdout(out):
                module.cmd_search(argparse.Namespace(db=db,query=query,limit=4,snippet_chars=320,
                    packet=label=='after',scope=SOURCES,lane='unknown',blocker='unknown'))
            context = out.getvalue()
            rows = [json.loads(line) for line in context.splitlines() if line]
            evidence = rows[0]['evidence'] if label=='after' else rows
            records.append({'task':index,'query':query,'question':question,'variant':label,
                'retrieval_seconds':time.perf_counter()-start,'context_utf8_bytes':len(context.encode()),
                'sources':len(evidence),'source_paths_exist':all((ROOT/r['source_path']).is_file() for r in evidence),
                'context':context})
    (RUN/'corpus-snapshot.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    return records

def messages(record):
    return [{'role':'system','content':SYSTEM},
        {'role':'user','content':record['question']+'\nEvidence:\n'+record['context']}]

def run_live(records, config):
    if not config.is_file():
        return {'status':'blocked','reason':'Actual config with agents.local_data is missing',
                'calls':0,'reported_cost_usd':0}
    log = RUN / 'api-costs.jsonl'
    tracker = CostTracker(log)
    if tracker.entries():
        return {'status':'blocked','reason':'Existing experiment ledger: do not rerun or duplicate calls',
                'calls':len(tracker.effective_entries()),'accounted_usd':str(tracker.experiment_total(EXPERIMENT))}
    with OpenRouterClient.from_config(config) as client:
        client.cost_tracker = tracker
        client.experiment_id, client.experiment_limit = EXPERIMENT, 2.0
        if 'local_data' not in client.agents:
            return {'status':'blocked','reason':'agents.local_data missing','calls':0}
        preflight = client.preflight('local_data')
        model_info = client.price_snapshot[preflight['model']].get('record',{})
        if 'temperature' not in model_info.get('supported_parameters',[]):
            return {'status':'blocked','reason':'Temperature 0 support could not be confirmed','calls':0}
        completed, outputs = [], []
        status, reason = 'complete',''
        # Hold a runner lock across the full experiment, distinct from per-call ledger lock.
        with CostTracker(RUN/'runner-guard.jsonl').exclusive():
            for index in range(8):
                pair = sorted((r for r in records if r['task']==index),key=lambda r:r['variant'],reverse=True)
                amounts = [client.reservation_for('local_data',{'model':preflight['model'],
                    'messages':messages(r),'max_tokens':2048,'temperature':0,
                    'provider':{'allow_fallbacks':False}}) for r in pair]
                if tracker.experiment_total(EXPERIMENT)+sum(amounts) > Decimal('2'):
                    status,reason='budget_stopped','Next complete pair would exceed $2'
                    break
                try:
                    for record in pair:
                        started = time.perf_counter()
                        text = client.chat('local_data',messages(record),max_tokens=2048,temperature=0)
                        entry = client.last_cost_entry
                        outputs.append({'task':index,'variant':record['variant'],'response':text,
                            'latency_seconds':time.perf_counter()-started,'usage':entry.usage,
                            'reported_cost_usd':entry.cost_usd,'request_id':entry.request_id})
                        (RUN/'api-responses.json').write_text(json.dumps(outputs,indent=2),encoding='utf-8')
                    completed.append(index)
                except Exception as exc:
                    status,reason='blocked',type(exc).__name__
                    break
        return {'status':status,'reason':reason,'model':preflight['model'],'price_snapshot':preflight['pricing'],
            'completed_pairs':len(completed),'calls':len(tracker.effective_entries()),
            'reported_cost_usd':sum(e.get('cost_usd') or 0 for e in tracker.effective_entries()),
            'quality_status':'Pending independent source/rubric review; not a quality certification'}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--config',type=Path,default=ROOT/'docs/knowledge_base/config.toml')
    args = parser.parse_args(argv)
    records = prepare()
    summary = {'experiment_id':EXPERIMENT,'corpus_hashes':json.loads((RUN/'corpus-snapshot.json').read_text()),
        'local_comparison':[{k:v for k,v in r.items() if k!='context'} for r in records],
        'api':{'status':'not_requested','calls':0},'token_measurement':'Only provider usage is actual tokens; UTF-8 bytes are context size',
        'quality_status':'Acceptance fixtures only; independent paired answer review not completed'}
    if args.live:
        try:
            summary['api'] = run_live(records,args.config)
        except Exception as exc:
            summary['api'] = {'status':'blocked','reason':type(exc).__name__,'calls':len(CostTracker(RUN/'api-costs.jsonl').effective_entries())}
    (RUN/'comparison.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({'report':str(RUN/'comparison.json'),'api':summary['api']},ensure_ascii=False))
    return 0 if summary['api']['status'] not in {'blocked'} else 2

if __name__ == '__main__':
    raise SystemExit(main())
