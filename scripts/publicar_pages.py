"""
Publica a versão web do relatório no GitHub Pages (artefato público, sem login).

    python avancado/case1_focus/agente_semanal.py --sem-email   # gera saida/relatorio_web.html
    python scripts/publicar_pages.py                             # copia para docs/index.html
    git add docs && git commit -m "Relatório da semana" && git push

O GitHub Pages serve a pasta docs/ da branch main em:
    https://josethiagobm.github.io/claude-lab-termometro-focus/

A página do web.py não traz <html>/<head> (o claude.ai acrescenta ao publicar); aqui o script
acrescenta o esqueleto com charset e viewport, para o navegador abrir igual em qualquer lugar.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "avancado" / "case1_focus" / "saida" / "relatorio_web.html"
DESTINO = RAIZ / "docs" / "index.html"

ESQUELETO = ('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
             '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
             '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
             'img{max-width:100%}[hidden]{display:none!important}</style>\n')


def publicar() -> Path:
    if not ORIGEM.exists():
        raise SystemExit(f"{ORIGEM} não existe. Rode o agente antes (agente_semanal.py).")
    pagina = ORIGEM.read_text(encoding="utf-8")
    cabeca, _, corpo = pagina.partition("<main>")
    DESTINO.parent.mkdir(exist_ok=True)
    DESTINO.write_text(f"{ESQUELETO}{cabeca}</head>\n<body>\n<main>{corpo}</body>\n</html>\n", encoding="utf-8")
    (DESTINO.parent / ".nojekyll").write_text("", encoding="utf-8")  # serve o HTML como está, sem Jekyll
    return DESTINO


if __name__ == "__main__":
    print("Página publicada em", publicar())
