"""Read-only summary of reported, estimated, held and unknown API costs."""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .api_client import CostTracker

class CostDashboard:
    def __init__(self, log_file):
        self.log_file = Path(log_file)

    def load_entries(self, days=None):
        entries = CostTracker(self.log_file).effective_entries()
        if days:
            cutoff = (datetime.now(timezone.utc)-timedelta(days=days)).date().isoformat()
            entries = [e for e in entries if e.get('timestamp',e.get('date',''))[:10] >= cutoff]
        return entries

    def agent_summary(self, days=None):
        summary = defaultdict(lambda: {'calls':0,'cost_usd':0.0,'reported_usd':0.0,
            'estimated_usd':0.0,'reserved_usd':0.0,'unknown_calls':0,'legacy_calls':0,'model':'?'})
        for entry in self.load_entries(days):
            row = summary[entry.get('agent_id','unknown')]
            row['calls'] += 1
            row['model'] = entry.get('model','?')
            status = entry.get('cost_status','legacy_estimated')
            amount = entry.get('cost_usd')
            if status == 'provider_reported' and amount is not None:
                row['reported_usd'] += amount
                row['cost_usd'] += amount
            elif status == 'legacy_estimated':
                row['legacy_calls'] += 1
                if amount is not None:
                    row['estimated_usd'] += amount
                else:
                    row['unknown_calls'] += 1
            else:
                estimate = entry.get('estimated_cost_usd')
                if estimate is not None:
                    row['estimated_usd'] += estimate
                row['unknown_calls'] += 1
            if entry.get('state') in {'reserved','unresolved'}:
                row['reserved_usd'] += entry.get('reserved_usd',0)
        return dict(summary)

    def report(self, days=None, agent_filter=None):
        summary = self.agent_summary(days)
        if agent_filter:
            summary = {k:v for k,v in summary.items() if k==agent_filter}
        return json.dumps({'accounting':'provider_reported is actual; estimates and reservations are separate',
                           'agents':summary},indent=2,ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log-file',type=Path,default=Path(__file__).parent/'cost_log.jsonl')
    parser.add_argument('--days',type=int)
    parser.add_argument('--agent')
    args = parser.parse_args()
    print(CostDashboard(args.log_file).report(args.days,args.agent))

if __name__ == '__main__':
    main()
