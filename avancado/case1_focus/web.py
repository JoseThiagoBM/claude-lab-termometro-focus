"""
Versão web do relatório da semana (o ARTEFATO PÚBLICO). Dono: Frente D.

    montar_web(resumo, analise, saida) -> str     # página para publicar (claude.ai ou GitHub Pages)

Mesmos dados do e-mail (resumo_semana.json), em página responsiva com tema claro e escuro.
A página não traz <html>/<head>/<body>: o claude.ai embrulha no esqueleto ao publicar, e o navegador
abre o arquivo local do mesmo jeito. O gráfico vai em base64 (a página não carrega nada de fora,
só as fontes do Google Fonts).
"""
import base64
import html
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
REPO = "https://github.com/JoseThiagoBM/claude-lab-termometro-focus"
NOMES = {"IPCA": "IPCA", "Selic": "Selic (fim do ano)", "Câmbio": "Câmbio (R$/US$)", "PIB Total": "PIB Total"}
UNID = {"IPCA": "%", "Selic": "% a.a.", "Câmbio": "R$/US$", "PIB Total": "%"}
MOTORES = {"claude": "Claude", "codex": "Codex", "sem_ia": "texto automático, sem IA"}

CSS = """
/* Layout: uma coluna de leitura (~760px); faixa de alertas no topo; tabelas no formato do Relatório Focus. */
:root {
  --bg: #f4f6f8; --surface: #ffffff; --fg: #17222c; --muted: #5b6b78; --line: #d8e0e7;
  --accent: #0b5c7a; --accent-soft: #e3f0f5; --alert: #b4510f; --alert-soft: #fdf0e4;
  --up: #b4510f; --down: #1d6b4f; --rare: #9b2c2c; --rare-soft: #fbe9e9; --paper: #ffffff;
  --display: "IBM Plex Sans Condensed", "Arial Narrow", Arial, sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", Arial, sans-serif;
  --mono: "IBM Plex Mono", Consolas, "Courier New", monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0f161c; --surface: #16212a; --fg: #e3eaf0; --muted: #93a4b2; --line: #2a3a46;
  --accent: #5fb4d6; --accent-soft: #15303c; --alert: #f0a061; --alert-soft: #33231a;
  --up: #f0a061; --down: #6cc79f; --rare: #f08c8c; --rare-soft: #3a1f22; --paper: #ffffff; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #0f161c; --surface: #16212a; --fg: #e3eaf0; --muted: #93a4b2; --line: #2a3a46;
  --accent: #5fb4d6; --accent-soft: #15303c; --alert: #f0a061; --alert-soft: #33231a;
  --up: #f0a061; --down: #6cc79f; --rare: #f08c8c; --rare-soft: #3a1f22; --paper: #ffffff; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font: 15px/1.55 var(--body); margin: 0;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
main { max-width: 760px; margin: 0 auto; padding-block: 28px 40px; display: grid; gap: 28px; }
h1, h2 { font-family: var(--display); text-wrap: balance; margin: 0; line-height: 1.15; }
h1 { font-size: clamp(26px, 5vw, 34px); font-weight: 600; }
h2 { font-size: 20px; font-weight: 600; color: var(--accent); }
section { display: grid; gap: 12px; min-width: 0; }
.eyebrow { font: 600 12px var(--body); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }
.meta { color: var(--muted); font-size: 13px; display: flex; flex-wrap: wrap; gap: 4px 14px; }
.ok { color: var(--down); font-weight: 600; }
.alertas { background: var(--alert-soft); border-left: 4px solid var(--alert); padding: 12px 16px; display: grid; gap: 6px; }
.alertas strong { color: var(--alert); }
.alertas ul, .incerteza ul { margin: 0; padding-left: 18px; display: grid; gap: 3px; }
.incerteza { border-left: 4px solid var(--line); padding: 4px 16px; display: grid; gap: 6px; }
.nota { color: var(--muted); font-size: 12.5px; margin: 0; }
.cartoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
.cartao { background: var(--surface); border: 1px solid var(--line); padding: 12px 14px; display: grid; gap: 2px; min-width: 0; }
.cartao .rot { font-size: 12px; color: var(--muted); }
.cartao .val { font: 600 26px var(--display); font-variant-numeric: tabular-nums; }
.cartao .det { font-size: 12.5px; color: var(--muted); }
.analise { background: var(--surface); border: 1px solid var(--line); padding: 4px 20px 8px; min-width: 0; }
.analise h3 { font-family: var(--display); font-size: 18px; margin: 14px 0 6px; text-wrap: balance; }
.analise ul { padding-left: 20px; } .analise li { margin: 4px 0; }
.rolagem { overflow-x: auto; border: 1px solid var(--line); background: var(--surface); }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
th { font-size: 11.5px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
th:first-child, td:first-child { text-align: left; }
td.num { font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 13.5px; }
tbody tr:last-child td { border-bottom: 0; }
.sobe { color: var(--up); } .desce { color: var(--down); } .igual { color: var(--muted); }
.chip { display: inline-block; font-size: 11.5px; padding: 1px 7px; border-radius: 10px; font-family: var(--body); }
.chip.rara { background: var(--rare-soft); color: var(--rare); font-weight: 600; }
.chip.incomum { background: var(--alert-soft); color: var(--alert); }
.chip.normal { color: var(--muted); }
figure { margin: 0; background: var(--paper); border: 1px solid var(--line); padding: 8px; }
figure img { display: block; width: 100%; max-width: 100%; height: auto; }
.verificacao { display: grid; gap: 8px; padding-left: 0; list-style: none; margin: 0; }
.verificacao li { padding-left: 22px; position: relative; }
.verificacao li::before { content: "✓"; position: absolute; left: 0; color: var(--down); font-weight: 700; }
footer { border-top: 1px solid var(--line); padding-top: 14px; color: var(--muted); font-size: 12.5px; display: grid; gap: 6px; }
a { color: var(--accent); }
a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
"""


