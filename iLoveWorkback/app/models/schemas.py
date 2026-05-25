from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    content: str
    mode: str
    additional_context: dict | None = None


class AnalyzeResponse(BaseModel):
    success: bool = True
    result: str = ""
    mode: str = ""
    model_used: str = ""
    error: str | None = None
