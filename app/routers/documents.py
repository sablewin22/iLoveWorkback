import io

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.document_processor import extract_text
from app.services.llm import analyze

router = APIRouter(prefix="/api", tags=["documents"])

import re


MODE_ALIASES = {
    "curriculo": "resume_analysis",
    "currículo": "resume_analysis",
    "resume_analysis": "resume_analysis",
    "contrato": "contract_analysis",
    "contract_analysis": "contract_analysis",
    "criar_contrato": "contract_creation",
    "contract_creation": "contract_creation",
    "comparar_contratos": "contract_comparison",
    "contract_comparison": "contract_comparison",
    "diretrizes": "guideline_interpretation",
    "guideline_interpretation": "guideline_interpretation",
    "gerar_email": "email_generation",
    "email_generation": "email_generation",
    "rescisao": "severance_simulator",
    "severance_simulator": "severance_simulator",
    "tradutor": "legal_translator",
    "legal_translator": "legal_translator",
    "ata": "meeting_minutes",
    "meeting_minutes": "meeting_minutes",
    "dados empresariais": "business_data_analysis",
    "business_data_analysis": "business_data_analysis",
    "politica interna": "internal_policy_creator",
    "internal_policy_creator": "internal_policy_creator",
}


def _normalize_mode(mode: str) -> str:
    key = mode.strip().lower()
    return MODE_ALIASES.get(key, mode)


@router.post("/analyze")
async def analyze_document(body: AnalyzeRequest):
    if not body.content.strip():
        return AnalyzeResponse(success=False, error="Conteúdo vazio.")

    mode = _normalize_mode(body.mode)
    context_extra = ""
    if body.additional_context:
        context_extra = "\n\nContexto adicional:\n" + str(body.additional_context)

    result, model_used = analyze(mode, body.content + context_extra)

    if model_used == "none":
        return AnalyzeResponse(
            success=False,
            error="Erro ao consultar a IA. Verifique sua chave de API.",
        )

    return AnalyzeResponse(result=result, mode=mode, model_used=model_used)


@router.post("/analyze/upload")
async def analyze_upload(
    mode: str = Form(...),
    file: UploadFile = File(...),
):
    file_bytes = await file.read()
    content = extract_text(file_bytes, file.filename or "documento.txt")

    if not content.strip():
        return AnalyzeResponse(success=False, error="Conteúdo vazio após extração.")

    mode = _normalize_mode(mode)
    result, model_used = analyze(mode, content)

    if model_used == "none":
        return AnalyzeResponse(
            success=False,
            error="Erro ao consultar a IA. Verifique sua chave de API.",
        )

    return AnalyzeResponse(result=result, mode=mode, model_used=model_used)


@router.post("/export/pdf")
async def export_pdf(body: AnalyzeResponse):
    if not body.result:
        raise HTTPException(400, "Nenhum resultado para exportar.")

    buf = io.BytesIO()
    doc = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 2 * cm
    y = height - margin
    doc.setFont("Helvetica-Bold", 16)
    doc.drawString(margin, y, f"iLoveWork - {body.mode}")
    y -= 1.5 * cm
    doc.setFont("Helvetica", 10)

    for line in body.result.split("\n"):
        if y < margin:
            doc.showPage()
            doc.setFont("Helvetica", 10)
            y = height - margin
        max_w = width - 2 * margin
        display = line.strip()
        while display:
            for cut in range(len(display), 0, -1):
                if doc.stringWidth(display[:cut], "Helvetica", 10) <= max_w:
                    break
            doc.drawString(margin, y, display[:cut].strip())
            y -= 0.5 * cm
            display = display[cut:].strip()
            if y < margin and display:
                doc.showPage()
                doc.setFont("Helvetica", 10)
                y = height - margin

    doc.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resultado.pdf"},
    )


SECTION_HEADERS = {
    "resume_analysis": "Versão reescrita otimizada",
    "contract_creation": "Contrato completo formatado",
}


