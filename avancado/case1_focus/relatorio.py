"""Newsletter do Focus: tabelas e estilos inline, com imagem base64 para conversão em CID."""
import base64
import html
from pathlib import Path

COR = {'texto': '#243e4b', 'suave': '#526975', 'borda': '#dce5e9',
       'fundo': '#eef3f5', 'marca': '#0b5c7a', 'alerta': '#b4510f', 'ok': '#1d6b4f'}
MOTORES = {'claude': 'Claude', 'codex': 'Codex', 'sem_ia': 'um texto automático, sem IA'}
NOMES = {'IPCA': 'IPCA (%)', 'Selic': 'Selic, fim do ano (%)',
         'Câmbio': 'Câmbio, fim do ano (R$/US$)', 'PIB Total': 'PIB Total (%)'}


def _esc(value) -> str:
    return html.escape(str(value if value is not None else '—'))


def _num(value, sinal=False) -> str:
    if value is None:
        return '—'
    return (f'{value:+.2f}' if sinal else f'{value:.2f}').replace('.', ',')


def _imagem(caminho: Path, alt: str) -> str:
    if not caminho.exists():
        return ''
    encoded = base64.b64encode(caminho.read_bytes()).decode()
    return (f'<img src="data:image/png;base64,{encoded}" alt="{_esc(alt)}" width="600" '
            'style="display:block;width:100%;max-width:600px;height:auto;border:0;background:#ffffff">')


def _secao(titulo, corpo, rotulo='') -> str:
    return (f'<tr><td bgcolor="#ffffff" style="padding:24px 16px;background:#ffffff;color:{COR["texto"]};'
            f'border-top:1px solid {COR["borda"]}">'
            f'<p style="margin:0 0 6px;font-size:14px;letter-spacing:1px;color:{COR["marca"]};font-weight:bold">{_esc(rotulo)}</p>'
            f'<h2 style="margin:0 0 16px;font-size:22px;line-height:1.25;color:{COR["texto"]}">{_esc(titulo)}</h2>{corpo}</td></tr>')


def _lista(itens, compacto=False) -> str:
    margem = 3 if compacto else 10
    return ''.join(f'<li style="margin:0 0 {margem}px">{_esc(i)}</li>' for i in itens)


def _alertas(resumo) -> str:
    alertas = resumo.get('alertas') or []
    if alertas:
        bloco = (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>'
                 f'<td bgcolor="#ffffff" style="background:#ffffff;border-left:4px solid {COR["alerta"]};padding:4px 12px;'
                 f'color:{COR["texto"]};font-size:16px;line-height:1.5">'
                 f'<strong style="color:{COR["alerta"]}">{len(alertas)} alerta(s) nesta semana</strong>'
                 f'<ul style="padding-left:20px;margin:12px 0 0">{_lista(alertas)}</ul></td></tr></table>')
    else:
        bloco = f'<p style="margin:0;color:{COR["ok"]}">Nenhum alerta sinalizado nesta edição.</p>'
    incerteza = resumo.get('sinais_de_incerteza') or []
    if incerteza:
        bloco += (f'<p style="margin:10px 0 4px;font-size:12px;font-weight:bold;color:{COR["suave"]}">Sinais de incerteza</p>'
                  f'<ul style="margin:0;padding-left:20px;font-size:12px;line-height:1.35">{_lista(incerteza, compacto=True)}</ul>')
    if resumo.get('regra_de_alerta'):
        bloco += f'<p style="font-size:12px;line-height:1.35;color:{COR["suave"]};margin:8px 0 0">Regra: {_esc(resumo.get("regra_de_alerta"))}.</p>'
    return bloco


def _cartao(rotulo, valor, detalhe, data) -> str:
    # Uma coluna em qualquer largura: não depende de media queries no Gmail.
    return (f'<tr><td bgcolor="#ffffff" style="background:#ffffff;padding:16px;border:1px solid {COR["borda"]};'
            f'border-top:3px solid {COR["marca"]};color:{COR["texto"]}">'
            f'<p style="margin:0;font-size:14px;font-weight:bold;color:{COR["marca"]}">{rotulo}</p>'
            f'<p style="margin:6px 0;font-size:30px;line-height:1.2;font-weight:bold;font-variant-numeric:tabular-nums">{valor}</p>'
            f'<p style="margin:0;font-size:14px;line-height:1.5">{detalhe}</p>'
            f'<p style="margin:8px 0 0;font-size:14px;color:{COR["suave"]}">Fonte: BCB · {data}</p>'
            '</td></tr><tr><td height="10" style="height:10px;background:#ffffff"></td></tr>')


