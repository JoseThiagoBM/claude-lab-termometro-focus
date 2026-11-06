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
CAMPOS_INTERNOS = {"integridade"}  # ficam no JSON, mas não vão para a análise do Claude
sys.path.insert(0, str(AQUI))

from analise import analisar_conferido  # noqa: E402
from historico import historico  # noqa: E402
from relatorio import montar  # noqa: E402
from termometro import calcular, checar  # noqa: E402


def baixar() -> None:
    subprocess.run([sys.executable, str(RAIZ / "scripts" / "baixar_dados_bcb.py")], check=True)


def parar(problemas: list[str], com_email: bool) -> None:
    """Não manda o relatório: avisa o time e sai com código 1."""
    aviso = "<p>O agente parou. Problemas encontrados:</p><ul>" + \
            "".join(f"<li>{html.escape(p)}</li>" for p in problemas) + "</ul>"
    print("   PAROU:", "; ".join(problemas))
    if com_email:
        from enviar_email import enviar
        enviar("[ALERTA] Agente do Focus parou", aviso)
    sys.exit(1)


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
        parar(problemas, not args.sem_email)

    print("4-5. Pedindo a análise ao Claude e conferindo os números...")
    # o bloco `integridade` é insumo interno do checar(): o Claude não o recebe, e o conferir()
    # não aceita números dele (CONTRATO.md)
    para_o_claude = {k: v for k, v in resumo.items() if k not in CAMPOS_INTERNOS}
    analise, suspeitos = analisar_conferido(para_o_claude)
    if suspeitos:
        parar([f"a análise citou números que não estão nos dados: {', '.join(suspeitos)}"], not args.sem_email)

    print("6. Montando o relatório...")
    relatorio = montar(resumo, analise, SAIDA)
    destino = SAIDA / "relatorio_semana.html"
    destino.write_text(relatorio, encoding="utf-8")
    print("   salvo em", destino)

    if not args.sem_email:
        from enviar_email import enviar
        # o gráfico já vai em base64 dentro do relatório; o enviar() o converte em Content-ID
        para = enviar(f"Termômetro do Focus — {resumo['data_focus']}", relatorio)
        print("7. E-mail enviado para", ", ".join(para))


if __name__ == "__main__":
    main()
