"""Auditoria independente: apenas biblioteca padrão, CSVs e JSON; nenhuma IA/rede."""
import csv
import hashlib
import json
import math
import re
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validacao'

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    paths = [ROOT/'data/case1_focus/focus_anuais.csv', ROOT/'data/case1_focus/sgs_realizado.csv', ROOT/'avancado/case1_focus/saida/resumo_semana.json']
    summary = read_json(paths[2])
    cutoff = datetime.strptime(summary['sexta_referencia'], '%d/%m/%Y').date()
    assert cutoff.weekday() == 4
    assert summary['data_focus'] == summary['sexta_referencia']
    groups = defaultdict(dict)
    duplicates = 0
    with paths[0].open(encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            if float(r['baseCalculo']) != 0:
                continue
            d = date.fromisoformat(r['Data'])
            if d > cutoff:
                continue
            key = (r['Indicador'], int(r['DataReferencia']))
            duplicates += d in groups[key]
            groups[key][d] = {k: float(r[k]) for k in ('Mediana', 'DesvioPadrao', 'numeroRespondentes')}
    assert not duplicates, f'{duplicates} duplicatas base 0'
    weekly = {}
    for key, observations in groups.items():
        weeks = {}
        for d, r in sorted(observations.items()):
            friday = d + timedelta(days=(4-d.weekday()) % 7)
            weeks[friday] = r
        weekly[key] = weeks
    sgs = defaultdict(dict)
    with paths[1].open(encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            sgs[r['serie']][date.fromisoformat(r['data'])] = float(r['valor'])
    golden = read_json(OUT/'gabarito_focus_2026-10-30.json')
    gold = {(r['indicador'], r['ano']): r for r in golden['indicadores']}
    rows = []
    def compare(ind, year, field, actual, calculated, external=None):
        def close(a,b):
            return a is not None and b is not None and math.isfinite(float(a)) and math.isfinite(float(b)) and abs(Decimal(str(a))-Decimal(str(b))) <= Decimal('0.01')
        ok = close(actual, calculated) and (external is None or (close(actual,external) and close(calculated,external)))
        rows.append((ind, year, field, actual, calculated, external, 'SIM' if ok else 'NAO'))
    def sigma(ind, horizon, lag):
        changes = []
        for (name, target), weeks in weekly.items():
            if name != ind:
                continue
            for d, r in weeks.items():
                prev = d-timedelta(weeks=lag)
                if d.year == target-horizon and d >= date(2021,1,1) and d >= date(target-horizon,1,1)+timedelta(weeks=lag) and prev in weeks:
                    changes.append(r['Mediana']-weeks[prev]['Mediana'])
        return statistics.stdev(changes), len(changes)
    sensitivity = []
    for item in summary['indicadores']:
        ind, year = item['indicador'], item['ano']
        weeks = weekly[ind,year]
        selected = [weeks[cutoff-timedelta(weeks=n)] for n in (0,1,4)]
        med, ant, old = [round(r['Mediana'],2) for r in selected]
        calculated = dict(mediana=med, mediana_semana_anterior=ant, mediana_4_semanas_atras=old, var_semana=round(med-ant,2), var_4_semanas=round(med-old,2), respondentes=int(selected[0]['numeroRespondentes']), desvio_padrao=round(selected[0]['DesvioPadrao'],2), desvio_padrao_semana_anterior=round(selected[1]['DesvioPadrao'],2), desvio_padrao_4_semanas_atras=round(selected[2]['DesvioPadrao'],2))
        sd1,n1 = sigma(ind,year-cutoff.year,1)
        sd4,n4 = sigma(ind,year-cutoff.year,4)
        calculated.update(limiar_semana=round(2*sd1,2),limiar_4s=round(2*sd4,2),desvios_4s=round((med-old)/sd4,1))
        for field,value in calculated.items():
            external = gold.get((ind,year),{}).get(field) if golden['fonte_acessada'] and golden['data_focus'] == summary['data_focus'] else None
            compare(ind,year,field,item.get(field),value,external)
        sensitivity.append(dict(indicador=ind,ano=year,sigma_semana=sd1,sigma_4s=sd4,n_semana=n1,n_4s=n4,**{str(k):abs(med-old)>k*sd4 or abs(med-ant)>k*sd1 for k in (1.5,2,2.5)}))
    history = []
    for item in summary['acuracia']:
        ind,year = item['indicador'],item['ano']
        observations = groups[ind,year]
        expected = observations[max(d for d in observations if d<=date(year,1,15))]['Mediana']
        july = observations[max(d for d in observations if d<=date(year,7,15))]['Mediana']
        if ind == 'IPCA':
            months = [(d,v) for d,v in sgs['ipca_mensal'].items() if d.year==year]
            assert len(months)==12 and len({d.month for d,v in months})==12
            realized = (math.prod(1+v/100 for d,v in months)-1)*100
        elif ind == 'Selic':
            d = max(d for d in sgs['selic_meta'] if d.year==year and d.month==12)
            realized = sgs['selic_meta'][d]
        else:
            raise ValueError(ind)
        for field,value in dict(esperado=expected,realizado=realized,erro_pp=realized-expected).items():
            compare(ind,year,field,item.get(field),round(value,2))
        history.append(dict(indicador=ind,ano=year,janeiro=expected,julho=july,realizado=realized,erro_janeiro=realized-expected,erro_julho=realized-july))
    metrics = {}
    for ind in ('IPCA','Selic'):
        h = [r for r in history if r['indicador']==ind]
        metrics[ind] = {m:{'erro_medio':statistics.mean(r['erro_'+m] for r in h),'erro_absoluto_medio':statistics.mean(abs(r['erro_'+m]) for r in h)} for m in ('janeiro','julho')}
    # Replica independente da regra textual observada; não importa a implementação.
    allowed = set()
    for token in re.findall(r'-?\d+(?:[.,]\d+)?',json.dumps(summary)):
        v = float(token.replace(',','.'))
        allowed.update((round(v,2),round(abs(v),2)))
    probe = [dict(texto=f'IPCA 2026 = {summary["indicadores"][2]["mediana"]:.2f}',correto=False),dict(texto='IPCA 2026 = 999%',correto=False),dict(texto='PIB Total 2027 variou +0,11',correto=False),dict(texto='IPCA 2026 = 5,22',correto=True)]
    for p in probe:
        tokens = re.findall(r'\d+,\d+|\d+\.\d+',p['texto'])
        p['aceito_regra_atual'] = all(round(float(t.replace(',','.')),2) in allowed for t in tokens)
    result = dict(conferidos=len(rows),bateram=sum(r[-1]=='SIM' for r in rows),divergencias=[r for r in rows if r[-1]!='SIM'],comparacoes_pdf=sum(r[5] is not None for r in rows),alertas=sensitivity,contagem_alertas={str(k):sum(r[str(k)] for r in sensitivity) for k in (1.5,2,2.5)},historico=history,metricas_historico=metrics,sondas_texto=probe,sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (OUT/'evidencias.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('indicador | ano | campo | resumo | recalculado | gabarito | bate?')
    for row in rows:
        print(' | '.join('-' if x is None else str(x) for x in row))
    print(f"TOTAL: {result['conferidos']} campos; {result['bateram']} batem; {len(result['divergencias'])} divergem; {result['comparacoes_pdf']} tambem conferidos no PDF")
    return int(bool(result['divergencias']))

if __name__ == '__main__':
    raise SystemExit(main())
