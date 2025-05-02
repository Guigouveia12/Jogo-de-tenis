import pygame
import sys
import random
import math
import os

pygame.init()
pygame.mixer.init()

def carregar_imagem_fundo():
    try:
        imagem = pygame.image.load("menu_background.png").convert()
        imagem = pygame.transform.scale(imagem, (largura, altura))
        return imagem
    except Exception as e:
        print(f"Erro ao carregar imagem de fundo: {e}")
        return None

# Configurações da tela
largura = 800
altura = 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Tennis game")

# Cores
VERDE = (0, 128, 0)
VERDE_ESCURO = (0, 100, 0)
AZUL = (0, 0, 255)
AZUL_CLARO = (100, 149, 237)
LARANJA = (255, 165, 0)
LARANJA_ESCURO = (255, 140, 0)
BRANCO = (255, 255, 255)
AMARELO = (255, 255, 0)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
MARROM = (139, 69, 19)
MARROM_CLARO = (160, 82, 45)
ROSA = (255, 105, 180)
CINZA = (169, 169, 169)

# Carregando fonte
fonte = pygame.font.SysFont("Arial", 30)
fonte_grande = pygame.font.SysFont("Arial", 50)
fonte_pequena = pygame.font.SysFont("Arial", 20)

# Configurar ícone do jogo
def criar_icone_raquete():
    tamanho_icone = 32
    superficie_icone = pygame.Surface((tamanho_icone, tamanho_icone))
    superficie_icone.fill((255, 255, 255))  # Fundo branco

    # Desenhar uma raquete simples no ícone
    raio = 8
    pygame.draw.ellipse(superficie_icone, PRETO, (4, 0, raio * 2, raio * 2.5), 2)
    # Linhas da rede
    for i in range(-raio + 6, raio - 3, 4):
        pygame.draw.line(superficie_icone, PRETO, (tamanho_icone // 2 + i, 2), (tamanho_icone // 2 + i, 18), 1)
    for i in range(-raio + 6, raio - 3, 4):
        pygame.draw.line(superficie_icone, PRETO, (6, i + 8), (26, i + 8), 1)
    # Cabo
    pygame.draw.line(superficie_icone, PRETO, (tamanho_icone // 2, 20), (tamanho_icone // 2, 30), 2)

    return superficie_icone

icone = criar_icone_raquete()
pygame.display.set_icon(icone)

# Carregar ou criar som
def carregar_som(nome_arquivo):
    try:
        som = pygame.mixer.Sound(nome_arquivo)
    except:
        print(f"Arquivo de som {nome_arquivo} não encontrado. Criando som padrão.")
        som = pygame.mixer.Sound(buffer=bytes([]))
    return som

# Sons do jogo
try:
    som_rebatida = pygame.mixer.Sound("rebatida.wav")
except:
    print("Criando som de rebatida padrão.")
    som_rebatida = pygame.mixer.Sound(buffer=bytes([]))

try:
    som_torcida = pygame.mixer.Sound("torcida.wav")
except:
    print("Criando som de torcida padrão.")
    som_torcida = pygame.mixer.Sound(buffer=bytes([]))

try:
    musica_menu = pygame.mixer.Sound("menu_music.wav")
    musica_menu.set_volume(0.5)
except:
    print("Criando música de menu padrão.")
    musica_menu = pygame.mixer.Sound(buffer=bytes([]))

# Classe Botão para o menu
class Botao:
    def __init__(self, x, y, largura, altura, texto, cor, cor_hover):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor = cor
        self.cor_hover = cor_hover
        self.hover = False

    def desenhar(self):
        cor_atual = self.cor_hover if self.hover else self.cor
        pygame.draw.rect(tela, cor_atual, self.rect, 0, 10)
        pygame.draw.rect(tela, PRETO, self.rect, 2, 10)

        texto_surf = fonte.render(self.texto, True, PRETO)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        tela.blit(texto_surf, texto_rect)

    def verificar_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover

    def foi_clicado(self, pos):
        return self.rect.collidepoint(pos)

# Classe da Bola
class Bola:
    def __init__(self):
        self.raio = 15
        self.pontos = 0
        self.vidas = 3
        self.nivel = 1
        self.combo = 0
        self.max_combo = 0
        self.reset()

    def reset(self):
        # Posição inicial da bola (lado do adversário)
        self.x = random.randint(50, largura - 50)
        self.y = 50

        # Velocidade inicial
        angulo = random.uniform(math.pi / 4, 3 * math.pi / 4)  # Ângulo de lançamento
        velocidade_base = 3 + self.nivel * 0.5
        self.vel_x = velocidade_base * math.cos(angulo)
        self.vel_y = velocidade_base * math.sin(angulo)

        # Controle de clique
        self.foi_clicada = False
        self.pode_clicar = False  # Só poderá clicar quando estiver na zona de rebatida

    def mover(self):
        self.x += self.vel_x
        self.y += self.vel_y

        # Colisão com as bordas laterais
        if self.x <= self.raio + 50 or self.x >= largura - self.raio - 50:
            self.vel_x = -self.vel_x

        # Colisão com o topo
        if self.y <= self.raio + 50:
            self.vel_y = abs(self.vel_y)
            # Resetar a possibilidade de clique quando a bola rebate no topo
            self.foi_clicada = False

        # Verificar se a bola está na zona de rebatida (parte inferior da tela)
        if self.y >= altura - 150 and not self.pode_clicar:
            self.pode_clicar = True
            self.foi_clicada = False  # Reset do clique quando entra na zona novamente

        # Verificar se a bola saiu da tela
        if self.y >= altura + self.raio:
            self.vidas -= 1
            self.combo = 0
            self.reset()

    def desenhar(self):
        pygame.draw.circle(tela, AMARELO, (int(self.x), int(self.y)), self.raio)

    def verificar_clique(self, pos_mouse):
        if not self.pode_clicar or self.foi_clicada:
            return False

        # Calcular a distância entre o mouse e o centro da bola
        dx = pos_mouse[0] - self.x
        dy = pos_mouse[1] - self.y
        distancia = math.sqrt(dx * dx + dy * dy)

        # Se o clique for na bola
        if distancia <= self.raio:
            self.foi_clicada = True
            self.pode_clicar = False
            self.vel_y = -abs(self.vel_y) - 1  # Rebate a bola para cima com mais velocidade

            # Ajusta a direção horizontal baseada em onde a bola foi clicada
            self.vel_x += dx * 0.1

            # Tocar som de rebatida
            som_rebatida.play()

            # Incrementa pontos e combo
            self.pontos += 10 * (1 + self.combo // 5)
            self.combo += 1
            if self.combo > self.max_combo:
                self.max_combo = self.combo
                # Tocar som de torcida quando bate recorde de combo
                if self.combo > 3:
                    som_torcida.play()

            # Verifica se deve aumentar o nível
            if self.pontos >= self.nivel * 200:
                self.nivel += 1

            return True
        return False

# Classe para a Torcida
class Torcida:
    def __init__(self):
        self.torcedores = []
        self.criar_torcedores()

    def criar_torcedores(self):
        # Criar torcedores na arquibancada esquerda (5 fileiras com 4 torcedores cada)
        for fileira in range(5):
            for coluna in range(4):
                x = 15 + coluna * 10
                y = 100 + fileira * 80
                cor = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                self.torcedores.append((x, y, cor, random.randint(0, 1)))

        # Criar torcedores na arquibancada direita (5 fileiras com 4 torcedores cada)
        for fileira in range(5):
            for coluna in range(4):
                x = largura - 15 - coluna * 10
                y = 100 + fileira * 80
                cor = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                self.torcedores.append((x, y, cor, random.randint(0, 1)))

    def desenhar(self, tempo):
        # Desenhar arquibancadas
        # Lado esquerdo
        for i in range(5):
            pygame.draw.rect(tela, MARROM_CLARO, (0, 50 + i * 80, 50, 60))
            pygame.draw.rect(tela, MARROM, (0, 50 + i * 80, 50, 15))  # Degrau

        # Lado direito
        for i in range(5):
            pygame.draw.rect(tela, MARROM_CLARO, (largura - 50, 50 + i * 80, 50, 60))
            pygame.draw.rect(tela, MARROM, (largura - 50, 50 + i * 80, 50, 15))  # Degrau

        # Desenhar torcedores
        for i, (x, y, cor, anim) in enumerate(self.torcedores):
            # Animação simples - torcedores se movem ligeiramente para cima e para baixo
            offset = math.sin(tempo * 0.1 + i) * 3
            y_anim = y + offset if anim else y - offset

            # Desenhar torcedor (cabeça e corpo simples)
            pygame.draw.circle(tela, cor, (x, y_anim - 5), 5)  # Cabeça
            pygame.draw.line(tela, cor, (x, y_anim), (x, y_anim + 10), 2)  # Corpo

            # Braços animados (levantando conforme o tempo)
            arm_angle = math.sin(tempo * 0.05 + i * 0.2) * 0.5
            arm_x = 5 * math.cos(arm_angle)
            arm_y = 5 * math.sin(arm_angle)

            pygame.draw.line(tela, cor, (x, y_anim + 5), (x - arm_x, y_anim + 7 - arm_y), 2)  # Braço esquerdo
            pygame.draw.line(tela, cor, (x, y_anim + 5), (x + arm_x, y_anim + 7 - arm_y), 2)  # Braço direito
            pygame.draw.line(tela, cor, (x, y_anim + 10), (x - 3, y_anim + 15), 2)  # Perna esquerda
            pygame.draw.line(tela, cor, (x, y_anim + 10), (x + 3, y_anim + 15), 2)  # Perna direita

# Raquete de tênis para o cursor
class Raquete:
    def __init__(self, cor=PRETO):
        self.cor = cor
        self.raio = 15
        self.cabo_comprimento = 25

    def desenhar(self, pos):
        x, y = pos
        # Oval da raquete
        pygame.draw.ellipse(tela, self.cor, (x - self.raio, y - self.raio - 5, self.raio * 2, self.raio * 2.5), 3)
        # Linhas da rede na raquete
        for i in range(-self.raio + 4, self.raio - 3, 6):
            pygame.draw.line(tela, self.cor, (x + i, y - self.raio), (x + i, y + self.raio - 10), 1)
        for i in range(-self.raio + 4, self.raio - 3, 6):
            pygame.draw.line(tela, self.cor, (x - self.raio + 3, y + i - 5), (x + self.raio - 3, y + i - 5), 1)
        # Cabo da raquete
        pygame.draw.line(tela, self.cor, (x, y + self.raio - 10), (x, y + self.raio + self.cabo_comprimento), 3)
        # Grip do cabo
        pygame.draw.line(tela, CINZA, (x, y + self.raio + 5), (x, y + self.raio + self.cabo_comprimento), 6)

class RaqueteAdversario:
    def __init__(self, cor=VERMELHO):
        self.cor = cor
        self.raio = 15
        self.cabo_comprimento = 25
        self.x = largura // 2
        self.y = 80  # Posição vertical fixa no topo da quadra
        self.velocidade = 4
        self.dificuldade = 0.8  # Fator de dificuldade (1.0 = perfeito, 0.0 = não se move)
        self.alvo_x = self.x  # Posição alvo para mover

    def atualizar(self, bola, nivel):
        # Aumenta a dificuldade com o nível
        dificuldade_ajustada = min(0.95, self.dificuldade + (nivel * 0.02))

        # Define o alvo como a posição x da bola quando ela está subindo
        if bola.vel_y < 0 and bola.y < altura // 2:
            # Adiciona um erro aleatório baseado na dificuldade
            erro = random.randint(-50, 50) * (1 - dificuldade_ajustada)
            self.alvo_x = bola.x + erro

        # Limita o alvo dentro dos limites da quadra
        self.alvo_x = max(50 + self.raio, min(largura - 50 - self.raio, self.alvo_x))

        # Move a raquete em direção ao alvo
        if self.x < self.alvo_x:
            self.x += min(self.velocidade, self.alvo_x - self.x)
        elif self.x > self.alvo_x:
            self.x -= min(self.velocidade, self.x - self.alvo_x)

    def verificar_colisao(self, bola):
        # Verifica se a bola está perto da raquete
        if bola.y - bola.raio <= self.y + self.raio and bola.vel_y < 0:
            # Calcular a distância horizontal entre a bola e o centro da raquete
            dx = abs(bola.x - self.x)
            if dx <= self.raio * 1.5:  # Área de colisão ligeiramente maior que a raquete visual
                # Rebate a bola
                bola.vel_y = abs(bola.vel_y)

                # Ajusta a direção horizontal baseada em onde a bola foi rebatida
                bola.vel_x += (bola.x - self.x) * 0.1

                # Tocar som de rebatida
                som_rebatida.play()
                return True
        return False

    def desenhar(self):
        # Oval da raquete
        pygame.draw.ellipse(tela, self.cor,
                            (self.x - self.raio, self.y - self.raio - 5, self.raio * 2, self.raio * 2.5), 3)
        # Linhas da rede na raquete
        for i in range(-self.raio + 4, self.raio - 3, 6):
            pygame.draw.line(tela, self.cor, (self.x + i, self.y - self.raio), (self.x + i, self.y + self.raio - 10), 1)
        for i in range(-self.raio + 4, self.raio - 3, 6):
            pygame.draw.line(tela, self.cor, (self.x - self.raio + 3, self.y + i - 5),
                             (self.x + self.raio - 3, self.y + i - 5), 1)
        # Cabo da raquete
        pygame.draw.line(tela, self.cor, (self.x, self.y + self.raio - 10),
                         (self.x, self.y + self.raio + self.cabo_comprimento), 3)
        # Grip do cabo
        pygame.draw.line(tela, CINZA, (self.x, self.y + self.raio + 5),
                         (self.x, self.y + self.raio + self.cabo_comprimento), 6)

# Modifique a função menu_inicial():
def menu_inicial():
    # Opções disponíveis
    cores_quadra = {
        "Verde": VERDE,
        "Azul": AZUL,
        "Laranja": LARANJA
    }

    cores_raquete = {
        "Preta": PRETO,
        "Azul": AZUL,
        "Vermelha": VERMELHO,
        "Verde": VERDE,
        "Amarela": AMARELO,
        "Rosa": ROSA
    }

    estado_menu = "principal"  # Estados: principal, escolher_quadra, escolher_raquete
    cor_quadra_escolhida = VERDE
    cor_raquete_escolhida = PRETO

    # Raquete para o mouse
    raquete = Raquete(PRETO)

    # Carregar imagem de fundo
    imagem_fundo = carregar_imagem_fundo()

    # Botões do menu principal
    btn_jogar = Botao(largura // 2 - 100, altura // 2 - 50, 200, 60, "JOGAR", VERDE_ESCURO, VERDE)
    btn_sair = Botao(largura // 2 - 100, altura // 2 + 50, 200, 60, "SAIR", VERMELHO, (255, 100, 100))

    # Botões para escolha de quadra
    botoes_quadra = []
    y_pos = altura // 2 - 100
    for nome, cor in cores_quadra.items():
        botoes_quadra.append((Botao(largura // 2 - 100, y_pos, 200, 50, nome, cor, cor), nome))
        y_pos += 70

    # Botões para escolha de raquete
    botoes_raquete = []
    y_pos = altura // 3
    x_pos = largura // 6
    cols = 2
    i = 0
    for nome, cor in cores_raquete.items():
        col = i % cols
        row = i // cols
        x = x_pos + col * 250
        y = y_pos + row * 100
        botoes_raquete.append((Botao(x, y, 200, 50, nome, cor, cor), nome))
        i += 1

    # Iniciar música do menu
    musica_menu.play(-1)  # Loop contínuo

    # Loop do menu
    while True:
        # Capturar posição do mouse
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if estado_menu == "principal":
                    if btn_jogar.foi_clicado(pos_mouse):
                        estado_menu = "escolher_quadra"
                    elif btn_sair.foi_clicado(pos_mouse):
                        pygame.quit()
                        sys.exit()

                elif estado_menu == "escolher_quadra":
                    for botao, nome in botoes_quadra:
                        if botao.foi_clicado(pos_mouse):
                            cor_quadra_escolhida = cores_quadra[nome]
                            estado_menu = "escolher_raquete"

                elif estado_menu == "escolher_raquete":
                    for botao, nome in botoes_raquete:
                        if botao.foi_clicado(pos_mouse):
                            cor_raquete_escolhida = cores_raquete[nome]
                            # Parar música e iniciar jogo
                            musica_menu.stop()
                            return cor_quadra_escolhida, cor_raquete_escolhida

        # Desenhar fundo do menu
        if imagem_fundo:
            # Se a imagem foi carregada com sucesso, use-a como fundo
            tela.blit(imagem_fundo, (0, 0))
        else:
            # Caso contrário, use a cor de fundo padrão
            tela.fill((50, 50, 50))

        # Adicionar uma camada semi-transparente para melhorar a visibilidade dos botões
        superficie_transparente = pygame.Surface((largura, altura), pygame.SRCALPHA)
        superficie_transparente.fill((0, 0, 0, 128))  # Preto com 50% de opacidade
        tela.blit(superficie_transparente, (0, 0))

        if estado_menu == "principal":
            # Desenhar botões
            btn_jogar.verificar_hover(pos_mouse)
            btn_sair.verificar_hover(pos_mouse)
            btn_jogar.desenhar()
            btn_sair.desenhar()

        elif estado_menu == "escolher_quadra":
            # Título
            titulo = fonte_grande.render("ESCOLHA A QUADRA", True, BRANCO)
            tela.blit(titulo, (largura // 2 - titulo.get_width() // 2, altura // 6))

            # Desenhar botões
            for botao, _ in botoes_quadra:
                botao.verificar_hover(pos_mouse)
                botao.desenhar()

        elif estado_menu == "escolher_raquete":
            # Título
            titulo = fonte_grande.render("ESCOLHA SUA RAQUETE", True, BRANCO)
            tela.blit(titulo, (largura // 2 - titulo.get_width() // 2, altura // 6))

            # Desenhar botões
            for botao, nome in botoes_raquete:
                botao.verificar_hover(pos_mouse)
                botao.desenhar()

                # Desenhar exemplo de raquete
                raquete_temp = Raquete(cores_raquete[nome])
                pos_x = botao.rect.x + botao.rect.width + 30
                pos_y = botao.rect.y + botao.rect.height // 2
                raquete_temp.desenhar((pos_x, pos_y))

        # Desenhar raquete seguindo o mouse
        raquete.desenhar(pos_mouse)

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def main():
    # Mostrar menu e obter escolhas
    cor_quadra, cor_raquete = menu_inicial()

    # Iniciar jogo com as escolhas
    clock = pygame.time.Clock()
    bola = Bola()
    torcida = Torcida()
    raquete = Raquete(cor_raquete)
    raquete_adversario = RaqueteAdversario(VERMELHO)  # Criando a raquete adversária
    game_over = False
    tempo = 0

    # Esconder cursor padrão
    pygame.mouse.set_visible(False)

    # Quadra de tênis (linhas simples)
    def desenhar_quadra():
        # Fundo da cor escolhida
        tela.fill(cor_quadra)

        # Linhas da quadra
        pygame.draw.rect(tela, BRANCO, (50, 50, largura - 100, altura - 100), 2)
        pygame.draw.line(tela, BRANCO, (largura // 2, 50), (largura // 2, altura - 50), 2)
        pygame.draw.line(tela, BRANCO, (50, altura // 2), (largura - 50, altura // 2), 2)

        # Zona de rebatida
        pygame.draw.rect(tela, (220, 220, 220), (0, altura - 150, largura, 150), 1)

    # Loop principal do jogo
    while True:
        tempo += 1  # Incrementar tempo para animações
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Processar cliques do mouse
            if evento.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if bola.verificar_clique(pos_mouse):
                    pass

            # Reiniciar jogo quando game over
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r and game_over:
                    # Voltar para o menu inicial
                    pygame.mouse.set_visible(True)
                    return
                elif evento.key == pygame.K_ESCAPE:
                    # Voltar para o menu inicial
                    pygame.mouse.set_visible(True)
                    return

        # Atualizar estado do jogo
        if not game_over:
            # Atualizar raquete adversária
            raquete_adversario.atualizar(bola, bola.nivel)

            # Verificar colisão com raquete adversária antes de mover a bola
            raquete_adversario.verificar_colisao(bola)

            # Mover a bola
            bola.mover()

            # Verificar se o jogo acabou
            if bola.vidas <= 0:
                game_over = True

        # Desenhar na tela
        desenhar_quadra()
        torcida.desenhar(tempo)
        raquete_adversario.desenhar()  # Desenhar raquete adversária
        bola.desenhar()

        # Desenhar raquete no lugar do cursor
        if not game_over:
            raquete.desenhar(pos_mouse)

        # Placar e informações
        pontos_texto = fonte.render(f"Pontos: {bola.pontos}", True, BRANCO)
        vidas_texto = fonte.render(f"Vidas: {bola.vidas}", True, BRANCO)
        nivel_texto = fonte.render(f"Nível: {bola.nivel}", True, BRANCO)
        combo_texto = fonte.render(f"Combo: {bola.combo}", True, BRANCO)

        tela.blit(pontos_texto, (60, 10))
        tela.blit(vidas_texto, (60, 40))
        tela.blit(nivel_texto, (largura - 150, 10))
        tela.blit(combo_texto, (largura - 150, 40))

        # Instruções para voltar ao menu
        menu_texto = fonte_pequena.render("Pressione ESC para voltar ao menu", True, BRANCO)
        tela.blit(menu_texto, (10, altura - 30))

        # Tela de Game Over
        if game_over:
            game_over_surf = fonte_grande.render("GAME OVER", True, VERMELHO)
            pontuacao_final = fonte.render(f"Pontuação Final: {bola.pontos}", True, BRANCO)
            max_combo_texto = fonte.render(f"Combo Máximo: {bola.max_combo}", True, BRANCO)
            reiniciar = fonte.render("Pressione R para voltar ao menu", True, BRANCO)

            tela.blit(game_over_surf, (largura // 2 - game_over_surf.get_width() // 2, altura // 2 - 80))
            tela.blit(pontuacao_final, (largura // 2 - pontuacao_final.get_width() // 2, altura // 2 - 20))
            tela.blit(max_combo_texto, (largura // 2 - max_combo_texto.get_width() // 2, altura // 2 + 20))
            tela.blit(reiniciar, (largura // 2 - reiniciar.get_width() // 2, altura // 2 + 60))

        pygame.display.flip()
        clock.tick(60)

# Permitir reiniciar o jogo várias vezes
if __name__ == "__main__":
    while True:
        main()