import arcade
import random
import math
import datetime

from peewee import (SqliteDatabase, Model, CharField, IntegerField,
                    FloatField, DateTimeField)

LARGURA = 800
ALTURA = 600
TITULO = "Cavaleiro VS Monstros"

TOTAL_MOEDAS = 25
VELOCIDADE_JOGADOR = 5
VELOCIDADE_MOEDA_ESPECIAL = 3
VELOCIDADE_INIMIGO = 2
VELOCIDADE_INIMIGO_ESPECIAL = 1.5

TAMANHO_INIMIGO_PX = 60
TAMANHO_AVATAR_PX = 90
TAMANHO_MOEDA_ESPECIAL_PX = 32
DURACAO_INVULNERABILIDADE = 1.0

# ---------- Física / cenário ----------
GRAVIDADE = 0.8
FORCA_PULO = 15
TAMANHO_BLOCO = 40
ALTURA_CHAO = TAMANHO_BLOCO  # topo do chão (1 fileira de blocos)
# (coluna inicial, y do centro, quantidade de blocos)
PLATAFORMAS = [
    (2, 140, 5),
    (9, 240, 5),
    (3, 340, 5),
    (10, 440, 6),
]

# ---------- Spritesheet do jogador ----------
# Arquivo: sprites/player_sheet.png  (faixa horizontal, personagem virado p/ direita)
# Quadros: 0 = parado | 1 = pulo | 2 e 3 = caminhada
SHEET_ARQUIVO = "sprites/player_sheet.png"
QUADRO_LARGURA = 64
QUADRO_ALTURA = 64
SHEET_COLUNAS = 4
SHEET_TOTAL_QUADROS = 4
INDICE_PARADO = 0
INDICE_PULO = 1
INDICES_CAMINHADA = [2, 3]
INTERVALO_QUADRO = 0.1  # 100 ms por quadro da caminhada
TAMANHO_PLAYER_PX = 64

NOME_DESENVOLVEDORES = ["Miguel Garcia Sorrilha Neto", "Pedro de Sousa Silva"]


# =====================================================================
#  MODELO DE DADOS (Peewee ORM)
# =====================================================================
db = SqliteDatabase("ranking.db")


class BaseModel(Model):
    class Meta:
        database = db


class Pontuacao(BaseModel):
    nome_jogador = CharField()
    pontos = IntegerField()
    tempo_partida = FloatField()
    data_hora = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"{self.nome_jogador} - {self.pontos} pts ({self.tempo_partida:.1f}s)"


def iniciar_banco():
    db.connect(reuse_if_open=True)
    db.create_tables([Pontuacao])


# =====================================================================
#  FUNÇÕES AUXILIARES
# =====================================================================
def calcular_escala(textura: arcade.Texture, tamanho_alvo_px: float) -> float:
    """Escala a textura para que seu maior lado tenha 'tamanho_alvo_px' px na tela."""
    return tamanho_alvo_px / max(textura.width, textura.height)


# =====================================================================
#  SPRITES
# =====================================================================
class Bloco(arcade.Sprite):
    """Bloco sólido usado no chão e nas plataformas suspensas."""

    def __init__(self, x: float, y: float):
        super().__init__("sprites/bloco.png")
        self.scale = calcular_escala(self.texture, TAMANHO_BLOCO)
        self.center_x = x
        self.center_y = y


