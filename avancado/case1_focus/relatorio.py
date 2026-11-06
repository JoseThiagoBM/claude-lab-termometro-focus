"""
Etapa 6 do agente: MONTAR o relatório em HTML (é o corpo do e-mail e o artefato web).
Dono: Frente D. Entrada: `resumo` (CONTRATO.md) + HTML da análise. Saída: HTML completo.

Assinatura fixa: montar(resumo, analise, saida) — `saida` é a pasta onde estão os gráficos (ex.: acuracia.png).

As imagens entram em base64 (`data:image/png;base64,...`), o que funciona no navegador e no artefato.
O Gmail não mostra imagem em base64: o enviar_email.py troca cada uma por um anexo com Content-ID.
Estilos todos inline e layout em tabela, porque clientes de e-mail ignoram <style> e CSS moderno.
"""
import base64
import html
from pathlib import Path

COR = {"texto": "#1f2933", "suave": "#616e7c", "borda": "#d9e2ec", "fundo": "#f5f7fa",
       "marca": "#0b4f6c", "alerta": "#b44d12", "alerta_fundo": "#fff4e5", "ok": "#2f7d32"}
NOMES = {"IPCA": "IPCA (%)", "Selic": "Selic, fim do ano (%)", "Câmbio": "Câmbio, fim do ano (R$/US$)",
         "PIB Total": "PIB (%)"}


def _num(v, sinal: bool = False) -> str:
    """5.2 -> '5,20'; com sinal: 0.3 -> '+0,30'. Mesmo arredondamento do JSON (2 casas)."""
    if v is None:
        return "—"
    return (f"{v:+.2f}" if sinal else f"{v:.2f}").replace(".", ",")


def _imagem(caminho: Path, alt: str) -> str:
    if not caminho or not caminho.exists():
        return ""
    b64 = base64.b64encode(caminho.read_bytes()).decode()
    return (f'<img src="data:image/png;base64,{b64}" alt="{html.escape(alt)}" width="640" '
            f'style="width:100%;max-width:640px;height:auto;display:block;border:0">')


def _secao(titulo: str, corpo: str) -> str:
    return (f'<tr><td style="padding:20px 24px 4px"><h2 style="margin:0 0 10px;font-size:17px;'
            f'color:{COR["marca"]}">{titulo}</h2>{corpo}</td></tr>')


def _alertas(resumo: dict) -> str:
    alertas = resumo.get("alertas") or []
    if not alertas:
        return (f'<p style="margin:0;color:{COR["ok"]}">Nenhuma variação fora do normal nas últimas 4 semanas.</p>')
    itens = "".join(f"<li style=\"margin:2px 0\">{html.escape(a)}</li>" for a in alertas)
    return (f'<div style="background:{COR["alerta_fundo"]};border-left:4px solid {COR["alerta"]};'
            f'padding:10px 14px"><strong style="color:{COR["alerta"]}">{len(alertas)} alerta(s) nesta semana</strong>'
            f'<ul style="margin:6px 0 0;padding-left:18px">{itens}</ul></div>')


def _tabela_semana(resumo: dict) -> str:
    th = f'style="text-align:right;padding:6px 8px;border-bottom:2px solid {COR["borda"]};font-size:12px;color:{COR["suave"]}"'
    cab = (f'<tr><th {th.replace("right", "left")}>Indicador</th><th {th}>Ano</th><th {th}>Mediana</th>'
           f'<th {th}>Semana</th><th {th}>4 semanas</th><th {th}>Desvio-padrão</th></tr>')
    linhas = []
    for l in resumo.get("indicadores", []):
        td = f'style="text-align:right;padding:6px 8px;border-bottom:1px solid {COR["borda"]}"'
        linhas.append(
            f'<tr><td {td.replace("right", "left")}>{NOMES.get(l["indicador"], l["indicador"])}</td>'
            f'<td {td}>{l["ano"]}</td><td {td}><strong>{_num(l["mediana"])}</strong></td>'
            f'<td {td}>{_num(l["var_semana"], True)}</td><td {td}>{_num(l["var_4_semanas"], True)}</td>'
            f'<td {td}>{_num(l.get("desvio_padrao"))}</td></tr>')
    meta = next((l for l in resumo.get("indicadores", []) if "distancia_da_meta" in l), None)
    nota = (f'<p style="margin:8px 0 0;font-size:12px;color:{COR["suave"]}">Mediana das projeções do Focus. '
            f'Variações em pontos percentuais (Câmbio em R$). '
            + (f'IPCA {meta["ano"]} está {_num(meta["distancia_da_meta"])} p.p. acima da meta de 3%.' if meta else "")
            + '</p>')
    return f'<table role="presentation" cellspacing="0" width="100%" style="border-collapse:collapse;font-size:14px">{cab}{"".join(linhas)}</table>{nota}'