def _n(v, casas: int = 2, sinal: bool = False) -> str:
    if v is None:
        return "—"
    return (f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}").replace(".", ",")


def _e(t) -> str:
    return html.escape(str(t))


def _comp_semanal(l: dict) -> str:
    """Como na coluna 'Comp. semanal' do Relatório Focus: ▲/▼/= e, entre parênteses, semanas seguidas."""
    v = l.get("var_semana") or 0
    seta, cls = ("▲", "sobe") if v > 0 else ("▼", "desce") if v < 0 else ("=", "igual")
    n = l.get("sequencia_semanas")
    return f'<span class="{cls}">{seta}{f" ({n})" if n else ""}</span>'


def _tabela(resumo: dict) -> str:
    linhas = []
    for l in resumo.get("indicadores", []):
        rar = l.get("raridade_4s")
        chip = (f'<span class="chip {_e(rar)}">{_e(rar)} · p{l.get("percentil_4s")}</span>' if rar else "—")
        linhas.append(
            f'<tr><td>{_e(NOMES.get(l["indicador"], l["indicador"]))} {l["ano"]}</td>'
            f'<td class="num">{_n(l.get("mediana_4_semanas_atras"))}</td>'
            f'<td class="num">{_n(l.get("mediana_semana_anterior"))}</td>'
            f'<td class="num"><strong>{_n(l["mediana"])}</strong></td>'
            f'<td class="num">{_comp_semanal(l)}</td>'
            f'<td class="num">{_n(l.get("var_4_semanas"), sinal=True)}</td>'
            f'<td>{chip}</td><td class="num">{_e(l.get("respondentes", "—"))}</td></tr>')
    return ('<div class="rolagem"><table><thead><tr><th>Mediana – Agregado</th><th>Há 4 semanas</th>'
            '<th>Há 1 semana</th><th>Hoje</th><th>Comp. semanal</th><th>Var. 4 semanas</th>'
            '<th>Raridade 4 sem.</th><th>Resp.</th></tr></thead><tbody>'
            + "".join(linhas) + "</tbody></table></div>")


