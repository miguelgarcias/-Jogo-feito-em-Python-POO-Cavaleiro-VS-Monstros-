import arcade
import random
import math

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

NOME_DESENVOLVEDORES = ["Miguel Garcia Sorrilha Neto", "Pedro de Sousa Silva"]


def calcular_escala(textura: arcade.Texture, tamanho_alvo_px: float) -> float:
    """Escala a textura para que seu maior lado tenha 'tamanho_alvo_px' px na tela."""
    return tamanho_alvo_px / max(textura.width, textura.height)


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("sprites/player_frente.png", scale=0.5)
        self.textura_frente = arcade.load_texture("sprites/player_frente.png")
        self.textura_costas = arcade.load_texture("sprites/player_costas.png")
        self.textura_direita = arcade.load_texture("sprites/player_direita.png")
        self.textura_esquerda = arcade.load_texture("sprites/player_esquerda.png")

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.change_x > 0:
            self.texture = self.textura_direita
        elif self.change_x < 0:
            self.texture = self.textura_esquerda
        elif self.change_y > 0:
            self.texture = self.textura_costas
        elif self.change_y < 0:
            self.texture = self.textura_frente

        self.left = max(self.left, 0)
        self.right = min(self.right, LARGURA)
        self.bottom = max(self.bottom, 0)
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
        angulo = random.uniform(0, 360)
        self.change_x = VELOCIDADE_MOEDA_ESPECIAL * math.cos(math.radians(angulo))
        self.change_y = VELOCIDADE_MOEDA_ESPECIAL * math.sin(math.radians(angulo))

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.right > LARGURA or self.left < 0:
            self.change_x *= -1
        if self.top > ALTURA or self.bottom < 0:
            self.change_y *= -1


class Inimigo(arcade.Sprite):
    PENALIDADE = 1

    def __init__(self):
        super().__init__("sprites/inimigo_direita.png")
        self.textura_direita = arcade.load_texture("sprites/inimigo_direita.png")
        self.textura_esquerda = arcade.load_texture("sprites/inimigo_esquerda.png")
        self.scale = calcular_escala(self.textura_direita, TAMANHO_INIMIGO_PX)
        self.change_x = random.choice([-1, 1]) * VELOCIDADE_INIMIGO
        self.change_y = random.choice([-1, 1]) * VELOCIDADE_INIMIGO
        self.texture = self.textura_direita if self.change_x > 0 else self.textura_esquerda

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.right > LARGURA or self.left < 0:
            self.change_x *= -1
        if self.top > ALTURA or self.bottom < 0:
            self.change_y *= -1
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
        self.center_y = random.randint(30, ALTURA - 30)


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
        arcade.draw_text("[ESC] Sair", LARGURA / 2, ALTURA / 2 - 70,
                          arcade.color.WHITE, font_size=22, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.J:
            self.window.show_view(JogoView())
        elif key == arcade.key.I:
            self.window.show_view(InstrucoesView())
        elif key == arcade.key.S:
            self.window.show_view(SobreView())
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
            "Objetivo: colete todas as moedas espalhadas pelo mapa.",
            "",
            "Cada moeda coletada vale +1 ponto.",
            "A moeda especial se move e quica nas bordas da tela; vale +5 pontos.",
            "O inimigo vermelho vaga pela tela e nunca desaparece: cada toque tira 1 ponto.",
            "O inimigo roxo persegue você lentamente; ao tocá-lo, você perde 1 ponto",
            "e ele é teletransportado para um novo local, recomeçando a perseguição.",
            "Após ser atingido, você fica 1 segundo protegido contra novos toques.",
            "Cuidado: se a pontuação ficar negativa, é Fim de Jogo (derrota) na hora!",
            "Você vence coletando todas as moedas antes que isso aconteça.",
            "",
            "Controles:",
            "  Setas direcionais ou WASD - mover o jogador",
            "  ESC - durante o jogo, interrompe a partida e volta ao Menu",
        ]
        y = ALTURA - 130
        for linha in linhas:
            arcade.draw_text(linha, LARGURA / 2, y, arcade.color.WHITE,
                              font_size=16, anchor_x="center")
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
        self.sprite_jogador = None
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

    def setup(self):
        self.window.background_color = (46, 147, 255)
        self.fundo = arcade.load_texture("sprites/fundo.png")
        self.retangulo_fundo = arcade.LBWH(0, 0, LARGURA, ALTURA)

        self.player = Player()
        self.player.center_x = LARGURA / 2
        self.player.center_y = ALTURA / 2
        self.sprite_jogador = arcade.SpriteList()
        self.sprite_jogador.append(self.player)

        self.sprite_moedas = arcade.SpriteList()
        for _ in range(TOTAL_MOEDAS):
            moeda = Moeda()
            moeda.center_x = random.randint(30, LARGURA - 30)
            moeda.center_y = random.randint(30, ALTURA - 30)
            self.sprite_moedas.append(moeda)

        self.sprite_inimigos = arcade.SpriteList()
        inimigo = Inimigo()
        inimigo.center_x = 100
        inimigo.center_y = 100
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
        elif key in (arcade.key.W, arcade.key.UP):
            self.player.change_y = VELOCIDADE_JOGADOR
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.player.change_y = -VELOCIDADE_JOGADOR

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.D, arcade.key.RIGHT, arcade.key.A, arcade.key.LEFT):
            self.player.change_x = 0
        elif key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.player.change_y = 0


class GameOverView(arcade.View):
    def __init__(self, pontuacao: int, tempo: float, venceu: bool):
        super().__init__()
        self.pontuacao = pontuacao
        self.tempo = tempo
        self.venceu = venceu

    def on_show_view(self):
        self.window.background_color = arcade.color.BLACK

    def on_draw(self):
        self.clear()
        titulo = "FIM DE JOGO" if self.venceu else "VOCÊ PERDEU"
        arcade.draw_text(titulo, LARGURA / 2, ALTURA - 120, arcade.color.WHITE,
                          36, anchor_x="center", bold=True)

        if not self.venceu:
            arcade.draw_text("Os inimigos drenaram sua pontuação! Colete moedas mais rápido.",
                              LARGURA / 2, ALTURA / 2 + 40, arcade.color.RED,
                              20, anchor_x="center")
        elif self.pontuacao >= TOTAL_MOEDAS:
            arcade.draw_text("Parabéns! Você escapou de todos os inimigos perfeitamente!",
                              LARGURA / 2, ALTURA / 2 + 40, arcade.color.GOLD,
                              20, anchor_x="center")
        else:
            arcade.draw_text("Parabéns por concluir o jogo!",
                              LARGURA / 2, ALTURA / 2 + 40, arcade.color.WHITE,
                              20, anchor_x="center")

        arcade.draw_text(f"Pontuação final: {self.pontuacao}", LARGURA / 2, ALTURA / 2,
                          arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text(f"Tempo total: {self.tempo:.1f}s", LARGURA / 2, ALTURA / 2 - 30,
                          arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("[M] Menu Principal    [ESC] Sair", LARGURA / 2, 60,
                          arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.M:
            self.window.show_view(MenuView())
        elif key == arcade.key.ESCAPE:
            arcade.exit()


class JanelaPrincipal(arcade.Window):
    def __init__(self):
        super().__init__(LARGURA, ALTURA, TITULO)


def main():
    janela = JanelaPrincipal()
    janela.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()