class Player(arcade.Sprite):
    def __init__(self):
        sheet = arcade.load_spritesheet(SHEET_ARQUIVO)
        quadros = sheet.get_texture_grid(
            size=(QUADRO_LARGURA, QUADRO_ALTURA),
            columns=SHEET_COLUNAS,
            count=SHEET_TOTAL_QUADROS,
        )
        super().__init__(quadros[INDICE_PARADO],
                         scale=calcular_escala(quadros[INDICE_PARADO], TAMANHO_PLAYER_PX))

        # texturas para a direita e (espelhadas) para a esquerda
        self.texturas = {
            "direita": {
                "parado": quadros[INDICE_PARADO],
                "pulo": quadros[INDICE_PULO],
                "andando": [quadros[i] for i in INDICES_CAMINHADA],
            },
            "esquerda": {
                "parado": quadros[INDICE_PARADO].flip_left_right(),
                "pulo": quadros[INDICE_PULO].flip_left_right(),
                "andando": [quadros[i].flip_left_right() for i in INDICES_CAMINHADA],
            },
        }

        self.virado_para = "direita"
        self.indice_caminhada = 0
        self.tempo_quadro = 0.0

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        # A movimentação em si é feita pelo PhysicsEnginePlatformer;
        # aqui só decidimos a direção e a textura (máquina de estados).
        if self.change_x > 0:
            self.virado_para = "direita"
        elif self.change_x < 0:
            self.virado_para = "esquerda"

        texturas = self.texturas[self.virado_para]

        if self.change_y != 0:                      # 1) Pulo / Queda
            self.texture = texturas["pulo"]
            self.tempo_quadro = 0.0
        elif self.change_x == 0:                    # 2) Repouso / Idle
            self.texture = texturas["parado"]
            self.indice_caminhada = 0
            self.tempo_quadro = 0.0
        else:                                       # 3) Andando / Walk
            self.tempo_quadro += delta_time
            if self.tempo_quadro >= INTERVALO_QUADRO:
                self.tempo_quadro -= INTERVALO_QUADRO
                self.indice_caminhada = (self.indice_caminhada + 1) % len(texturas["andando"])
            self.texture = texturas["andando"][self.indice_caminhada]

        # mantém o jogador dentro da tela
        self.left = max(self.left, 0)
        self.right = min(self.right, LARGURA)
        self.top = min(self.top, ALTURA)


class Moeda(arcade.Sprite):
    VALOR = 1

    def __init__(self):
        super().__init__("sprites/moeda.png", scale=0.1)


class MoedaEspecial(arcade.Sprite):
    VALOR = 5

    def __init__(self):
        super().__init__("sprites/moeda_especial.png")
        self.scale = calcular_escala(self.texture, TAMANHO_MOEDA_ESPECIAL_PX)
        angulo = random.uniform(20, 160)
        self.change_x = VELOCIDADE_MOEDA_ESPECIAL * math.cos(math.radians(angulo))
        self.change_y = VELOCIDADE_MOEDA_ESPECIAL * math.sin(math.radians(angulo))

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.right > LARGURA or self.left < 0:
            self.change_x *= -1
        if self.top > ALTURA or self.bottom < ALTURA_CHAO:
            self.change_y *= -1


class Inimigo(arcade.Sprite):
    """Patrulha o chão de um lado ao outro da tela."""
    PENALIDADE = 1

    def __init__(self):
        super().__init__("sprites/inimigo_direita.png")
        self.textura_direita = arcade.load_texture("sprites/inimigo_direita.png")
        self.textura_esquerda = arcade.load_texture("sprites/inimigo_esquerda.png")
        self.scale = calcular_escala(self.textura_direita, TAMANHO_INIMIGO_PX)
        self.change_x = random.choice([-1, 1]) * VELOCIDADE_INIMIGO
        self.change_y = 0
        self.texture = self.textura_direita if self.change_x > 0 else self.textura_esquerda

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.center_x += self.change_x
        if self.right > LARGURA or self.left < 0:
            self.change_x *= -1
        if self.change_x > 0:
            self.texture = self.textura_direita
        elif self.change_x < 0:
            self.texture = self.textura_esquerda


class InimigoEspecial(arcade.Sprite):
    PENALIDADE = 1

    def __init__(self):
        super().__init__("sprites/inimigo_especial_direita.png")
        self.textura_direita = arcade.load_texture("sprites/inimigo_especial_direita.png")
        self.textura_esquerda = arcade.load_texture("sprites/inimigo_especial_esquerda.png")
        self.scale = calcular_escala(self.textura_direita, TAMANHO_INIMIGO_PX)

    def seguir(self, alvo: arcade.Sprite) -> None:
        dx = alvo.center_x - self.center_x
        dy = alvo.center_y - self.center_y
        distancia = max(math.hypot(dx, dy), 1)
        self.change_x = (dx / distancia) * VELOCIDADE_INIMIGO_ESPECIAL
        self.change_y = (dy / distancia) * VELOCIDADE_INIMIGO_ESPECIAL

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.change_x > 0:
            self.texture = self.textura_direita
        elif self.change_x < 0:
            self.texture = self.textura_esquerda

    def teletransportar(self) -> None:
        self.center_x = random.randint(30, LARGURA - 30)
        self.center_y = random.randint(ALTURA_CHAO + 30, ALTURA - 30)


