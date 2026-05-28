from groq import Groq

from app.config import settings

SECTION_SEP = "\n\n---\n\n"

TOPIC_HEADER = "## **{}**\n\n"

SYSTEM_PROMPTS = {
    "resume_analysis": (
        "Você é um especialista em RH e análise de currículos. "
        "Analise o currículo fornecido e produza uma resposta estruturada.\n\n"
        "FORMATO OBRIGATÓRIO:\n"
        "- Use ## **Título da Seção** para cada seção principal.\n"
        "- Dentro de cada seção, use \"-\" para itens e \"  -\" (2 espaços + -) para subtópicos.\n"
        "- Use **negrito** para destacar o rótulo do tópico (ex: - **Experiência:** descrição).\n"
        "- NUNCA use \"---\" ou \"////\" ou \"===\" ou \"***\".\n\n"
        "Seções obrigatórias:\n"
        "## **Nota geral**\n"
        "- **Nota:** X/10\n\n"
        "## **Pontos fortes**\n"
        "- **Item:** descrição\n\n"
        "## **Pontos fracos / gaps**\n"
        "- **Item:** descrição\n\n"
        "## **Sugestões de melhoria**\n"
        "- **Item:** descrição\n\n"
        "## **Versão reescrita otimizada**\n\n"
        "A partir daqui, reescreva o currículo como um modelo profissional EXATAMENTE neste formato:\n\n"
        "### Dados Pessoais\n"
        "- **Nome:** ...\n"
        "- **Telefone:** ...\n"
        "- **E-mail:** ...\n\n"
        "### Resumo Profissional\n"
        "- ...\n\n"
        "### Experiência\n"
        "#### Nome da Empresa | Cargo\n"
        "- Descrição com verbos de ação e realizações\n"
        "- ...\n\n"
        "### Formação\n"
        "#### Curso — Instituição\n"
        "- Período: ...\n\n"
        "### Habilidades\n"
        "- ...\n\n"
        "### Idiomas\n"
        "- ...\n\n"
        "Mantenha TODAS as informações do currículo original sem resumir ou omitir nada na versão reescrita. "
        "Use verbos de ação fortes, destaque realizações quantificáveis, corrija formatação. "
        "A versão reescrita deve ser TÃO OU MAIS detalhada que o original.\n\n"
        "Responda em português brasileiro."
    ),
    "contract_analysis": (
        "Você é um advogado especialista em análise de contratos. "
        "Analise o contrato fornecido e produza uma resposta estruturada.\n\n"
        "FORMATO OBRIGATÓRIO:\n"
        "- Use ## **Título da Seção** para cada seção principal.\n"
        "- Dentro de cada seção, use \"-\" para itens e \"  -\" (2 espaços + -) para subtópicos.\n"
        "- Use **negrito** para destacar o rótulo do tópico (ex: - **Cláusula:** descrição).\n"
        "- NUNCA use \"---\" ou \"////\" ou \"===\" ou \"***\".\n\n"
        "Seções obrigatórias:\n"
        "## **Resumo simplificado do contrato**\n"
        "- **Partes:** ...\n"
        "- **Objeto:** ...\n\n"
        "## **Lista de cláusulas identificadas**\n"
        "- **Cláusula 1 — título:** pontos principais\n"
        "  - **Prazo:** ...\n"
        "  - **Condição:** ...\n\n"
        "## **Classificação de risco por cláusula**\n"
        "- **Cláusula:** nome / **Risco:** descrição / **Justificativa:** motivo\n\n"
        "## **Ambiguidades ou falhas de redação**\n"
        "- **Cláusula:** nome / **Problema:** descrição / **Sugestão:** correção\n\n"
        "## **Prazos e condições relevantes**\n"
        "- **Evento:** nome / **Prazo/Condição:** descrição\n\n"
        "## **Sugestões de alteração**\n"
        "- **Item:** descrição\n\n"
        "Responda em português brasileiro."
    ),
    "contract_creation": (
        "Você é um advogado especialista em elaboração de contratos. "
        "Produza um contrato completo com as informações fornecidas.\n\n"
        "FORMATO OBRIGATÓRIO:\n"
        "- Use ## **Título da Seção** para cada seção principal.\n"
        "- Dentro de cada seção, use \"-\" para itens e \"  -\" para subtópicos.\n"
        "- Use **negrito** para rótulos.\n"
        "- NUNCA use \"---\" ou \"////\" ou \"===\" ou \"***\".\n\n"
        "REGRAS:\n"
        "- Não invente informações que não foram fornecidas.\n"
        "- Se algo não foi informado (endereço, cidade etc.), deixe \"___________________\" para a pessoa preencher depois.\n"
        "- Use a data atual fornecida pelo usuário no campo Data.\n\n"
        "Responda em português brasileiro com linguagem formal."
    ),
    "contract_comparison": (
        "Você é um advogado especialista em comparação de contratos. "
        "Compare os dois contratos fornecidos.\n\n"
        "FORMATO OBRIGATÓRIO:\n"
        "- Use ## **Título da Seção** para cada seção principal.\n"
        "- Dentro de cada seção, use \"-\" para itens e \"  -\" para subtópicos.\n"
        "- Use **negrito** para rótulos.\n"
        "- NUNCA use \"---\" ou \"////\" ou \"===\" ou \"***\".\n\n"
        "Responda em português brasileiro."
    ),
    "guideline_interpretation": (
        "Você é um especialista em compliance e interpretação de normas. "
        "Analise o documento fornecido.\n\n"
        "FORMATO OBRIGATÓRIO:\n"
        "- Use ## **Título da Seção** para cada seção principal.\n"
        "- Dentro de cada seção, use \"-\" para itens e \"  -\" para subtópicos.\n"
        "- Use **negrito** para rótulos.\n"
        "- NUNCA use \"---\" ou \"////\" ou \"===\" ou \"***\".\n\n"
        "Responda em português brasileiro."
    ),
    "email_generation": (
        "Você é um especialista em comunicação profissional. "
        "Produza um e-mail profissional completo com base nas informações fornecidas.\n\n"
        "REGRAS:\n"
        "- Escreva o e-mail por inteiro (Assunto, Saudação, Corpo, Fechamento, Assinatura) em um único bloco.\n"
        "- NÃO divida em seções ou tópicos — apenas o e-mail pronto para usar.\n"
        "- Não invente informações. Se faltar algum detalhe (nome, empresa, etc.), deixe \"___________________\" para o usuário preencher.\n"
        "- NUNCA use \"---\" ou \"////\" ou \"===\" ou \"***\".\n\n"
        "Responda em português brasileiro."
    ),
}


def _build_messages(mode: str, content: str) -> list[dict]:
    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["contract_analysis"])
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]


def _call_groq(model: str, messages: list[dict]) -> str | None:
    if not settings.groq_api_key:
        return None
    try:
        client = Groq(api_key=settings.groq_api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[_call_groq] {model} error: {e}")
        return None


def analyze(mode: str, content: str) -> tuple[str, str]:
    messages = _build_messages(mode, content)

    import sys as _sys
    with open(r"C:\Users\LG\AppData\Local\Temp\opencode\debug_llm.log", "a") as f:
        f.write(f"pid={_sys.executable} primary={settings.primary_model} fallback={settings.fallback_model}\n")
    print(f"[analyze] pid={_sys.executable} primary={settings.primary_model} fallback={settings.fallback_model}", flush=True)

    result = _call_groq(settings.primary_model, messages)
    if result:
        return result, settings.primary_model

    result = _call_groq(settings.fallback_model, messages)
    if result:
        return result, settings.fallback_model

    return "Erro: não foi possível obter resposta da IA. Verifique sua chave de API.", "none"