def _cartoes(resumo: dict) -> str:
    t, c = resumo.get("termometro") or {}, resumo.get("contas_frente_c") or {}
    itens = []
    if "selic_hoje" in t:
        itens.append(("Selic hoje", f'{_n(t["selic_hoje"])}%',
                      f'Focus espera {_n(t.get("selic_esperada_fim_do_ano"))}% no fim do ano'))
    if "ipca_12m" in t:
        itens.append((f'IPCA 12 meses ({_e(t.get("ipca_12m_mes", ""))})', f'{_n(t["ipca_12m"])}%',
                      f'{_n(t.get("ipca_12m_menos_meta"), sinal=True)} p.p. sobre a meta de {_n(t.get("meta_inflacao"))}%'))
    if "dolar_ptax" in t:
        itens.append(("Dólar PTAX", f'R$ {_n(t["dolar_ptax"])}', f'venda em {_e(t.get("dolar_ptax_data", ""))}'))
    juros = {j["ano"]: j["juro_real"] for j in c.get("juro_real_esperado", [])}
    if juros:
        ano = min(juros)
        itens.append((f"Juro real esperado {ano}", f"{_n(juros[ano])}%",
                      "(1 + Selic) / (1 + IPCA) − 1, Focus do ano"))
    return '<div class="cartoes">' + "".join(
        f'<div class="cartao"><span class="rot">{r}</span><span class="val">{v}</span><span class="det">{d}</span></div>'
        for r, v, d in itens) + "</div>"


def _alertas(resumo: dict) -> str:
    a, inc = resumo.get("alertas") or [], resumo.get("sinais_de_incerteza") or []
    partes = []
    if a:
        partes.append(f'<div class="alertas" role="note"><strong>{len(a)} alerta(s) nesta semana</strong><ul>'
                      + "".join(f"<li>{_e(x)}</li>" for x in a) + "</ul></div>")
    else:
        partes.append('<p class="ok">Nenhuma variação fora do normal nesta semana.</p>')
    if inc:
        partes.append('<div class="incerteza"><strong>Sinais de incerteza</strong>'
                      '<span class="nota">As instituições discordam mais do que há 4 semanas.</span><ul>'
                      + "".join(f"<li>{_e(x)}</li>" for x in inc) + "</ul></div>")
    if resumo.get("regra_de_alerta"):
        partes.append(f'<p class="nota">Regra do alerta: {_e(resumo["regra_de_alerta"])}.</p>')
    return "".join(partes)


def _historico(resumo: dict, saida: Path | None) -> str:
    partes = []
    png = saida / "acuracia.png" if saida else None
    if png and png.exists():
        b64 = base64.b64encode(png.read_bytes()).decode()
        partes.append(f'<figure><img src="data:image/png;base64,{b64}" width="700" height="430" '
                      f'alt="Esperado pelo Focus em três momentos e realizado, IPCA e Selic, 2021 a 2025"></figure>')
    res = resumo.get("acuracia_resumo") or {}
    if res:
        hs = ["12 meses antes", "início do ano", "meio do ano"]
        linhas = "".join(
            f'<tr><td>{ind}</td>' + "".join(
                f'<td class="num">{_n(res[ind]["por_horizonte"].get(h, {}).get("erro_abs_medio"))}</td>' for h in hs)
            + f'<td class="num">{res[ind].get("anos_subestimou", "—")} de {res[ind].get("n_anos", "—")}</td></tr>'
            for ind in ("IPCA", "Selic") if ind in res)
        partes.append('<div class="rolagem"><table><thead><tr><th>Erro absoluto médio (p.p.)</th>'
                      '<th>12 meses antes</th><th>Janeiro</th><th>Julho</th><th>Subestimou (jan.)</th></tr></thead>'
                      f'<tbody>{linhas}</tbody></table></div>')
        partes.append('<p class="nota">Erro = realizado − esperado. IPCA composto mês a mês; Selic meta no fim do ano. '
                      f'Anos fechados: {_e(res.get("IPCA", {}).get("anos", ""))}.</p>')
    return "".join(partes) or '<p class="nota">Histórico indisponível nesta execução.</p>'