def _historico(resumo: dict, saida: Path | None) -> str:
    acc = resumo.get("acuracia") or []
    if not acc:
        return f'<p style="color:{COR["suave"]}">Histórico indisponível nesta execução.</p>'
    img = _imagem(saida / "acuracia.png", "Esperado × realizado de IPCA e Selic") if saida else ""
    td = f'style="text-align:right;padding:4px 8px;border-bottom:1px solid {COR["borda"]}"'
    linhas = "".join(
        f'<tr><td {td.replace("right", "left")}>{a["indicador"]}</td><td {td}>{a["ano"]}</td>'
        f'<td {td}>{_num(a["esperado"])}</td><td {td}>{_num(a["realizado"])}</td>'
        f'<td {td}><strong>{_num(a["erro_pp"], True)}</strong></td></tr>' for a in acc)
    quando = acc[0].get("quando", "")
    tabela = (f'<table role="presentation" cellspacing="0" width="100%" style="border-collapse:collapse;font-size:13px;margin-top:10px">'
              f'<tr><th {td.replace("right", "left")}>Indicador</th><th {td}>Ano</th><th {td}>Esperado</th>'
              f'<th {td}>Realizado</th><th {td}>Erro (p.p.)</th></tr>{linhas}</table>'
              f'<p style="margin:6px 0 0;font-size:12px;color:{COR["suave"]}">Esperado = mediana do Focus no {html.escape(quando)}. '
              f'Erro positivo = o realizado ficou acima do esperado. IPCA composto mês a mês; Selic meta no fim do ano.</p>')
    return img + tabela


def montar(resumo: dict, analise: str, saida: Path | None = None) -> str:
    data = resumo["data_focus"]
    corpo = "".join([
        _secao("Alertas", _alertas(resumo)),
        _secao("Análise da semana", f'<div style="font-size:15px;line-height:1.5">{analise}</div>'),
        _secao("Números da semana", _tabela_semana(resumo)),
        _secao("O Focus acertou? Últimos 5 anos fechados", _historico(resumo, saida)),
    ])
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Termômetro do Focus — {data}</title></head>
<body style="margin:0;padding:0;background:{COR['fundo']};font-family:Arial,Helvetica,sans-serif;color:{COR['texto']}">
<table role="presentation" cellspacing="0" width="100%" style="background:{COR['fundo']}"><tr><td align="center" style="padding:16px">
<table role="presentation" cellspacing="0" width="100%" style="max-width:680px;background:#ffffff;border:1px solid {COR['borda']}">
<tr><td style="background:{COR['marca']};color:#ffffff;padding:18px 24px">
<div style="font-size:12px;letter-spacing:.5px;text-transform:uppercase;opacity:.85">Termômetro do Focus</div>
<div style="font-size:22px;font-weight:bold;margin-top:4px">Relatório Focus de {data}</div>
<div style="font-size:12px;opacity:.85;margin-top:4px">Gerado automaticamente em {resumo.get('gerado_em', '')} · números conferidos contra os dados do BC</div>
</td></tr>
{corpo}
<tr><td style="padding:20px 24px;font-size:11px;color:{COR['suave']};border-top:1px solid {COR['borda']}">
Fonte: Banco Central do Brasil, Relatório Focus de {data} (API Olinda) e séries do SGS (433, 13522, 432).
Análise escrita pelo Claude e conferida automaticamente: todo número do texto existe nos dados calculados.
Projeto acadêmico do Claude Lab PUC-Rio. Não constitui recomendação de investimento.
</td></tr></table></td></tr></table></body></html>"""
