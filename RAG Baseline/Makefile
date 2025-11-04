.PHONY: setup ingest serve eval policy pricing product tone objections contract


setup:
python -m pip install -U pip
pip install -e .


ingest:
python -m at_mind.ingest.index --src data/devseed


serve:
uvicorn at_mind.api:app --reload


policy:
echo '{"question":"Procedure test drive"}' | python -m at_mind.cli policy_qa


pricing:
echo '{"query":"Rata Panda 2023 36 mesi"}' | python -m at_mind.cli pricing_lookup


product:
echo '{"question":"Potenza motore Panda 2023"}' | python -m at_mind.cli product_qa


tone:
echo '{"brief":"Riscrivi: Gentile cliente, la sua rata è..."}' | python -m at_mind.cli tone_writer


objections:
echo '{"objection":"Il prezzo è troppo alto"}' | python -m at_mind.cli objections


contract:
cat examples/quote.json | python -m at_mind.cli contract
