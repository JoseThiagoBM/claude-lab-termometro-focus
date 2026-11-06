"""
Case 1 — Termômetro do Focus · o AGENTE SEMANAL (orquestrador).

Rode da raiz do repositório:
    python avancado/case1_focus/agente_semanal.py                 # fluxo completo
    python avancado/case1_focus/agente_semanal.py --sem-email     # gera o relatório, mas não envia
    python avancado/case1_focus/agente_semanal.py --sem-download  # usa os CSVs que já estão em data/

As etapas e quem cuida de cada uma (formato dos dados em CONTRATO.md):
  1. baixar    — scripts/baixar_dados_bcb.py
  2. calcular  — termometro.py  (Pessoa A)
  2b. histórico — historico.py  (Pessoa B): expectativa × realizado, 5 anos fechados, com gráfico
  3. checar    — termometro.py  (Pessoa A): se algo estiver errado, o agente PARA e avisa o time
  4. analisar  — analise.py     (Pessoa C): o Claude escreve via `claude -p`
  5. conferir  — analise.py     (Pessoa C): todo número do texto precisa existir no JSON
  6. montar    — relatorio.py   (Pessoa D): saida/relatorio_semana.html (também é o artefato web)
  7. enviar    — enviar_email.py (Pessoa D): Gmail + .env
"""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SAIDA = AQUI / "saida"
sys.path.insert(0, str(AQUI))

from analise import analisar, conferir  # noqa: E402
from historico import historico  # noqa: E402
from relatorio import montar  # noqa: E402
from termometro import calcular, checar  # noqa: E402


def baixar() -> None:
    subprocess.run([sys.executable, str(RAIZ / "scripts" / "baixar_dados_bcb.py")], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sem-download", action="store_true")
    ap.add_argument("--sem-email", action="store_true")
    args = ap.parse_args()
    SAIDA.mkdir(exist_ok=True)

    if not args.sem_download:
        print("1. Baixando dados..."); baixar()
    print("2. Calculando o termômetro..."); resumo = calcular()
    print("   + histórico de acerto..."); resumo["acuracia"] = historico(SAIDA)
    (SAIDA / "resumo_semana.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")

    print("3. Checando..."); problemas = checar(resumo)
    if problemas:
        aviso = "<p>O agente parou. Problemas encontrados:</p><ul>" + \
                "".join(f"<li>{html.escape(p)}</li>" for p in problemas) + "</ul>"
        print("   PAROU:", "; ".join(problemas))
        if not args.sem_email:
            from enviar_email import enviar
            enviar("[ALERTA] Agente do Focus parou", aviso)
        sys.exit(1)

    print("4. Pedindo a análise ao Claude..."); analise = analisar(resumo)
    print("5. Conferindo números do texto...")
    suspeitos = conferir(analise, resumo)
    if suspeitos:
        print("   ATENÇÃO: números no texto que não estão no JSON:", ", ".join(suspeitos))

    print("6. Montando o relatório...")
    relatorio = montar(resumo, analise)
    destino = SAIDA / "relatorio_semana.html"
    destino.write_text(relatorio, encoding="utf-8")
    print("   salvo em", destino)

    if not args.sem_email:
        from enviar_email import enviar
        para = enviar(f"Termômetro do Focus — {resumo['data_focus']}", relatorio)
        print("7. E-mail enviado para", ", ".join(para))


if __name__ == "__main__":
    main()