# =====================================================================
#  TELAS (VIEWS)
# =====================================================================
class MenuView(arcade.View):
    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY

    def on_draw(self):
        self.clear()
        arcade.draw_text(TITULO, LARGURA / 2, ALTURA - 150, arcade.color.WHITE,
                          font_size=36, anchor_x="center", bold=True)
        arcade.draw_text("[J] Jogar", LARGURA / 2, ALTURA / 2 + 50,
                          arcade.color.WHITE, font_size=22, anchor_x="center")
        arcade.draw_text("[I] Instruções", LARGURA / 2, ALTURA / 2 + 10,
                          arcade.color.WHITE, font_size=22, anchor_x="center")
        arcade.draw_text("[S] Sobre o Jogo", LARGURA / 2, ALTURA / 2 - 30,
                          arcade.color.WHITE, font_size=22, anchor_x="center")
        arcade.draw_text("[R] Ranking", LARGURA / 2, ALTURA / 2 - 70,
                          arcade.color.WHITE, font_size=22, anchor_x="center")
        arcade.draw_text("[ESC] Sair", LARGURA / 2, ALTURA / 2 - 110,
                          arcade.color.WHITE, font_size=22, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.J:
            self.window.show_view(JogoView())
        elif key == arcade.key.I:
            self.window.show_view(InstrucoesView())
        elif key == arcade.key.S:
            self.window.show_view(SobreView())
        elif key == arcade.key.R:
            self.window.show_view(TelaRanking())
        elif key == arcade.key.ESCAPE:
            arcade.exit()


class InstrucoesView(arcade.View):
    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_SLATE_GRAY

    def on_draw(self):
        self.clear()
        arcade.draw_text("Instruções", LARGURA / 2, ALTURA - 70, arcade.color.WHITE,
                          font_size=32, anchor_x="center", bold=True)

        linhas = [
            "Objetivo: colete todas as moedas espalhadas pelo chão e plataformas.",
            "",
            "Cada moeda coletada vale +1 ponto.",
            "A moeda especial voa e quica nas bordas da tela; vale +5 pontos.",
            "O inimigo vermelho patrulha o chão: cada toque tira 1 ponto (pule sobre ele!).",
            "O inimigo roxo persegue você lentamente; ao tocá-lo, você perde 1 ponto",
            "e ele é teletransportado para um novo local, recomeçando a perseguição.",
            "Após ser atingido, você fica 1 segundo protegido contra novos toques.",
            "Cuidado: se a pontuação ficar negativa, é Fim de Jogo (derrota) na hora!",
            "Você vence coletando todas as moedas antes que isso aconteça.",
            "",
            "Controles:",
            "  Setas ou A / D - andar    |    W, Seta para cima ou ESPAÇO - pular",
            "  ESC - durante o jogo, interrompe a partida e volta ao Menu",
        ]
        y = ALTURA - 130
        for linha in linhas:
            arcade.draw_text(linha, LARGURA / 2, y, arcade.color.WHITE,
                              font_size=15, anchor_x="center")
            y -= 30

        arcade.draw_text("[ESC] / [M] Voltar ao Menu", LARGURA / 2, 40,
                          arcade.color.LIGHT_GRAY, font_size=16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.M):
            self.window.show_view(MenuView())


class SobreView(arcade.View):
    def __init__(self):
        super().__init__()
        self.sprite_avatares = arcade.SpriteList()
        for i, _nome in enumerate(NOME_DESENVOLVEDORES):
            avatar = arcade.Sprite("sprites/inimigo_especial_direita.png")
            avatar.scale = calcular_escala(avatar.texture, TAMANHO_AVATAR_PX)
            avatar.center_x = 150 + i * 250
            avatar.center_y = ALTURA / 2 + 40
            self.sprite_avatares.append(avatar)

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_SLATE_GRAY

    def on_draw(self):
        self.clear()
        arcade.draw_text("Sobre o Jogo", LARGURA / 2, ALTURA - 80, arcade.color.WHITE,
                          font_size=32, anchor_x="center", bold=True)
        self.sprite_avatares.draw()
        for i, nome in enumerate(NOME_DESENVOLVEDORES):
            arcade.draw_text(nome, 150 + i * 250, ALTURA / 2 - 30, arcade.color.WHITE,
                              font_size=16, anchor_x="center")
        arcade.draw_text("[ESC] / [M] Voltar ao Menu", LARGURA / 2, 50,
                          arcade.color.LIGHT_GRAY, font_size=16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.M):
            self.window.show_view(MenuView())


class JogoView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.physics = None
        self.sprite_jogador = None
        self.sprite_blocos = None
        self.sprite_moedas = None
        self.sprite_moedas_especiais = None
        self.sprite_inimigos = None
        self.sprite_inimigos_especiais = None

        self.pontuacao = 0
        self.tempo_decorrido = 0.0
        self.alerta_timer = 0.0
        self.texto_alerta = ""
        # invulneravel_timer > 0: jogador imune a novos toques (evita perder
        # pontos em todo quadro enquanto os sprites ainda estão sobrepostos).
        self.invulneravel_timer = 0.0

    def criar_cenario(self):
        """Monta o chão e as plataformas suspensas com a classe Bloco."""
        self.sprite_blocos = arcade.SpriteList()

        # chão: uma fileira de blocos cobrindo toda a largura
        for coluna in range(LARGURA // TAMANHO_BLOCO):
            x = coluna * TAMANHO_BLOCO + TAMANHO_BLOCO / 2
            self.sprite_blocos.append(Bloco(x, TAMANHO_BLOCO / 2))

        # plataformas suspensas
        for coluna_inicial, y, quantidade in PLATAFORMAS:
            for k in range(quantidade):
                x = (coluna_inicial + k) * TAMANHO_BLOCO + TAMANHO_BLOCO / 2
                self.sprite_blocos.append(Bloco(x, y))

    def setup(self):
        self.window.background_color = (46, 147, 255)
        self.fundo = arcade.load_texture("sprites/fundo.png")
        self.retangulo_fundo = arcade.LBWH(0, 0, LARGURA, ALTURA)

        self.criar_cenario()

        self.player = Player()
        self.player.center_x = LARGURA / 2
        self.player.bottom = ALTURA_CHAO + 5
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.player)

        # motor de física: gravidade + colisão com os blocos
        self.physics = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.sprite_blocos, gravity_constant=GRAVIDADE
        )

        # moedas sobre blocos sorteados (chão ou plataformas)
        self.sprite_moedas = arcade.SpriteList()
        for bloco in random.sample(list(self.sprite_blocos), TOTAL_MOEDAS):
            moeda = Moeda()
            moeda.center_x = bloco.center_x
            moeda.center_y = bloco.top + 20
            self.sprite_moedas.append(moeda)

        self.sprite_inimigos = arcade.SpriteList()
        inimigo = Inimigo()
        inimigo.center_x = 100
        inimigo.bottom = ALTURA_CHAO
        self.sprite_inimigos.append(inimigo)

        self.sprite_moedas_especiais = arcade.SpriteList()
        moeda_especial = MoedaEspecial()
        moeda_especial.center_x = 600
        moeda_especial.center_y = 500
        self.sprite_moedas_especiais.append(moeda_especial)

        self.sprite_inimigos_especiais = arcade.SpriteList()
        inimigo_especial = InimigoEspecial()
        inimigo_especial.center_x = 700
        inimigo_especial.center_y = 500
        self.sprite_inimigos_especiais.append(inimigo_especial)

        self.pontuacao = 0
        self.tempo_decorrido = 0.0
        self.alerta_timer = 0.0
        self.invulneravel_timer = 0.0

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.fundo, self.retangulo_fundo)
        self.sprite_blocos.draw()
        self.sprite_moedas.draw()
        self.sprite_moedas_especiais.draw()
        self.sprite_inimigos.draw()
        self.sprite_inimigos_especiais.draw()
        self.sprite_jogador.draw()

        arcade.draw_text(f"Pontuação: {self.pontuacao}", 10, ALTURA - 25,
                          arcade.color.WHITE, 16)
        arcade.draw_text(f"Tempo: {self.tempo_decorrido:.1f}s", 10, ALTURA - 50,
                          arcade.color.WHITE, 16)
        arcade.draw_text(f"Moedas restantes: {len(self.sprite_moedas)}", 10, ALTURA - 75,
                          arcade.color.WHITE, 16)

        if self.alerta_timer > 0:
            arcade.draw_text(self.texto_alerta, LARGURA / 2, ALTURA - 30,
                              arcade.color.RED, 20, anchor_x="center", bold=True)

    def on_update(self, delta_time):
        self.tempo_decorrido += delta_time
        if self.alerta_timer > 0:
            self.alerta_timer -= delta_time
        if self.invulneravel_timer > 0:
            self.invulneravel_timer -= delta_time

        # 1º física (move o jogador), 2º animação (Player.update)
        self.physics.update()
        self.sprite_jogador.update(delta_time)
        self.sprite_moedas_especiais.update(delta_time)
        self.sprite_inimigos.update(delta_time)

        for inimigo_especial in self.sprite_inimigos_especiais:
            inimigo_especial.seguir(self.player)
        self.sprite_inimigos_especiais.update(delta_time)

        self.verificar_colisoes()

        if self.pontuacao < 0:
            self.window.show_view(
                GameOverView(self.pontuacao, self.tempo_decorrido, venceu=False)
            )
        elif len(self.sprite_moedas) == 0:
            self.window.show_view(
                GameOverView(self.pontuacao, self.tempo_decorrido, venceu=True)
            )

    def verificar_colisoes(self):
        for moeda in arcade.check_for_collision_with_list(self.player, self.sprite_moedas):
            moeda.remove_from_sprite_lists()
            self.pontuacao += Moeda.VALOR

        for especial in arcade.check_for_collision_with_list(self.player, self.sprite_moedas_especiais):
            especial.remove_from_sprite_lists()
            self.pontuacao += MoedaEspecial.VALOR

        if self.invulneravel_timer > 0:
            return

        if arcade.check_for_collision_with_list(self.player, self.sprite_inimigos):
            self.pontuacao -= Inimigo.PENALIDADE
            self.alerta_timer = 1.0
            self.texto_alerta = "Cuidado! O inimigo te atingiu!"
            self.invulneravel_timer = DURACAO_INVULNERABILIDADE
            return

        perseguidores = arcade.check_for_collision_with_list(self.player, self.sprite_inimigos_especiais)
        if perseguidores:
            self.pontuacao -= InimigoEspecial.PENALIDADE
            self.alerta_timer = 1.0
            self.texto_alerta = "O perseguidor te alcançou!"
            for perseguidor in perseguidores:
                perseguidor.teletransportar()
            self.invulneravel_timer = DURACAO_INVULNERABILIDADE

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())
            return
        if key in (arcade.key.D, arcade.key.RIGHT):
            self.player.change_x = VELOCIDADE_JOGADOR
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.player.change_x = -VELOCIDADE_JOGADOR
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            # can_jump() só é True com o jogador apoiado em um bloco: sem pulo duplo
            if self.physics.can_jump():
                self.physics.jump(FORCA_PULO)

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.D, arcade.key.RIGHT, arcade.key.A, arcade.key.LEFT):
            self.player.change_x = 0