def _verificacao(resumo: dict) -> str:
    itens = [
        "Antes de escrever, o agente checa o dado: Focus atrasado, respondentes abaixo do mínimo, semana repetida, "
        "linhas duplicadas, série do SGS parada e IPCA composto × série oficial. Se algo falha, ele não envia o "
        "relatório e avisa o time.",
        "Todo número citado na análise precisa existir nos dados calculados. Se não existir, a IA reescreve o texto "
        "(até 2 vezes) ou o agente usa outro motor.",
        "As contas (variações, juro real, histórico) são feitas em Python. A IA só escreve o texto.",
    ]
    total = RAIZ / "validacao" / "saida_recalculo.txt"
    if total.exists():
        linha = next((l for l in total.read_text(encoding="utf-8").splitlines() if l.startswith("TOTAL:")), "")
        if linha:
            itens.append(f"Validação independente (código separado, direto dos CSVs do BC): {_e(linha[6:].strip())}.")
    return '<ul class="verificacao">' + "".join(f"<li>{i}</li>" for i in itens) + "</ul>"


def montar_web(resumo: dict, analise: str, saida: Path | None = None) -> str:
    data = _e(resumo["data_focus"])
    motor = MOTORES.get(resumo.get("motor_analise", "claude"), resumo.get("motor_analise", ""))
    return f"""<title>Termômetro do Focus</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
<main>
<header style="display:grid;gap:8px">
  <span class="eyebrow">Termômetro do Focus · relatório semanal</span>
  <h1>Relatório Focus de {data}</h1>
  <div class="meta"><span>Gerado em {_e(resumo.get("gerado_em", ""))}</span>
  <span>Análise: {_e(motor)}</span><span class="ok">Números conferidos contra os dados do BC</span></div>
</header>
<section aria-labelledby="s-alertas"><h2 id="s-alertas">Alertas</h2>{_alertas(resumo)}</section>
<section aria-labelledby="s-agora"><h2 id="s-agora">O que já aconteceu × o que o mercado espera</h2>{_cartoes(resumo)}</section>
<section aria-labelledby="s-analise"><h2 id="s-analise">Análise da semana</h2><div class="analise">{analise}</div></section>
<section aria-labelledby="s-numeros"><h2 id="s-numeros">Expectativas de mercado</h2>{_tabela(resumo)}
<p class="nota">Medianas do Focus, como no relatório do BC. Comp. semanal: ▲ subiu, ▼ caiu, = estável; entre parênteses,
semanas seguidas na mesma direção. Raridade: percentil da variação de 4 semanas entre as dos últimos 6 anos.</p></section>
<section aria-labelledby="s-hist"><h2 id="s-hist">O Focus acertou? Últimos 5 anos fechados</h2>{_historico(resumo, saida)}</section>
<section aria-labelledby="s-verif"><h2 id="s-verif">Como conferimos</h2>{_verificacao(resumo)}</section>
<footer>
  <span>Fonte: Banco Central do Brasil, Relatório Focus de {data} (API Olinda) e séries do SGS (433, 13522, 432, 1).</span>
  <span>Projeto acadêmico do Claude Lab PUC-Rio, 06/11/2026. Não constitui recomendação de investimento.</span>
  <span>Código, dados e metodologia: <a href="{REPO}" target="_blank" rel="noopener">{REPO.removeprefix("https://")}</a></span>
</footer>
</main>
"""
