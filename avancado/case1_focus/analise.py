"""
Etapas 4 e 5 do agente: ANALISAR (o Claude escreve via `claude -p`) e CONFERIR (todo número do texto existe no JSON).
Dono: Frente C (Theo). Entrada: `resumo` (CONTRATO.md). Saída: HTML da análise (só <h3>, <p>, <ul>, <li>, <strong>).

Regras combinadas com o time:
- Todo número do texto tem que bater com o JSON (2 casas). Só muda a forma: 4.55 -> "4,55", 5.0 -> "5%".
- O Claude não faz conta. As contas extras (juro real, variação da Selic, viés histórico do IPCA) são feitas
  aqui em Python, em `contas_extras()`, entram no resumo que vai ao motor e viram números aceitos pelo conferir().
- Se o conferir() acusar suspeitos, o MESMO `gerar` recebido reescreve até `tentativas` vezes.
"""
import json
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ARQ_CONTAS = AQUI / "saida" / "contas_frente_c.json"
CAMPOS_INTERNOS = {"integridade"}  # insumo do checar(): não vale como número citável (CONTRATO.md)


# ------------------------------------------------------------------ motor Claude
def analisar(resumo: dict, instrucao_extra: str = "") -> str:
    """Motor Claude. Mesma forma de todo motor (reserva.py): gerar(resumo, instrucao_extra="") -> html."""
    claude = shutil.which("claude")
    if not claude:
        raise SystemExit("Claude Code não encontrado. Instale e faça login (ver avancado/README.md).")
    prompt = (AQUI / "prompt_analise.md").read_text(encoding="utf-8")
    entrada = prompt + "\n" + json.dumps(resumo, ensure_ascii=False, indent=2)
    if instrucao_extra:
        entrada += "\n\n" + instrucao_extra
    r = subprocess.run([claude, "-p"], input=entrada, capture_output=True, text=True,
                       encoding="utf-8", timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"Erro ao chamar o Claude Code:\n{r.stderr}")
    return r.stdout.strip().removeprefix("```html").removesuffix("```").strip()


# ------------------------------------------------------------------ contas extras (Python, nunca o Claude)
def _mediana(resumo: dict, indicador: str, ano: int):
    for l in resumo.get("indicadores", []):
        if l.get("indicador") == indicador and l.get("ano") == ano and l.get("mediana") is not None:
            return l["mediana"]
    return None


def juro_real(selic: float, ipca: float) -> float:
    """Juro real ex-ante, fórmula exata: (1 + Selic) / (1 + IPCA) − 1, em % com 2 casas."""
    return round(((1 + selic / 100) / (1 + ipca / 100) - 1) * 100, 2)


def contas_extras(resumo: dict) -> dict:
    """Contas que o texto pode citar. Campo ausente no JSON -> a conta não entra (nunca inventa)."""
    contas: dict = {"n_alertas": len(resumo.get("alertas", []))}  # contagem que o texto pode citar
    anos = sorted({l["ano"] for l in resumo.get("indicadores", []) if l.get("indicador") == "Selic"})

    juros = []
    for ano in anos:
        selic, ipca = _mediana(resumo, "Selic", ano), _mediana(resumo, "IPCA", ano)
        if selic is not None and ipca is not None:
            juros.append({"ano": ano, "selic_fim_do_ano": selic, "ipca_do_ano": ipca,
                          "juro_real": juro_real(selic, ipca)})
    if juros:
        contas["juro_real_esperado"] = juros
        contas["juro_real_formula"] = "(1 + Selic do fim do ano) / (1 + IPCA do mesmo ano) − 1"

    if len(anos) >= 2:
        a, b = anos[0], anos[1]
        s_a, s_b = _mediana(resumo, "Selic", a), _mediana(resumo, "Selic", b)
        contas["variacao_selic_entre_anos"] = {
            "de_ano": a, "para_ano": b, "selic_de": s_a, "selic_para": s_b,
            "variacao_pp": round(s_b - s_a, 2)}

    vies = None
    res = (resumo.get("acuracia_resumo") or {}).get("IPCA")
    if res and res.get("erro_medio") is not None:
        vies = {"erro_medio_pp": res["erro_medio"], "anos": res.get("anos"),
                "horizonte": res.get("horizonte_principal"), "fonte": "acuracia_resumo"}
    else:
        erros = [l["erro_pp"] for l in resumo.get("acuracia", [])
                 if l.get("indicador") == "IPCA" and l.get("erro_pp") is not None]
        if erros:
            vies = {"erro_medio_pp": round(sum(erros) / len(erros), 2), "n_anos": len(erros),
                    "fonte": "media de acuracia[*].erro_pp"}
    if vies:
        vies["leitura"] = ("erro = realizado − esperado; positivo = o IPCA veio acima do que o Focus esperava "
                           "(mercado subestimou)")
        contas["vies_historico_ipca"] = vies
    return contas


def com_contas(resumo: dict) -> dict:
    """Cópia do resumo com as contas extras em `contas_frente_c` (o que vai para o motor e para o conferir)."""
    novo = dict(resumo)
    novo["contas_frente_c"] = contas_extras(resumo)
    return novo


