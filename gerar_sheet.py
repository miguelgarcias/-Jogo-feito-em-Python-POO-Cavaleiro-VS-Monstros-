from PIL import Image  # pip install pillow

TAM = 64
base = Image.open("sprites/player_direita.png").convert("RGBA")
base.thumbnail((TAM, TAM))  # reduz mantendo a proporção


def quadro(altura_pe=0):
    """Um quadro 64x64 com o personagem centralizado; altura_pe levanta o sprite."""
    q = Image.new("RGBA", (TAM, TAM), (0, 0, 0, 0))
    x = (TAM - base.width) // 2
    y = TAM - base.height - altura_pe
    q.paste(base, (x, y), base)
    return q


# 0 = parado | 1 = pulo (sprite "no ar") | 2 e 3 = caminhada (com um leve "pulinho")
quadros = [quadro(0), quadro(6), quadro(0), quadro(4)]

sheet = Image.new("RGBA", (TAM * 4, TAM), (0, 0, 0, 0))
for i, q in enumerate(quadros):
    sheet.paste(q, (i * TAM, 0))
sheet.save("sprites/player_sheet.png")
print("sprites/player_sheet.png criado!")