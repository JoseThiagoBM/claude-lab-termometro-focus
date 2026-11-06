"""Sondas da Frente C, separadas do recálculo independente dos CSVs."""
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('analise_auditada', root/'avancado/case1_focus/analise.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
summary = json.loads((root/'avancado/case1_focus/saida/resumo_semana.json').read_text(encoding='utf-8'))
evidence = json.loads((root/'validacao/evidencias.json').read_text(encoding='utf-8'))
for probe in evidence['sondas_texto']:
    suspicious = module.conferir(probe['texto'],summary)
    assert (not suspicious) == probe['aceito_regra_atual']
    print(json.dumps(dict(**probe,suspeitos=suspicious),ensure_ascii=False))