class GameOverView(arcade.View):
    TAMANHO_MAX_NOME = 15

    def __init__(self, pontuacao: int, tempo: float, venceu: bool):
        super().__init__()
        self.pontuacao = pontuacao
        self.tempo = tempo
        self.venceu = venceu
        self.nome = ""
        self.salvo = False

    def on_show_view(self):
        self.window.background_color = arcade.color.BLACK

    def salvar_pontuacao(self):
        nome = self.nome.strip() or "Anônimo"
        Pontuacao.create(nome_jogador=nome, pontos=self.pontuacao,
                         tempo_partida=self.tempo)
        self.salvo = True

    def on_draw(self):
        self.clear()
        titulo = "FIM DE JOGO" if self.venceu else "VOCÊ PERDEU"
        arcade.draw_text(titulo, LARGURA / 2, ALTURA - 120, arcade.color.WHITE,
                          36, anchor_x="center", bold=True)

        if not self.venceu:
            arcade.draw_text("Os inimigos drenaram sua pontuação! Colete moedas mais rápido.",
                              LARGURA / 2, ALTURA / 2 + 60, arcade.color.RED,
                              18, anchor_x="center")
        elif self.pontuacao >= TOTAL_MOEDAS:
            arcade.draw_text("Parabéns! Você escapou de todos os inimigos perfeitamente!",
                              LARGURA / 2, ALTURA / 2 + 60, arcade.color.GOLD,
                              20, anchor_x="center")
        else:
            arcade.draw_text("Parabéns por concluir o jogo!",
                              LARGURA / 2, ALTURA / 2 + 60, arcade.color.WHITE,
                              20, anchor_x="center")

        arcade.draw_text(f"Pontuação final: {self.pontuacao}", LARGURA / 2, ALTURA / 2 + 20,
                          arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text(f"Tempo total: {self.tempo:.1f}s", LARGURA / 2, ALTURA / 2 - 10,
                          arcade.color.WHITE, 18, anchor_x="center")

        if not self.salvo:
            arcade.draw_text("Digite seu nome e pressione ENTER para salvar:",
                              LARGURA / 2, ALTURA / 2 - 60, arcade.color.LIGHT_GRAY,
                              16, anchor_x="center")
            arcade.draw_text(self.nome + "_", LARGURA / 2, ALTURA / 2 - 95,
                              arcade.color.YELLOW, 22, anchor_x="center", bold=True)
            arcade.draw_text("[ESC] Pular sem salvar", LARGURA / 2, 60,
                              arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        else:
            arcade.draw_text("Pontuação salva no ranking!", LARGURA / 2, ALTURA / 2 - 70,
                              arcade.color.GREEN, 18, anchor_x="center")
            arcade.draw_text("[M] Menu Principal    [R] Ranking    [ESC] Sair",
                              LARGURA / 2, 60, arcade.color.LIGHT_GRAY, 16,
                              anchor_x="center")

    def on_text(self, text: str):
        # captura de texto digitado (só enquanto o nome não foi salvo)
        if self.salvo:
            return
        if text.isprintable() and len(self.nome) < self.TAMANHO_MAX_NOME:
            self.nome += text

    def on_key_press(self, key, modifiers):
        if not self.salvo:
            if key == arcade.key.BACKSPACE:
                self.nome = self.nome[:-1]
            elif key in (arcade.key.ENTER, arcade.key.NUM_ENTER):
                self.salvar_pontuacao()
            elif key == arcade.key.ESCAPE:
                self.window.show_view(MenuView())
            return

        if key == arcade.key.M:
            self.window.show_view(MenuView())
        elif key == arcade.key.R:
            self.window.show_view(TelaRanking())
        elif key == arcade.key.ESCAPE:
            arcade.exit()


class TelaRanking(arcade.View):
    def __init__(self):
        super().__init__()
        # Consulta executada UMA única vez (nunca dentro do on_draw)
        self.melhores = list(
            Pontuacao.select().order_by(Pontuacao.pontos.desc()).limit(10)
        )

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_SLATE_GRAY

    def on_draw(self):
        self.clear()
        arcade.draw_text("Ranking - Top 10", LARGURA / 2, ALTURA - 70,
                          arcade.color.WHITE, 32, anchor_x="center", bold=True)

        if not self.melhores:
            arcade.draw_text("Nenhuma pontuação registrada ainda.", LARGURA / 2,
                              ALTURA / 2, arcade.color.LIGHT_GRAY, 20, anchor_x="center")
        else:
            y_cabecalho = ALTURA - 125
            arcade.draw_text("#", 80, y_cabecalho, arcade.color.GOLD, 16, bold=True)
            arcade.draw_text("Jogador", 130, y_cabecalho, arcade.color.GOLD, 16, bold=True)
            arcade.draw_text("Pontos", 480, y_cabecalho, arcade.color.GOLD, 16,
                              anchor_x="right", bold=True)
            arcade.draw_text("Tempo", 570, y_cabecalho, arcade.color.GOLD, 16,
                              anchor_x="right", bold=True)
            arcade.draw_text("Data", 620, y_cabecalho, arcade.color.GOLD, 16, bold=True)

            for i, registro in enumerate(self.melhores):
                y = ALTURA - 160 - i * 35
                arcade.draw_text(f"{i + 1}º", 80, y, arcade.color.WHITE, 16)
                arcade.draw_text(registro.nome_jogador, 130, y, arcade.color.WHITE, 16)
                arcade.draw_text(str(registro.pontos), 480, y, arcade.color.WHITE, 16,
                                  anchor_x="right")
                arcade.draw_text(f"{registro.tempo_partida:.1f}s", 570, y,
                                  arcade.color.WHITE, 16, anchor_x="right")
                arcade.draw_text(registro.data_hora.strftime("%d/%m/%y"), 620, y,
                                  arcade.color.LIGHT_GRAY, 14)

        arcade.draw_text("[ESC] / [M] Voltar ao Menu", LARGURA / 2, 30,
                          arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.M):
            self.window.show_view(MenuView())


class JanelaPrincipal(arcade.Window):
    def __init__(self):
        super().__init__(LARGURA, ALTURA, TITULO)


def main():
    iniciar_banco()
    janela = JanelaPrincipal()
    janela.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()