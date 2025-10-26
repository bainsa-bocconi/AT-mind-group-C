from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AT Mind – Group C")

class AssistRequest(BaseModel):
    query: str
    quote_id: str | None = None

class AssistResponse(BaseModel):
    json_payload: dict
    markdown: str

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/assist", response_model=AssistResponse)
def assist(req: AssistRequest):
    payload = {
        "quote_id": req.quote_id or "N/A",
        "suggested_actions": ["Follow up with financing details"],
        "risks": ["Customer uncertain about add-ons"],
        "followup_message": "Hi! Following up on your quote..."
    }
    markdown = f"### Summary for `{payload['quote_id']}`\n- Suggested action: follow up\n- Risk: uncertainty"
    return AssistResponse(json_payload=payload, markdown=markdown)