# ------------------------------------------------------------------ conferência
_EXTENSO = {
    "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8,
    "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "catorze": 14,
    "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19, "vinte": 20,
    "trinta": 30, "quarenta": 40, "cinquenta": 50, "sessenta": 60, "setenta": 70, "oitenta": 80,
    "noventa": 90, "cem": 100, "segunda": 2, "segundo": 2, "terceira": 3, "terceiro": 3,
    "quarta": 4, "quarto": 4, "quinta": 5, "quinto": 5, "sexta": 6, "sexto": 6, "sétima": 7,
    "sétimo": 7, "oitava": 8, "oitavo": 8, "nona": 9, "nono": 9, "décima": 10, "décimo": 10,
}
# "um/uma/primeira" ficam de fora: são artigo ou "primeira vez" quase sempre.
_HORIZONTES_FIXOS = re.compile(r"\b(?:4|quatro)\s+semanas\b|\b(?:5|cinco)\s+anos\b|\b12\s+meses\b", re.I)
_DATA = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2}/\d{4}\b")
_FORMULA_1 = re.compile(r"\(\s*1\s*\+|\)\s*[−–-]\s*1\b")


def _texto_puro(texto: str) -> str:
    return unicodedata.normalize("NFC", re.sub(r"<[^>]+>", " ", texto))


def conferir(texto: str, resumo: dict) -> list[str]:
    """Todo número do texto precisa existir no JSON (pega número inventado). Devolve os suspeitos.

    Confere decimais ("4,73"), inteiros e percentuais inteiros ("5%", "13ª") e números por extenso ("sete").
    Não são suspeitos: anos de 2020 a 2030, datas que estão no JSON (ex.: 30/10/2026, 09/2026), os horizontes
    fixos "4 semanas", "5 anos", "12 meses" e o "1" da fórmula do juro real.
    """
    citaveis = {k: v for k, v in resumo.items() if k not in CAMPOS_INTERNOS}
    bruto = json.dumps(citaveis, ensure_ascii=False)
    validos = set()
    for v in re.findall(r"\d+(?:[.,]\d+)?", bruto):
        validos.add(round(float(v.replace(",", ".")), 2))

    t = _texto_puro(texto)
    suspeitos = []
    for d in _DATA.findall(t):  # datas: valem só se estiverem no JSON
        if d not in bruto:
            suspeitos.append(d)
    t = _DATA.sub(" ", t)
    t = _HORIZONTES_FIXOS.sub(" ", t)
    t = _FORMULA_1.sub(" ", t)

    for v in re.findall(r"\d+(?:[.,]\d+)*", t):
        if re.fullmatch(r"\d+(?:\.\d{3})+", v):  # 1.000 (milhar)
            x = float(v.replace(".", ""))
        elif v.count(",") + v.count(".") > 1:
            suspeitos.append(v)
            continue
        else:
            x = float(v.replace(",", "."))
        if x.is_integer() and 2020 <= x <= 2030:  # ano
            continue
        if round(x, 2) not in validos:
            suspeitos.append(v)

    for palavra in re.findall(r"[a-záéíóúâêôãõç]+", t.lower()):
        n = _EXTENSO.get(palavra)
        if n is not None and float(n) not in validos:
            suspeitos.append(palavra)
    return suspeitos


# ------------------------------------------------------------------ análise conferida + reescrita
def instrucao_reescrita(texto_anterior: str, suspeitos: list[str]) -> str:
    """O que vai para o motor quando a conferência reprova o texto."""
    return (
        "CORREÇÃO OBRIGATÓRIA. O texto abaixo foi reprovado na conferência porque cita números que NÃO "
        f"existem no JSON: {', '.join(suspeitos)}.\n"
        "Reescreva a análise inteira seguindo as mesmas regras. Use só números que aparecem no JSON, "
        "com as mesmas 2 casas decimais. Não faça contas: se o número não está no JSON, tire a frase.\n\n"
        f"Texto reprovado:\n{texto_anterior}"
    )


def _salvar_contas(contas: dict) -> None:
    """Grava as contas em saida/contas_frente_c.json para a conferência manual (o agente passa uma cópia
    do resumo à análise, então elas não chegam sozinhas ao resumo_semana.json)."""
    try:
        if ARQ_CONTAS.parent.is_dir():
            ARQ_CONTAS.write_text(json.dumps(contas, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def analisar_conferido(resumo: dict, gerar=None, tentativas: int = 2) -> tuple[str, list[str]]:
    """Gera a análise e confere. Devolve (html, suspeitos). Lista vazia = pode enviar.

    Assinatura fixa: o agente_semanal.py chama assim e PARA (ou passa ao próximo motor) se `suspeitos`
    não vier vazio. `gerar` é injetável para os testes não chamarem o Claude (padrão: analisar).
    Se houver suspeitos, chama o MESMO `gerar` de novo, até `tentativas` vezes, com o texto anterior e os
    números fora do JSON em `instrucao_extra`. Devolve o primeiro texto que passar, ou o último e os suspeitos.
    """
    gerar = gerar or analisar
    dados = com_contas(resumo)
    _salvar_contas(dados["contas_frente_c"])
    texto = gerar(dados)
    suspeitos = conferir(texto, dados)
    # Nunca `claude -p` direto aqui: a reserva (reserva.py: Codex, sem IA) usa este mesmo caminho.
    for _ in range(tentativas):
        if not suspeitos:
            break
        texto = gerar(dados, instrucao_reescrita(texto, suspeitos))
        suspeitos = conferir(texto, dados)
    return texto, suspeitos
