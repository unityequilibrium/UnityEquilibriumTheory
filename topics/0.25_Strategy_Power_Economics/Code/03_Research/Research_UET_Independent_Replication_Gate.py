from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/"Result/artifacts/0_25_independent_replication_gate.json"
def main():
 out={"schema_version":"1.0","topic":"0.25_Strategy_Power_Economics","status":"BLOCKED","required_protocol":{"replicator":"independent analyst or agent","inputs":"same frozen source vintage and hashes","code_path":"independent implementation, not a rerun of the primary script","agreement":"primary effect direction agrees, confidence intervals overlap, preregistered tolerance is met","failure_reporting":"all replication failures must be reported"},"blockers":["No independent analyst/agent rerun artifact is archived.","No second implementation using the frozen archive exists.","No replication comparison table with coefficient/interval tolerance exists."],"claim_boundary":"Internal reruns are not external replication. Evidence Grade A remains blocked until an independent replication succeeds or transparently fails."};ART.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print('Independent replication gate: BLOCKED')
if __name__=="__main__":main()
