import sys, json
from at_mind.skills.contract.run import run as run_contract
from at_mind.skills.policy_qa.run import run as run_policy
from at_mind.skills.pricing_lookup.run import run as run_pricing
from at_mind.skills.product_qa.run import run as run_product
from at_mind.skills.tone_writer.run import run as run_tone
from at_mind.skills.objections.run import run as run_obj
from at_mind.skills.cx_insights.run import run as run_cx


USAGE = "Usage: python -m at_mind.cli [contract|policy_qa|pricing_lookup|product_qa|tone_writer|objections|cx_insights]"


def main():
if len(sys.argv) < 2:
print(USAGE)
sys.exit(1)
skill = sys.argv[1]
payload = json.loads(sys.stdin.read() or "{}")
if skill == "contract":
out = run_contract(payload)
elif skill == "policy_qa":
out = run_policy(payload.get("question", ""))
elif skill == "pricing_lookup":
out = run_pricing(payload.get("query", ""))
elif skill == "product_qa":
out = run_product(payload.get("question", ""))
elif skill == "tone_writer":
out = run_tone(payload.get("brief", ""))
elif skill == "objections":
out = run_obj(payload.get("objection", ""))
elif skill == "cx_insights":
out = run_cx()
else:
print(USAGE)
sys.exit(1)
print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
main()