def _extract_section(text: str, section_keyword: str) -> str | None:
    keyword_loose = section_keyword.replace("ã", "[aã]").replace("é", "[eé]").replace("ê", "[eê]").replace("ç", "[cç]").replace("á", "[aá]").replace("í", "[ií]").replace("ó", "[oó]").replace("õ", "[oõ]").replace("ú", "[uú]")
    pattern = rf"##\s*\*+[^*]*{keyword_loose}[^*]*\*+.*?(?=\n##\s|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group()
        content = re.sub(r"^##\s*\*+[^*]+\*+", "", content).strip()
        content = re.sub(r"^---+", "", content).strip()
        return content
    return None


def _make_pdf(text: str, title: str = "iLoveWork") -> bytes:
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 2 * cm
    usable = width - 2 * margin
    y = height - margin
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin, y, title)
    y -= 1 * cm
    for line in text.split("\n"):
        raw = line.strip()
        if not raw:
            y -= 0.2 * cm
            continue
        if raw.startswith("---") or raw.startswith("///"):
            y -= 0.2 * cm
            pdf.setStrokeColor(0.85, 0.85, 0.85)
            pdf.setLineWidth(0.5)
            pdf.line(margin, y, width - margin, y)
            y -= 0.4 * cm
            pdf.setStrokeColor(0, 0, 0)
            continue
        is_heading = raw.startswith("##")
        is_bullet = raw.startswith("- ") or raw.startswith("* ")
        if is_heading:
            clean = re.sub(r"^#+\s*\**", "", raw).rstrip("*").strip()
            y -= 0.1 * cm
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(margin, y, clean[:90])
            y -= 0.55 * cm
            pdf.setFont("Helvetica", 10)
            continue
        indent = 0.4 * cm if is_bullet else 0
        text_x = margin + indent
        max_w = usable - indent
        display = raw.lstrip("- ").lstrip("* ")
        display = display.replace("**", "")
        pdf.setFont("Helvetica", 10)
        while display:
            for cut in range(len(display), 0, -1):
                if pdf.stringWidth(display[:cut], "Helvetica", 10) <= max_w:
                    break
            pdf.drawString(text_x, y, display[:cut].strip())
            y -= 0.4 * cm
            display = display[cut:].strip()
            if y < margin:
                pdf.showPage()
                y = height - margin
                text_x = margin + indent
    pdf.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


@router.post("/export/section-auto")
async def export_section_auto(body: AnalyzeResponse, format: str = "pdf"):
    if not body.result:
        raise HTTPException(400, "Nenhum resultado para exportar.")

    for keyword in SECTION_HEADERS.values():
        section = _extract_section(body.result, keyword)
        if section:
            if format == "pdf":
                pdf_bytes = _make_pdf(section, title=keyword)
                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename={keyword.replace(' ', '_')}.pdf"
                    },
                )
            return Response(
                content=section,
                media_type="text/plain; charset=utf-8",
                headers={
                    "Content-Disposition": f"attachment; filename={keyword.replace(' ', '_')}.txt"
                },
            )
    raise HTTPException(404, "Nenhuma seção encontrda para exportar.")


@router.post("/export/section")
async def export_section(body: AnalyzeResponse):
    if not body.result:
        raise HTTPException(400, "Nenhum resultado para exportar.")

    keyword = SECTION_HEADERS.get(body.mode, "")
    if not keyword:
        raise HTTPException(400, "Exportação de seção não disponível para este modo.")

    section = _extract_section(body.result, keyword)
    if not section:
        raise HTTPException(404, "Seção não encontrada no resultado.")

    return Response(
        content=section,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={body.mode}_{keyword.replace(' ', '_')}.txt"
        },
    )


MODOS = {
    "resume_analysis": "Análise de Currículo",
    "contract_analysis": "Análise de Contrato",
    "contract_creation": "Criação de Contrato",
    "contract_comparison": "Comparação de Contratos",
    "guideline_interpretation": "Interpretação de Diretrizes",
    "email_generation": "Geração de E-mail Profissional",
    "severance_simulator": "Simulador de Rescisão Trabalhista",
    "legal_translator": "Tradutor Jurídico",
    "meeting_minutes": "Gerador de Ata de Reunião",
    "business_data_analysis": "Analisador de Dados Empresariais",
    "internal_policy_creator": "Criador de Política Interna",
}


@router.get("/modes")
async def list_modes():
    return MODOS
