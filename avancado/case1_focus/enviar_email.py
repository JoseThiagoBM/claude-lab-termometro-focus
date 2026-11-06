"""
Case 1 — Envio do e-mail semanal pelo Gmail. Dono: Frente D.

Lê as credenciais de avancado/case1_focus/.env (copie .env.exemplo para .env e preencha à mão).
O .env NUNCA vai para o GitHub: o .gitignore já o ignora.

Assinatura fixa: enviar(assunto, html, imagens=None) -> destinatários.
- Imagens em base64 dentro do HTML (como o relatorio.py gera) viram anexos com Content-ID,
  porque o Gmail não mostra <img src="data:...">.
- `imagens` são PNGs extras para embutir; ficam no fim do corpo.

Teste sozinho:
    python avancado/case1_focus/enviar_email.py
"""
import base64
import re
import smtplib
import ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ENV = Path(__file__).resolve().parent / ".env"
DATA_URI = re.compile(r'src="data:image/(png|jpeg|gif);base64,([A-Za-z0-9+/=]+)"')


def ler_env(caminho: Path = ENV) -> dict:
    if not caminho.exists():
        raise SystemExit(f"Arquivo {caminho} não encontrado. Copie .env.exemplo para .env e preencha.")
    cfg = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            chave, valor = linha.split("=", 1)
            cfg[chave.strip()] = valor.strip().strip('"').strip("'")
    for chave in ("GMAIL_USUARIO", "GMAIL_SENHA_DE_APP", "DESTINATARIOS"):
        if not cfg.get(chave):
            raise SystemExit(f"Falta {chave} no .env")
    return cfg


def preparar_mensagem(assunto: str, html: str, remetente: str, destinatarios: list[str],
                      imagens: list[Path] | None = None) -> MIMEMultipart:
    """Monta o e-mail sem enviar (testável sem rede): HTML + imagens embutidas por Content-ID."""
    anexos: list[tuple[str, bytes, str]] = []

    def trocar(m: re.Match) -> str:
        cid = f"img{len(anexos) + 1}"
        anexos.append((cid, base64.b64decode(m.group(2)), m.group(1)))
        return f'src="cid:{cid}"'

    html = DATA_URI.sub(trocar, html)
    for caminho in imagens or []:
        cid = f"img{len(anexos) + 1}"
        anexos.append((cid, Path(caminho).read_bytes(), "png"))
        html = html.replace("</body>", f'<p><img src="cid:{cid}" alt="{Path(caminho).stem}" width="640"></p></body>')

    msg = MIMEMultipart("related")
    msg["Subject"], msg["From"], msg["To"] = assunto, remetente, ", ".join(destinatarios)
    alternativa = MIMEMultipart("alternative")
    alternativa.attach(MIMEText("Este e-mail precisa de um leitor com suporte a HTML.", "plain", "utf-8"))
    alternativa.attach(MIMEText(html, "html", "utf-8"))
    msg.attach(alternativa)
    for cid, dados, subtipo in anexos:
        img = MIMEImage(dados, _subtype=subtipo)
        img.add_header("Content-ID", f"<{cid}>")
        img.add_header("Content-Disposition", "inline", filename=f"{cid}.{subtipo}")
        msg.attach(img)
    return msg


def enviar(assunto: str, html: str, imagens: list[Path] | None = None) -> list[str]:
    cfg = ler_env()
    destinatarios = [d.strip() for d in cfg["DESTINATARIOS"].split(",") if d.strip()]
    msg = preparar_mensagem(assunto, html, cfg["GMAIL_USUARIO"], destinatarios, imagens)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(cfg["GMAIL_USUARIO"], cfg["GMAIL_SENHA_DE_APP"].replace(" ", ""))
        s.sendmail(cfg["GMAIL_USUARIO"], destinatarios, msg.as_string())
    return destinatarios


if __name__ == "__main__":
    para = enviar("Teste do agente do Focus", "<p>Se você recebeu isto, o envio está funcionando.</p>")
    print("E-mail de teste enviado para", ", ".join(para))
