from at_mind.skills.contract.run import _render_template


def test_render_inserts_fields():
tpl = "Cliente: {{customer.full_name}}"
md = _render_template(tpl, {"customer": {"full_name": "Mario Rossi"}})
assert "Mario Rossi" in md
