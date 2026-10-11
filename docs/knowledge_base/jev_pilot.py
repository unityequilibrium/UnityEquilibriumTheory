"""Bounded, experimental relevance pilot. Credentials are read without echo or storage."""
from __future__ import annotations
import argparse
import getpass
import json
import math
import statistics
from decimal import Decimal
from pathlib import Path
import time
from .api_client import CostTracker, OpenRouterClient
from .foundation_pilot import ROOT, RUN, EXPERIMENT

MODEL = 'typesafe/jev-1.13'
SUBJECTS = ['claim wording','source provenance','equation units','observable mapping',
            'experiment baselines','holdout evaluation','reproducibility','blocker status']

def cases():
    """Controlled authored labels, NOT a domain validation or natural-corpus evaluation."""
    tasks = []
    for subject in SUBJECTS:
        tasks.append({'question':f'What evidence is needed to assess {subject} in a research project?',
            'documents':[
                {'id':'method','text':f'To assess {subject}, record the exact inputs, assumptions, '
                    'comparison baseline and scope of the result. A successful internal rerun is '
                    'not external validation.','expected':'keep','mandatory':True},
                {'id':'contrary','text':f'The current {subject} result has contrary evidence: '
                    'an independent comparison disagrees with the proposed conclusion. This '
                    'limitation must be reviewed before making a stronger research claim.',
                    'expected':'keep','mandatory':False},
                {'id':'unrelated','text':'The cafeteria menu lists coffee, tea and sandwiches. '
                    'The printer purchase order concerns paper trays, toner inventory and '
                    'delivery timing, with no scientific definitions or research evidence.',
                    'expected':'drop','mandatory':False},
                {'id':'ambiguous','text':f'A note mentions {subject} but gives no method, inputs, '
                    'source citation, scope or conclusion. Its relevance cannot be established '
                    'without the original source.','expected':'unknown','mandatory':False}]})
    return tasks

def payload(task):
    state = {'research_question':task['question'],
             'documents':{d['id']:d['text'] for d in task['documents']}}
    questions = {d['id']:{'type':'choice',
        'instructions':f'Assess whether `documents.{d["id"]}` contributes evidence to '
                       '`research_question`. Contrary evidence and limitations are relevant. '
                       'Classify content only; never certify a research claim.',
        'criteria':{'keep':'Directly relevant method, source, assumption, result, limitation or contrary evidence.',
                    'drop':'Clearly unrelated content with no bearing on the research question.',
                    'unknown':'Insufficient content to establish relevance; more source information is needed.'}}
        for d in task['documents']}
    return state, questions

def select(task, answers):
    if set(answers) != {d['id'] for d in task['documents']}:
        raise ValueError('Missing or extra decision IDs')
    retained, raw = [], {}
    for document in task['documents']:
        answer = answers[document['id']]
        probs = answer.get('probabilities',{})
        if answer.get('type') != 'choice' or answer.get('choice') not in {'keep','drop','unknown'}:
            raise ValueError('Invalid decision type or choice')
        if set(probs) != {'keep','drop','unknown'}:
            raise ValueError('Incomplete probabilities')
        values = list(probs.values())+[answer.get('confidence')]
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v)
               or not 0 <= v <= 1 for v in values) or abs(sum(probs.values())-1) > .02:
            raise ValueError('Invalid probability distribution')
        raw[document['id']] = answer['choice']
        # Uncalibrated thresholds are conservative pilot policy only.
        drop = (answer['choice']=='drop' and probs['drop'] >= .9 and answer['confidence'] >= .9)
        if document['mandatory'] or not drop:
            retained.append({'id':document['id'],'text':document['text']})
    return retained,raw

