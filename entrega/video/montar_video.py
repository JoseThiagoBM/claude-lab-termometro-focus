"""Monta o vídeo do Termômetro do Focus a partir de prints reais, saídas reais do terminal e narração TTS (pt-BR)."""
import re
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

V = Path(__file__).resolve().parent
REPO = Path(r"C:\Users\joseb\Documents\Hackathon-PUC-Rio\time-case1")
OUT = REPO / "docs" / "video.mp4"
W, H, FPS = 1280, 720, 30
RATE = int(sys.argv[1]) if len(sys.argv) > 1 else 1
F = r"C:\Windows\Fonts"
fonte = lambda n, s: ImageFont.truetype(f"{F}\\{n}", s)
SANS, BOLD, MONO = "segoeui.ttf", "segoeuib.ttf", "consola.ttf"
AZUL, FUNDO, CLARO = (11, 92, 122), (16, 24, 32), (235, 240, 245)

# ---------------------------------------------------------------- narração do roteiro
narr = []
for l in (REPO / "entrega" / "ROTEIRO_VIDEO.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r'\| \*\*\d:\d\d–\d:\d\d\*\* \|[^|]*\| "(.*?)" \|', l)
    if m:
        narr.append(m.group(1))
assert len(narr) == 8, narr


def tts(texto: str, destino: Path) -> float:
    t = destino.with_suffix(".txt")
    t.write_text(texto, encoding="utf-8")
    ps = ("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
          "$s.SelectVoice('Microsoft Maria Desktop'); $s.Rate=%d; "
          "$f=New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(22050,[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,[System.Speech.AudioFormat.AudioChannel]::Mono); "
          "$s.SetOutputToWaveFile('%s',$f); $s.Speak([IO.File]::ReadAllText('%s',[Text.Encoding]::UTF8)); $s.Dispose()"
          % (RATE, destino, t))
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    with wave.open(str(destino)) as w:
        return w.getnframes() / w.getframerate()


# ---------------------------------------------------------------- telas
def base(cor=FUNDO):
    return Image.new("RGB", (W, H), cor)


def legenda(img, texto, sub=None):
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 96, W, H], fill=(10, 14, 20))
    d.rectangle([0, H - 96, 8, H], fill=(201, 162, 39))
    d.text((32, H - 84), texto, font=fonte(BOLD, 30), fill=CLARO)
    if sub:
        d.text((32, H - 40), sub, font=fonte(SANS, 22), fill=(170, 185, 200))
    return img