def _termometro(resumo) -> str:
    t = resumo.get('termometro') or {}
    cards = []
    if t.get('selic_hoje') is not None:
        cards.append(_cartao('SELIC OBSERVADA', f'{_num(t.get("selic_hoje"))}%',
            f'Focus: {_num(t.get("selic_esperada_fim_do_ano"))}% no fim do ano · '
            f'diferença {_num(t.get("selic_esperada_menos_hoje"), True)} p.p.',
            f'SGS: {_esc(t.get("selic_hoje_data"))} · Focus: {_esc(resumo.get("data_focus"))}'))
    if t.get('ipca_12m') is not None:
        cards.append(_cartao('IPCA EM 12 MESES', f'{_num(t.get("ipca_12m"))}%',
            f'Distância da meta: {_num(t.get("ipca_12m_menos_meta"), True)} p.p. · '
            f'meta {_num(t.get("meta_inflacao"))}% · teto {_num(t.get("teto_da_meta"))}%', _esc(t.get('ipca_12m_mes'))))
    if t.get('dolar_ptax') is not None:
        cards.append(_cartao('DÓLAR PTAX', f'R$ {_num(t.get("dolar_ptax"))}', 'Cotação de venda', _esc(t.get('dolar_ptax_data'))))
    if not cards:
        return ''
    return _secao('O que já aconteceu × o que o mercado espera',
        f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0">{"".join(cards)}</table>', 'OBSERVADO × ESPERADO')


def _comparacao(linha):
    variacao = linha.get('var_semana')
    if variacao is None:
        return '—', COR['suave']
    seta = '▲' if variacao > 0 else '▼' if variacao < 0 else '='
    sequencia = linha.get('sequencia_semanas')
    texto = seta + (f' ({_esc(sequencia)})' if sequencia is not None else '')
    return texto, COR['alerta'] if variacao > 0 else COR['ok'] if variacao < 0 else COR['suave']


def _tabela_semana(resumo):
    # Indicador/ano ocupa uma linha própria para manter as cinco colunas legíveis no celular.
    style = f'padding:10px 2px;text-align:right;font-size:14px;border-bottom:1px solid {COR["borda"]};font-variant-numeric:tabular-nums;'
    cab = ''.join(f'<th scope="col" width="20%" style="{style}color:{COR["suave"]};font-weight:normal">{t}</th>'
                  for t in ('Há 4 semanas', 'Há 1 semana', 'Hoje', 'Comp. semanal', 'Resp.'))
    linhas = []
    for l in resumo.get('indicadores') or []:
        ind = l.get('indicador')
        comp, cor = _comparacao(l)
        linhas.append(f'<tr><th colspan="5" scope="rowgroup" style="padding:20px 2px 8px;text-align:left;font-size:16px;color:{COR["marca"]}">'
                      f'{_esc(NOMES.get(ind, ind))} · {_esc(l.get("ano"))}</th></tr>')
        valores = (_num(l.get('mediana_4_semanas_atras')), _num(l.get('mediana_semana_anterior')),
                   _num(l.get('mediana')), comp, _esc(l.get('respondentes')))
        linhas.append('<tr>' + ''.join(
            f'<td style="{style}color:{cor if i == 3 else COR["texto"]};font-weight:{"bold" if i in (2,3) else "normal"}">{v}</td>'
            for i,v in enumerate(valores)) + '</tr>')
    if not linhas:
        return '<p>Números da semana indisponíveis nesta execução.</p>'
    return (f'<table width="100%" cellspacing="0" cellpadding="0" style="table-layout:fixed;border-collapse:collapse;background:#ffffff">'
            f'<caption style="text-align:left;font-size:14px;color:{COR["suave"]};padding-bottom:8px">Mediana das projeções · Focus {_esc(resumo.get("data_focus"))}</caption>'
            f'<thead><tr>{cab}</tr></thead><tbody>{"".join(linhas)}</tbody></table>'
            f'<p style="font-size:14px;color:{COR["suave"]};margin:12px 0 0">▲ alta · ▼ queda · = estável. '
            'Entre parênteses: semanas seguidas na mesma direção. Resp.: respondentes. —: dado indisponível.</p>')


def _historico(resumo, saida):
    acc = resumo.get('acuracia') or []
    if not acc:
        return '<p>Histórico indisponível nesta execução.</p>'
    img = _imagem(saida / 'acuracia.png', 'Esperado × realizado de IPCA e Selic') if saida else ''
    style = f'padding:10px 2px;text-align:right;font-size:14px;border-bottom:1px solid {COR["borda"]};font-variant-numeric:tabular-nums'
    linhas = ''.join('<tr>' + ''.join(f'<td style="{style}">{v}</td>' for v in
        (_esc(a.get('indicador')), _esc(a.get('ano')), _num(a.get('esperado')), _num(a.get('realizado')), _num(a.get('erro_pp'),True))) + '</tr>' for a in acc)
    cab = ''.join(f'<th scope="col" width="{largura}%" style="{style};font-weight:normal;overflow-wrap:break-word;color:{COR["suave"]}">{v}</th>'
                  for largura, v in zip((15, 15, 23, 23, 24), ('Série','Ano','Espe&shy;rado','Reali&shy;zado','Erro (p.p.)')))
    return (img + f'<table width="100%" cellspacing="0" cellpadding="0" style="table-layout:fixed;border-collapse:collapse;background:#ffffff;margin-top:16px">'
            f'<thead><tr>{cab}</tr></thead><tbody>{linhas}</tbody></table>'
            f'<p style="font-size:14px;color:{COR["suave"]};margin:12px 0 0">Expectativa: {_esc(acc[0].get("quando"))}. '
            'Erro positivo: realizado acima do esperado. IPCA composto mês a mês; Selic meta no fim do ano.</p>')


def montar(resumo: dict, analise: str, saida: Path | None = None) -> str:
    data = _esc(resumo.get('data_focus'))
    n_alertas = len(resumo.get('alertas') or [])
    corpo = ''.join([
        _termometro(resumo),
        _secao('Alertas da semana', _alertas(resumo), 'O QUE MUDOU'),
        _secao('Análise da semana', f'<div style="font-size:16px;line-height:1.6;color:{COR["texto"]};background:#ffffff">{analise}</div>', 'LEITURA DA SEMANA'),
        _secao('Números da semana', _tabela_semana(resumo), 'EM NÚMEROS'),
        _secao('O Focus acertou?', _historico(resumo, saida), 'EXPECTATIVA × REALIZADO')])
    motor = _esc(MOTORES.get(resumo.get('motor_analise'), resumo.get('motor_analise') or 'motor não informado'))
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Termômetro do Focus — {data}</title></head>
<body style="margin:0;padding:0;background:{COR['fundo']};font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.5;color:{COR['texto']}">
<div aria-hidden="true" style="display:none;max-height:0;max-width:0;overflow:hidden;opacity:0;mso-hide:all;font-size:1px;line-height:1px;color:#ffffff;background:#ffffff">Focus de {data} · {n_alertas} alerta(s) nesta semana.</div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" bgcolor="{COR['fundo']}" style="background:{COR['fundo']}"><tr><td align="center" style="padding:16px 4px">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" style="max-width:640px;background:#ffffff;border:1px solid {COR['borda']}">
<tr><td bgcolor="#ffffff" style="padding:28px 16px;background:#ffffff;border-top:6px solid {COR['marca']};color:{COR['texto']}">
<table role="presentation" cellspacing="0" cellpadding="0" style="margin:0 0 18px;background:#ffffff"><tr>
<td width="40" height="40" align="center" bgcolor="{COR['marca']}" aria-hidden="true" style="width:40px;height:40px;background:{COR['marca']};color:#ffffff;font-family:Georgia,serif;font-size:24px;line-height:40px">TF</td>
<td style="padding-left:10px;background:#ffffff;color:{COR['marca']}"><h1 style="margin:0;font-family:Georgia,serif;font-size:22px;font-weight:normal;letter-spacing:1px">Termômetro do Focus</h1><span style="font-size:11px;letter-spacing:1px">RELATÓRIO SEMANAL · CLAUDE LAB PUC-RIO</span></td>
</tr></table>
<p style="margin:0;font-size:16px;color:{COR['marca']};font-weight:bold">Relatório Focus de {data}</p>
<p style="margin:6px 0 0;font-size:14px;color:{COR['suave']}">Gerado em {_esc(resumo.get('gerado_em'))} · Banco Central do Brasil</p>
</td></tr>{corpo}
<tr><td bgcolor="#ffffff" style="padding:24px 16px;background:#ffffff;border-top:3px solid {COR['marca']};font-size:14px;line-height:1.6;color:{COR['suave']}">
<p style="margin:0 0 8px">Fonte: Banco Central do Brasil · Focus de {data} (Olinda) e SGS.</p>
<p style="margin:0 0 8px">Metodologia: medianas do Focus; IPCA composto; Selic de fim de ano.</p>
<p style="margin:0 0 8px">Análise escrita por {motor}. Conferência numérica automática; sujeita às limitações do método.</p>
<p style="margin:0;color:{COR['texto']}">Não constitui recomendação de investimento.</p>
</td></tr></table></td></tr></table></body></html>'''
