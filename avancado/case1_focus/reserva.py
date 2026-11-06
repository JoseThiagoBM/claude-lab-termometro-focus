"""
Motores de análise de reserva, para quando o Claude não responder (limite do plano, fora do ar, sem login).
Dono: integração. Não substitui o analise.py (Frente C): o agente tenta os motores em ordem.

    MOTOR_ANALISE=claude,codex,sem_ia   (padrão: tenta nesta ordem)
    MOTOR_ANALISE=codex                 (só o Codex)
    MOTOR_ANALISE=sem_ia                (texto só com os números do JSON; nunca falha na conferência)

Todo motor tem a mesma forma: gerar(resumo, instrucao_extra="") -> HTML com <h3>, <p>, <ul>, <li>, <strong>.
`instrucao_extra` é o que a reescrita (Frente C) manda quando a conferência acusa número fora do JSON.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORDEM_PADRAO = "claude,codex,sem_ia"
NOMES = {"claude": "Claude (claude -p)", "codex": "Codex (codex exec)", "sem_ia": "texto automático, sem IA"}


def _limpar(texto: str) -> str:
    return texto.strip().removeprefix("```html").removeprefix("```").removesuffix("```").strip()


# ------------------------------------------------------------------ Codex
def gerar_codex(resumo: dict, instrucao_extra: str = "") -> str:
    """Mesmo prompt da análise, pelo Codex CLI em modo não interativo e somente leitura.
    --ignore-user-config: ignora o config.toml pessoal (modelo e MCPs dele podem não valer aqui);
    o login do Codex fica em outro arquivo e continua valendo."""
    codex = shutil.which("codex")
    if not codex:
        raise RuntimeError("Codex CLI não encontrado (instale e faça login com `codex login`).")
    prompt = (AQUI / "prompt_analise.md").read_text(encoding="utf-8")
    entrada = prompt + "\n" + json.dumps(resumo, ensure_ascii=False, indent=2)
    if instrucao_extra:
        entrada += "\n\n" + instrucao_extra
    with tempfile.TemporaryDirectory() as tmp:
        saida = Path(tmp) / "resposta.txt"
        r = subprocess.run([codex, "exec", "--ignore-user-config", "--skip-git-repo-check", "--ephemeral",
                            "-s", "read-only", "--color", "never", "-C", tmp, "-o", str(saida), "-"],
                           input=entrada, capture_output=True, text=True, encoding="utf-8", timeout=300)
        if r.returncode != 0 or not saida.exists():
            raise RuntimeError(f"Codex falhou (código {r.returncode}): {r.stderr.strip()[-300:]}")
        return _limpar(saida.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ sem IA
def _n(v, sinal: bool = False) -> str:
    return (f"{v:+.2f}" if sinal else f"{v:.2f}").replace(".", ",")


def texto_sem_ia(resumo: dict, instrucao_extra: str = "") -> str:
    """Análise montada só com o JSON. Usada quando nenhuma IA responde: o relatório sai mesmo assim."""
    inds = resumo.get("indicadores", [])
    alertas = resumo.get("alertas", [])
    principal = (f"{len(alertas)} alerta(s) no Focus de {resumo['data_focus']}" if alertas
                 else f"Focus de {resumo['data_focus']}: semana sem variações fora do normal")
    itens = [f"<li><strong>Alerta:</strong> {a}</li>" for a in alertas]
    for l in inds:
        itens.append(f"<li><strong>{l['indicador']} {l['ano']}:</strong> mediana {_n(l['mediana'])}, "
                     f"{_n(l['var_semana'], True)} na semana e {_n(l['var_4_semanas'], True)} em 4 semanas.</li>")
    t = resumo.get("termometro") or {}
    extra = ""
    if "selic_hoje" in t and "selic_esperada_fim_do_ano" in t:
        extra = (f"<p>A Selic está em {_n(t['selic_hoje'])}% e o mercado espera "
                 f"{_n(t['selic_esperada_fim_do_ano'])}% no fim do ano.</p>")
    return (f"<h3>{principal}</h3><ul>{''.join(itens)}</ul>{extra}"
            f"<p><strong>Atenção:</strong> nesta semana a análise foi gerada automaticamente, sem IA, "
            f"só com os números calculados.</p>")


def motores(ordem: str | None = None) -> list[tuple[str, object]]:
    """Lista (nome, gerar) na ordem de MOTOR_ANALISE."""
    from analise import analisar  # Frente C
    disponiveis = {"claude": analisar, "codex": gerar_codex, "sem_ia": texto_sem_ia}
    nomes = [m.strip() for m in (ordem or os.environ.get("MOTOR_ANALISE") or ORDEM_PADRAO).split(",") if m.strip()]
    desconhecidos = [m for m in nomes if m not in disponiveis]
    if desconhecidos:
        raise SystemExit(f"MOTOR_ANALISE com motor desconhecido: {', '.join(desconhecidos)}")
    return [(m, disponiveis[m]) for m in nomes]
