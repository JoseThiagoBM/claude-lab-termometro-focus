"""
Etapa 6 do agente: MONTAR o relatório em HTML (é o corpo do e-mail e o artefato web).
Dono: Pessoa C. Entrada: `resumo` (CONTRATO.md) + HTML da análise. Saída: HTML completo.
"""


def montar(resumo: dict, analise: str) -> str:
    linhas = "".join(
        f"<tr><td>{l['indicador']}</td><td>{l['ano']}</td><td>{l['mediana']:.2f}</td>"
        f"<td>{l['var_semana']:+.2f}</td><td>{l['var_4_semanas']:+.2f}</td></tr>"
        for l in resumo["indicadores"])
    # TODO: deixem o e-mail com a cara do time (cores, gráfico do histórico de acerto, ordem das seções).
    return f"""<html><body style="font-family:Arial,sans-serif;max-width:680px;margin:auto">
<h2>Termômetro do Focus — {resumo['data_focus']}</h2>
{analise}
<h3>Números da semana (mediana)</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse">
<tr><th>Indicador</th><th>Ano</th><th>Mediana</th><th>Var. semana</th><th>Var. 4 semanas</th></tr>
{linhas}</table>
<p style="font-size:12px;color:#666">Fonte: Banco Central do Brasil, Relatório Focus de {resumo['data_focus']}.
Análise gerada automaticamente com o Claude e conferida contra os dados. Não constitui recomendação de investimento.</p>
</body></html>"""
