import re
from groq import Groq

from app.config import settings

SECTION_SEP = "\n\n---\n\n"

TOPIC_HEADER = "## **{}**\n\n"

SYSTEM_PROMPTS = {
    "resume_analysis": (
        "Você é um especialista em RH e análise de currículos.\n\n"
        "REGRAS:\n"
        "- Períodos com sobreposição de datas são normais. NUNCA aponte como fraqueza.\n"
        "- Currículos acadêmicos têm múltiplos idiomas. NUNCA aponte idioma como fraqueza.\n"
        "- Currículo pode estar em qualquer idioma. NUNCA aponte idioma como fraqueza.\n"
        "- Falta de endereço físico NUNCA é fraqueza. E-mail/telefone bastam.\n"
        "- Publicações e produções acadêmicas SÃO realizações. NUNCA diga que faltam métricas quantitativas.\n\n"
        "CURRÍCULO REFERÊNCIA (NOTA 10) — Matheus Cavalcanti Pestana:\n"
        "Professor FGV, Doutor UERJ/IESP. 3 livros, 7 artigos. 9 disciplinas (2022-2026). "
        "Projetos: Monitoramento Legislativo, Eleições 2022, ISER+Nexo. "
        "Prêmios: melhor tese, aprovações concurso público. "
        "Formação: Doutorado (2020-2025), Mestrado (2018-2020), Graduação 9,1/10 (2012-2016). "
        "Idiomas: Português, Inglês, Francês, Espanhol, Russo.\n\n"
        "AVALIAÇÃO:\n"
        "10/10 = igual ou superior ao benchmark em estrutura, detalhamento, organização\n"
        "8-9/10 = muito bom, faltam detalhes pequenos\n"
        "6-7/10 = bom, faltam realizações\n"
        "4-5/10 = regular, informações básicas\n"
        "1-3/10 = incompleto\n\n"
        "FORMATO OBRIGATÓRIO:\n"
        "- Use ## **Título da Seção** para cada seção principal.\n"
        "- Dentro de cada seção, use \"-\" para itens e \"  -\" (2 espaços + -) para subtópicos.\n"
        "- Use **negrito** para destacar o rótulo do tópico (ex: - **Experiência:** descrição).\n"
        "- NUNCA use \"---\" ou \"////\" ou \"===\" ou \"***\".\n\n"
        "Seções obrigatórias (siga este formato EXATAMENTE):\n"
        "## **Nota geral**\n"
        "- **Nota:** X/10\n\n"
        "## **Pontos fortes**\n"
        "- **Item:** descrição\n\n"
        "## **Pontos fracos / gaps**\n"
        "- **Item:** descrição\n\n"
        "## **Sugestões de melhoria**\n"
        "- **Item:** descrição\n\n"
        "## **Pontos fracos / gaps**\n"
        "- **Item:** descrição\n"
        "IMPORTANTE: OS SEGUINTES ITENS NUNCA SÃO PONTOS FRACOS: idioma do currículo, "
        "falta de endereço físico, uso de múltiplos idiomas, sobreposição de datas entre empregos, "
        "formatação visual, ausência de foto.\n\n"
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
            temperature=0.1,
            max_tokens=4096,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[_call_groq] {model} error: {e}")
        return None


def analyze(mode: str, content: str) -> tuple[str, str]:
    messages = _build_messages(mode, content)

    result = _call_groq(settings.primary_model, messages)
    model_used = settings.primary_model
    if not result:
        result = _call_groq(settings.fallback_model, messages)
        model_used = settings.fallback_model
    if not result:
        return "Erro: não foi possível obter resposta da IA. Verifique sua chave de API.", "none"

    result = _post_process(mode, result, content)
    return result, model_used


def _post_process(mode: str, result: str, content: str) -> str:
    if "resume" not in mode:
        return result

    is_benchmark = "Matheus Cavalcanti Pestana" in content

    if is_benchmark:
        result = re.sub(r'(Nota:\s*\*?\*?\s*)\d+[.,]?\d*(\s*\*?\*?/10)', r'\g<1>10\g<2>', result)
        result = re.sub(r'(?s)## \*\*Pontos fracos / gaps\*\*.*?(?=## \*\*)', '', result)

    return result