def summarize(tasks):
    before = sum(t['before_utf8_bytes'] for t in tasks)
    after = sum(t['after_utf8_bytes'] for t in tasks)
    return {'decision_accuracy':sum(t['raw_choices'][k]==v for t in tasks for k,v in t['expected'].items()),
        'decisions_total':sum(len(t['expected']) for t in tasks),
        'raw_relevant_kept':sum(t['raw_relevant_kept'] for t in tasks),
        'policy_relevant_kept':sum(t['policy_relevant_kept'] for t in tasks),
        'relevant_total':sum(t['relevant_total'] for t in tasks),
        'before_utf8_bytes':before,'after_utf8_bytes':after,
        'context_byte_reduction_fraction':1-after/before if before else None,
        'actual_jev_input_tokens':sum(t['usage'].get('input_tokens',0) for t in tasks),
        'actual_jev_output_tokens':sum(t['usage'].get('output_tokens',0) for t in tasks),
        'median_latency_seconds':statistics.median(t['latency_seconds'] for t in tasks) if tasks else None}

def run(key):
    RUN.mkdir(parents=True,exist_ok=True)
    tracker = CostTracker(RUN/'api-costs.jsonl')
    if tracker.entries():
        raise ValueError('Experiment ledger already has calls; review before rerun')
    report = {'model':MODEL,'scope':'8 authored relevance fixtures; no main-model answer calls',
        'threshold_status':'Uncalibrated pilot only','tasks':[],
        'downstream_actual_token_savings':None,'main_model_quality':None}
    agents = {'local_data':{'model':MODEL,'daily_budget_usd':0,'key_name':'default'}}
    with OpenRouterClient('https://openrouter.ai/api/v1',{'default':key},agents,tracker) as client:
        client.experiment_id,client.experiment_limit = EXPERIMENT,2
        report['preflight'] = client.preflight('local_data')
        with CostTracker(RUN/'runner-guard.jsonl').exclusive():
            for task in cases():
                state,questions = payload(task)
                started = time.perf_counter()
                try:
                    result = client.decide('local_data',state,questions)
                    retained, raw = select(task,result['answers'])
                    if result.get('provider') != 'TypeSafe':
                        raise ValueError('Unexpected decision provider')
                    full = [{'id':d['id'],'text':d['text']} for d in task['documents']]
                    relevant = [d['id'] for d in task['documents'] if d['expected']=='keep']
                    report['tasks'].append({'question':task['question'],'raw_choices':raw,
                        'expected':{d['id']:d['expected'] for d in task['documents']},
                        'retained_ids':[d['id'] for d in retained],
                        'raw_relevant_kept':sum(raw[i]=='keep' for i in relevant),
                        'policy_relevant_kept':sum(i in {d['id'] for d in retained} for i in relevant),
                        'relevant_total':len(relevant),
                        'before_utf8_bytes':len(json.dumps(full,ensure_ascii=False).encode()),
                        'after_utf8_bytes':len(json.dumps(retained,ensure_ascii=False).encode()),
                        'latency_seconds':time.perf_counter()-started,
                        'usage':client.last_cost_entry.usage})
                    (RUN/'jev-raw.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
                except Exception as exc:
                    report['blocker'] = type(exc).__name__
                    break
    report['calls'] = len(tracker.effective_entries())
    report['reported_cost_usd'] = float(sum((Decimal(str(e.get('cost_usd') or 0))
        for e in tracker.effective_entries()),Decimal(0)))
    report['experiment_accounted_usd'] = str(tracker.experiment_total(EXPERIMENT))
    report['status'] = 'complete' if len(report['tasks'])==8 else 'blocked'
    report['decision'] = 'Experimental only: natural-corpus and downstream answer evaluation remain required'
    report['summary'] = summarize(report['tasks'])
    (RUN/'jev-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

def main():
    key = getpass.getpass('OpenRouter credential (not echoed): ')
    try:
        report = run(key)
        public = {k:v for k,v in report.items() if k!='preflight'}
        destination = ROOT/'docs/knowledge_base/JEV_PILOT_RESULTS.json'
        with destination.open('w',encoding='utf-8',newline='\n') as stream:
            stream.write(json.dumps(public,indent=2)+'\n')
        print(json.dumps({'status':report['status'],'calls':report['calls'],
            'cost_usd':report['reported_cost_usd'],'report':str(destination)}))
    except Exception as exc:
        print(json.dumps({'status':'blocked','reason':type(exc).__name__}))
        raise SystemExit(2)
    finally:
        key = None

if __name__ == '__main__':
    main()
