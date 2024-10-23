import pygame
import random

# Inicializando o pygame
pygame.init()

# Definindo algumas cores
WHITE = (255, 255, 255)
GREEN = (0,255,0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (192, 192, 192)  # Cor para cartas ocultas
YELLOW = (255, 255, 0)  # Cor para o indicador de seleção

# Definindo o tamanho da tela
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Triple Triad')

# Carregar imagem de fundo
background_image = pygame.image.load('resources/background.png').convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Carregar imagem do título
title_image = pygame.image.load('resources/title2.png').convert_alpha()
title_rect = title_image.get_rect(center=(SCREEN_WIDTH // 2, 100))

# Carregando e Tocando música de fundo
pygame.mixer.music.load('resources/theme-loop.wav')

# Definindo o tamanho das cartas e do tabuleiro
CARD_WIDTH = 100
CARD_HEIGHT = 120
BOARD_SIZE = 3
BOARD_MARGIN = 10

# Calculando as posições para centralizar o tabuleiro na tela
board_width = (CARD_WIDTH + BOARD_MARGIN) * BOARD_SIZE - BOARD_MARGIN
board_height = (CARD_HEIGHT + BOARD_MARGIN) * BOARD_SIZE - BOARD_MARGIN
BOARD_X = (SCREEN_WIDTH - board_width) // 2
BOARD_Y = (SCREEN_HEIGHT - board_height) // 2 + 50  # Ajustar para o título

# Posições para exibição das cartas dos jogadores
PLAYER1_AREA_X = BOARD_MARGIN
PLAYER1_AREA_Y = BOARD_MARGIN + 100

PLAYER2_AREA_X = SCREEN_WIDTH - CARD_WIDTH - BOARD_MARGIN
PLAYER2_AREA_Y = BOARD_MARGIN + 100

# Definindo uma fonte para o texto
font = pygame.font.Font(None, 36)

# Definindo uma classe para as Cartas
class Card:
    def __init__(self, top, bottom, left, right, owner):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.owner = owner  # 0 para jogador 1, 1 para jogador 2
        self.placed = False
        self.visible = True  # As cartas são inicialmente visíveis

    def draw(self, x, y, selected=False, hover=False):
        # Definindo a cor da carta
        color = BLUE if self.owner == 0 else RED
        pygame.draw.rect(screen, color, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), 3)

        # Hover effect
        if hover:
            pygame.draw.rect(screen, YELLOW, (x, y, CARD_WIDTH, CARD_HEIGHT), 3)

        # Desenhar os valores das cartas, se visíveis
        if self.visible or self.placed:  # Se a carta está no tabuleiro, sempre visível
            text_top = font.render(self.get_value_display(self.top), True, WHITE)
            text_bottom = font.render(self.get_value_display(self.bottom), True, WHITE)
            text_left = font.render(self.get_value_display(self.left), True, WHITE)
            text_right = font.render(self.get_value_display(self.right), True, WHITE)

            screen.blit(text_top, (x + CARD_WIDTH // 2 - 10, y + 10))
            screen.blit(text_bottom, (x + CARD_WIDTH // 2 - 10, y + CARD_HEIGHT - 40))
            screen.blit(text_left, (x + 10, y + CARD_HEIGHT // 2 - 10))
            screen.blit(text_right, (x + CARD_WIDTH - 30, y + CARD_HEIGHT // 2 - 10))

        # Se a carta está selecionada, desenhar um indicador
        if selected:
            pygame.draw.rect(screen, YELLOW, (x - 5, y - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 3)

    def get_value_display(self, value):
        return 'A' if value == 10 else str(value)

# Gerar cartas aleatórias (apenas exemplo)
def generate_random_card(owner):
    return Card(random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), owner)

# Classe para o Tabuleiro
class Board:
    def __init__(self):
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def place_card(self, card, row, col, players_scores):
        if self.grid[row][col] is None:
            self.grid[row][col] = card
            card.placed = True
            card.visible = True  # As cartas no tabuleiro sempre serão visíveis
            self.capture_adjacent_cards(card, row, col, players_scores)
            return True
        return False

    def capture_adjacent_cards(self, card, row, col, players_scores):
        directions = [(-1, 0, 'top', 'bottom'), (1, 0, 'bottom', 'top'), (0, -1, 'left', 'right'), (0, 1, 'right', 'left')]

        for d_row, d_col, card_side, adjacent_side in directions:
            adj_row, adj_col = row + d_row, col + d_col
            if 0 <= adj_row < BOARD_SIZE and 0 <= adj_col < BOARD_SIZE:
                adjacent_card = self.grid[adj_row][adj_col]
                if adjacent_card and adjacent_card.owner != card.owner:
                    card_value = getattr(card, card_side)
                    adjacent_value = getattr(adjacent_card, adjacent_side)
                    if card_value > adjacent_value:
                        adjacent_card.owner = card.owner
                        players_scores[card.owner] += 1
                        players_scores[1 - card.owner] -= 1
                        self.combo_capture(adjacent_card, adj_row, adj_col, players_scores)

    def combo_capture(self, card, row, col, players_scores):
        directions = [(-1, 0, 'top', 'bottom'), (1, 0, 'bottom', 'top'), (0, -1, 'left', 'right'), (0, 1, 'right', 'left')]
        to_check = [(row, col)]

        while to_check:
            current_row, current_col = to_check.pop()
            
            for d_row, d_col, card_side, adjacent_side in directions:
                adj_row, adj_col = current_row + d_row, current_col + d_col
                if 0 <= adj_row < BOARD_SIZE and 0 <= adj_col < BOARD_SIZE:
                    adjacent_card = self.grid[adj_row][adj_col]
                    if adjacent_card and adjacent_card.owner != card.owner:
                        card_value = getattr(card, card_side)
                        adjacent_value = getattr(adjacent_card, adjacent_side)
                        if card_value > adjacent_value:
                            # Captura a carta
                            adjacent_card.owner = card.owner
                            players_scores[card.owner] += 1
                            players_scores[1 - card.owner] -= 1
                            # Adiciona a carta adjacente à lista para verificar suas adjacentes
                            to_check.append((adj_row, adj_col))
    def draw(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = col * (CARD_WIDTH + BOARD_MARGIN) + BOARD_X
                y = row * (CARD_HEIGHT + BOARD_MARGIN) + BOARD_Y
                if self.grid[row][col]:
                    self.grid[row][col].draw(x, y)
                else:
                    pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), 3)

    def is_full(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.grid[row][col] is None:
                    return False
        return True

# Função que controla a visibilidade das cartas no início de cada turno
def update_visibility_based_on_turn(player_cards, opponent_cards):
    # Calcula o número de cartas a serem ocultadas com base no número de cartas do oponente
    if len(opponent_cards) == 5:
        cards_to_hide = 2
    elif len(opponent_cards) == 4:
        cards_to_hide = 1
    else:
        cards_to_hide = 0  # Se o oponente tiver 3 ou menos cartas, nenhuma é ocultada

    # Torna todas as cartas do jogador atual visíveis
    for card in player_cards:
        card.visible = True

    # Oculta as cartas do oponente conforme necessário, apenas se ainda não foram colocadas
    for i, card in enumerate(opponent_cards):
        if not card.placed:
            if i < cards_to_hide:
                card.visible = False  # Oculta as primeiras cartas
            else:
                card.visible = True  # Mantém o restante visível

# Desenhar cartas dos jogadores
def draw_player_cards(player_cards, x_start, y_start, selected_card=None):
    for i, card in enumerate(player_cards):
        card_x = x_start
        card_y = y_start + i * (CARD_HEIGHT + 10)
        if not card.placed:
            hover = card_x <= pygame.mouse.get_pos()[0] <= card_x + CARD_WIDTH and card_y <= pygame.mouse.get_pos()[1] <= card_y + CARD_HEIGHT
            selected = card == selected_card
            card.draw(card_x, card_y, selected=selected, hover=hover)

# Função para desenhar a tela de fim de jogo
def draw_game_over_screen(winner):
    screen.fill(BLACK)
    
    # Renderizar o texto de fim de jogo
    game_over_text = font.render("Fim de jogo!", True, WHITE)
    if game_over_text:  # Verifica se o texto foi renderizado corretamente
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

    # Renderizar o texto do vencedor ou empate
    if winner is not None:
        winner_text = font.render(f"Vencedor: Jogador {winner + 1}", True, WHITE)
    else:
        winner_text = font.render("Empate", True, WHITE)
    
    if winner_text:  # Verifica se o texto foi renderizado corretamente
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2))
    
    # Definir os botões de reinício e saída
    restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 30, 140, 50)
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 90, 140, 50)
    
    # Desenhar botão de reiniciar
    pygame.draw.rect(screen, GREEN, restart_button)
    
    # Renderizar o texto de reiniciar
    restart_text = font.render("Reiniciar", True, BLACK)
    if restart_text:  # Verifica se o texto foi renderizado corretamente
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

    pygame.display.flip()

# Função principal do jogo
def main():
    clock = pygame.time.Clock()
    pygame.mixer.music.play(-1)
    # Inicializar variáveis
    board = Board()
    player1_cards = [generate_random_card(0) for _ in range(5)]
    player2_cards = [generate_random_card(1) for _ in range(5)]
    player_turn = 0  # 0 = jogador 1, 1 = jogador 2
    selected_card = None
    selected_row, selected_col = None, None
    players_scores = [5, 5]  # Ambos jogadores começam com 5 pontos

    running = True
    game_over = False

    while running:
        
        screen.fill(BLACK)

        # Desenhar imagem de fundo
        screen.blit(background_image, (0, 0))

        # Desenhar título
        screen.blit(title_image, title_rect)

        # Desenhar o tabuleiro
        board.draw()

        if not game_over:
            # Atualizar visibilidade das cartas baseado no turno
            if player_turn == 0:
                update_visibility_based_on_turn(player1_cards, player2_cards)
            else:
                update_visibility_based_on_turn(player2_cards, player1_cards)

            # Desenhar cartas dos jogadores
            draw_player_cards(player1_cards, PLAYER1_AREA_X, PLAYER1_AREA_Y, selected_card if player_turn == 0 else None)
            draw_player_cards(player2_cards, PLAYER2_AREA_X, PLAYER2_AREA_Y, selected_card if player_turn == 1 else None)

            # Desenhar placar
            score_text = font.render(f'Player 1: {players_scores[0]}  Player 2: {players_scores[1]}', True, BLACK)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT - 50))

            # Desenhar indicador de turno
            turn_text = font.render(f"Turno do Jogador {player_turn + 1}", True, BLACK)
            screen.blit(turn_text, (SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 680))

            # Definindo a cor do indicador com base no jogador
            indicator_color = BLUE if player_turn == 0 else RED
            pygame.draw.rect(screen, indicator_color, 
                            (SCREEN_WIDTH // 2 - 100, 705, 200, 5))  # Retângulo indicador

            # Eventos de controle
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Selecionar uma carta da mão do jogador
                    if player_turn == 0:
                        for i, card in enumerate(player1_cards):
                            card_x = PLAYER1_AREA_X
                            card_y = PLAYER1_AREA_Y + i * (CARD_HEIGHT + 10)
                            if card_x <= pygame.mouse.get_pos()[0] <= card_x + CARD_WIDTH and card_y <= pygame.mouse.get_pos()[1] <= card_y + CARD_HEIGHT:
                                selected_card = card
                                break
                    else:
                        for i, card in enumerate(player2_cards):
                            card_x = PLAYER2_AREA_X
                            card_y = PLAYER2_AREA_Y + i * (CARD_HEIGHT + 10)
                            if card_x <= pygame.mouse.get_pos()[0] <= card_x + CARD_WIDTH and card_y <= pygame.mouse.get_pos()[1] <= card_y + CARD_HEIGHT:
                                selected_card = card
                                break
                    # Selecionar uma posição no tabuleiro
                    if selected_card:
                        for row in range(BOARD_SIZE):
                            for col in range(BOARD_SIZE):
                                x = col * (CARD_WIDTH + BOARD_MARGIN) + BOARD_X
                                y = row * (CARD_HEIGHT + BOARD_MARGIN) + BOARD_Y
                                if x <= pygame.mouse.get_pos()[0] <= x + CARD_WIDTH and y <= pygame.mouse.get_pos()[1] <= y + CARD_HEIGHT:
                                    if board.place_card(selected_card, row, col, players_scores):
                                        selected_card = None
                                        selected_row, selected_col = row, col
                                        player_turn = 1 - player_turn  # Trocar o turno
                                        break

            # Verificar se o tabuleiro está cheio (fim de jogo)
            if board.is_full():
                pygame.mixer.music.stop()  # Para a música
                game_over = True  # Ativa a tela de fim de jogo
                
                # Determinar o vencedor
                if players_scores[0] > players_scores[1]:
                    winner = 0  # Jogador 1 venceu
                elif players_scores[0] < players_scores[1]:
                    winner = 1  # Jogador 2 venceu
                else:
                    winner = None  # Empate


        else:
            draw_game_over_screen(winner)  # Passa o vencedor para a função
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 10, 140, 50)
                    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 70, 140, 50)

                    if restart_button.collidepoint(mouse_pos):
                        main()  # Reinicia o jogo
                    elif quit_button.collidepoint(mouse_pos):
                        running = False  # Sai do jogo

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()