def recorte(arq, caixa, fundo=(244, 246, 248)):
    im = Image.open(V / arq).convert("RGB").crop(caixa)
    area_w, area_h = W - 80, H - 96 - 40
    esc = min(area_w / im.width, area_h / im.height)
    im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    tela = base(fundo)
    tela.paste(im, ((W - im.width) // 2, 20 + (area_h - im.height) // 2))
    return tela


def terminal(linhas, destaque=None):
    tela = base((12, 12, 12))
    d = ImageDraw.Draw(tela)
    d.rectangle([0, 0, W, 34], fill=(40, 40, 40))
    d.text((16, 6), "Windows PowerShell · time-case1", font=fonte(SANS, 18), fill=(200, 200, 200))
    y = 56
    for l in linhas:
        cor = (120, 220, 140) if l.startswith("PS ") else (255, 120, 90) if destaque and destaque in l else (225, 225, 225)
        d.text((24, y), l, font=fonte(MONO, 24), fill=cor)
        y += 34
    return tela


def slide(titulo, linhas, rodape=None):
    tela = base((247, 248, 250))
    d = ImageDraw.Draw(tela)
    d.rectangle([0, 0, W, 10], fill=AZUL)
    d.text((70, 70), titulo, font=fonte(BOLD, 46), fill=AZUL)
    y = 170
    for l, tam, cor in linhas:
        d.text((70, y), l, font=fonte(BOLD if tam > 30 else SANS, tam), fill=cor)
        y += tam + 26
    if rodape:
        d.text((70, H - 150), rodape, font=fonte(SANS, 22), fill=(90, 100, 110))
    return tela


def curto(caminho: str) -> str:
    return caminho.replace(r"C:\Users\joseb\Documents\Hackathon-PUC-Rio\time-case1", "...")


ag = [curto(l.rstrip()) for l in (V / "term_agente.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
ag = [l for l in ag if not l.startswith(("Focus ", "SGS ", "Pronto."))][-11:]
sab = [curto(l.rstrip()) for l in (V / "term_sabotagem.txt").read_text(encoding="utf-8").splitlines() if l.strip()]

ESCURO = (16, 22, 28)
cenas = [
    [(legenda(recorte("pages.png", (180, 0, 1100, 760), ESCURO), "Termômetro do Focus · Claude Lab PUC-Rio · 06/11/2026",
              "Página pública: josethiagobm.github.io/claude-lab-termometro-focus"), 1)],
    [(legenda(slide("Equipe", [
        ("Thomas Shu Chung · Economia · alertas e checagens", 30, (30, 40, 50)),
        ("Thiago Signorini Leal · Economia · histórico de acerto", 30, (30, 40, 50)),
        ("Theo Monteiro Dorr Abreu · Economia · análise do Claude", 30, (30, 40, 50)),
        ("José Thiago Bevilaqua Monteiro · Eng. de Produção · relatório e e-mail", 30, (30, 40, 50)),
        ("Validação independente: Codex", 24, (90, 100, 110))]), "Construído com Claude Code + Python",
        "Código: github.com/JoseThiagoBM/claude-lab-termometro-focus"), 1)],
    [(legenda(terminal(["PS> python agente_semanal.py --sem-download --sem-email", ""] + ag),
              "baixar → calcular → verificar → analisar → conferir → enviar",
              "Saída real do terminal · envio real pelo Gmail testado às 14h57"), 1)],
    [(legenda(recorte("email.png", (0, 0, 900, 760)), "Observado × esperado: Selic hoje 13,75% · fim do ano 13,50%",
              "E-mail real gerado pelo agente (Focus de 30/10/2026)"), 0.45),
     (legenda(recorte("email.png", (0, 736, 900, 1220)), "IPCA 2027: +0,46 p.p. em 4 semanas · rara (percentil 96)",
              "Alerta = mudança maior que 2 desvios-padrão das mudanças desde 2021"), 0.55)],
    [(legenda(recorte("email.png", (0, 2553, 900, 2967)), "Erro médio do IPCA: 1,97 p.p. em janeiro → 1,53 p.p. em julho",
              "De 2021 a 2025, o mercado subestimou a inflação (+1,35 p.p. em média)"), 1)],
    [(legenda(terminal(["PS> # teste: IPCA trocado para 52,2 só na memória", "PS> python - < sabotagem.py", ""] + sab,
                       destaque="PAROU"), "PAROU: IPCA 2026 = 52.2 fora da faixa plausível",
              "Com dado errado, o agente não envia o relatório e avisa o time"), 1)],
    [(legenda(slide("Como conferimos", [
        ("126 de 126 valores iguais", 44, AZUL),
        ("0 divergências · 32 conferidos no PDF oficial do Focus", 30, (30, 40, 50)),
        ("Recálculo independente, direto dos dados do Banco Central,", 24, (90, 100, 110)),
        ("com código que não usa o código do projeto (validacao/recalcular.py)", 24, (90, 100, 110))]),
        "126/126 · 0 divergências · 32 no PDF oficial", "Fonte: validacao/saida_recalculo.txt"), 1)],
    [(legenda(recorte("pages.png", (180, 1081, 1100, 1512), ESCURO), "Para gestores, economistas e analistas · agendado: segunda, 10h",
              "josethiagobm.github.io/claude-lab-termometro-focus · Não constitui recomendação de investimento"), 1)],
]

# ---------------------------------------------------------------- áudio
audios, duracoes = [], []
for i, texto in enumerate(narr):
    w = V / f"cena{i + 1}.wav"
    duracoes.append(tts(texto, w) + 0.35)
    audios.append(w)
print("duração por cena:", [round(d, 1) for d in duracoes], "total:", round(sum(duracoes), 1), "s")

with wave.open(str(audios[0])) as w0:
    params = w0.getparams()
with wave.open(str(V / "narracao.wav"), "wb") as out:
    out.setparams(params)
    for a, dur in zip(audios, duracoes):
        with wave.open(str(a)) as w:
            dados = w.readframes(w.getnframes())
        out.writeframes(dados)
        falta = int(round(dur * params.framerate)) - len(dados) // params.sampwidth
        out.writeframes(b"\x00\x00" * max(falta, 0))

# ---------------------------------------------------------------- vídeo
mudo = V / "mudo.mp4"
gen = imageio_ffmpeg.write_frames(str(mudo), (W, H), fps=FPS, codec="libx264", pix_fmt_out="yuv420p",
                                  output_params=["-crf", "23", "-preset", "veryfast"])
gen.send(None)
for cena, dur in zip(cenas, duracoes):
    for img, frac in cena:
        quadro = np.asarray(img, dtype=np.uint8).tobytes()
        for _ in range(int(round(dur * frac * FPS))):
            gen.send(quadro)
gen.close()

OUT.parent.mkdir(exist_ok=True)
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(mudo), "-i", str(V / "narracao.wav"),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(OUT)], check=True)
for i, (cena, dur) in enumerate(zip(cenas, duracoes)):
    cena[0][0].save(V / f"previa{i + 1}.png")
print("vídeo:", OUT, round(OUT.stat().st_size / 1e6, 1), "MB")
