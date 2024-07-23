import pygame
import sys
from button import Button
from queue import PriorityQueue
import math
import random

# Initialize
pygame.init()

# Set up the display
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("First to Neigh Neigh")

# Background image
BG = pygame.image.load("asset/bg.png")

# Load piece images
knight_img = pygame.image.load("asset/p2.png")
goal_img = pygame.image.load("asset/goal.png")

click_sound = pygame.mixer.Sound("asset/click.mp3")
win_sound = pygame.mixer.Sound("asset/neigh.mp3")

# Font
def get_font(size):
    return pygame.font.Font("asset/font1.ttf", size)

# Function to draw the board
def draw_board(player_moves, ai_moves):
    board_size = 8
    tile_size = 80
    total = board_size * tile_size
    
    offset_x = (screen.get_width() - total) // 2
    offset_y = (screen.get_height() - total) // 2

    for row in range(board_size):
        for col in range(board_size):
            pos = (col, row)
            if pos in player_moves:
                color = (255, 0, 0)  # Red for player moves
            elif pos in ai_moves:
                color = (0, 0, 255)  # Blue for AI moves
            elif (row + col) % 2 == 0:
                color = (200, 200, 200)
            else:
                color = (50, 50, 50)
            pygame.draw.rect(screen, color, (offset_x + col * tile_size, offset_y + row * tile_size, tile_size, tile_size))
    
    return offset_x, offset_y, tile_size

# Function to get board coordinates from pixel positions
def get_board_coords(pos, offset_x, offset_y, tile_size):
    x, y = pos
    col = (x - offset_x) // tile_size
    row = (y - offset_y) // tile_size
    return col, row

# Function to check if a move is valid for a knight considering visited tiles
def is_valid_knight_move(start, end, visited):
    dx = abs(start[0] - end[0])
    dy = abs(start[1] - end[1])
    if (dx, dy) in [(1, 2), (2, 1)]:
        
        if 0 <= end[0] < 8 and 0 <= end[1] < 8 and end not in visited:
            return True
    return False

# A* search algorithm
def a_star_search(start, goal, visited):
    if start == goal:
        return [start] 

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        _, current = frontier.get()

        if current == goal:
            break

        for dx, dy in [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]:
            next = (current[0] + dx, current[1] + dy)
            if 0 <= next[0] < 8 and 0 <= next[1] < 8 and next not in visited:
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put((priority, next))
                    came_from[next] = current

    # Reconstruct path
    current = goal
    path = []
    while current != start:
        path.append(current)
        if current in came_from:
            current = came_from[current]
        else:
            break
    path.reverse()

    return path

def minimax(position, goal_pos, depth, alpha, beta, maximizing_player, visited):
    if depth == 0 or position == goal_pos:
        return heuristic(position, goal_pos), position

    possible_moves = generate_knight_moves(position)

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in possible_moves:
            if move in visited:
                continue
            path_to_goal = a_star_search(move, goal_pos, visited)
            move_eval = -len(path_to_goal) if path_to_goal else float('-inf')
            eval = move_eval

            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in possible_moves:
            if move in visited:
                continue
            path_to_goal = a_star_search(move, goal_pos, visited)
            move_eval = len(path_to_goal) if path_to_goal else float('inf')
            eval = move_eval

            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# Heuristic function
def heuristic(position, goal_pos):
    dx = position[0] - goal_pos[0]
    dy = position[1] - goal_pos[1]
    return math.sqrt(dx ** 2 + dy ** 2)

# Generate all possible knight moves from a position
def generate_knight_moves(position):
    x, y = position
    moves = [
        (x + 1, y + 2), (x + 2, y + 1), (x - 1, y + 2), (x - 2, y + 1),
        (x + 1, y - 2), (x + 2, y - 1), (x - 1, y - 2), (x - 2, y - 1)
    ]
    return [(mx, my) for mx, my in moves if 0 <= mx < 8 and 0 <= my < 8]

# Helper function to convert board coordinates to chess notation
def to_chess_notation(pos):
    cols = "ABCDEFGH"
    rows = "87654321"
    col, row = pos
    return f"{cols[col]}{rows[row]}"

# Show the win message and ask for a new game or exit
def show_win_message(winner):
    win_sound.play()
    print(f"{winner} wins!")
    while True:
        
        message_text = get_font(75).render(f"{winner} wins the game!", True, "White")
        message_rect = message_text.get_rect(center=(640, 200))
        screen.blit(message_text, message_rect)

        play_again_btn = Button(image=None, pos=(640, 400), text_input="PLAY AGAIN", font=get_font(75), base_color="White", hovering_color="#FFCA03")
        exit_btn = Button(image=None, pos=(640, 550), text_input="EXIT", font=get_font(75), base_color="White", hovering_color="#CF3030")
        win_back_btn = Button(image=None, pos=(1150, 50), text_input="BACK", font=get_font(75), base_color="White", hovering_color="#CF3030")

        mouse_pos = pygame.mouse.get_pos()

        for button in [play_again_btn, win_back_btn, exit_btn]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                click_sound.play()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_btn.checkInput(mouse_pos):
                    click_sound.play()
                    return True
                elif win_back_btn.checkInput(mouse_pos):
                    click_sound.play()
                    main_menu()
                elif exit_btn.checkInput(mouse_pos):
                    click_sound.play()
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def is_white_tile(pos):
    x, y = pos
    return (x + y) % 2 == 0

def generate_position_ranges():
    knight_pos_white = []
    goal_pos_white = [] 
    knight_pos_black = [] 
    goal_pos_black = [] 
    
    for x in range(8):
        for y in range(8):
            pos = (x, y)
            if is_white_tile(pos):
                knight_pos_white.append(pos)
                goal_pos_white.append(pos)
            else:
                knight_pos_black.append(pos)
                goal_pos_black.append(pos)
                
    return knight_pos_white, knight_pos_black, goal_pos_white, goal_pos_black

knight_pos_white, knight_pos_black, goal_pos_white, goal_pos_black = generate_position_ranges()

# Play game function
def play(first_turn):
    while True:
        if first_turn == "AI":
            knight_pos = random.choice(knight_pos_white)  # Start position for AI
            goal_pos = random.choice(goal_pos_black) # Goal position
        else:
            knight_pos = random.choice(knight_pos_black)  # Start position for player
            goal_pos = random.choice(goal_pos_black)   # Goal position

        
        if knight_pos != goal_pos:
            
            if not any(is_valid_knight_move(knight_pos, goal_pos, set()) for dx, dy in generate_knight_moves((0,0))):
                break 

    current_turn = first_turn
    player_moves = {knight_pos} if first_turn == "Player" else set()
    ai_moves = {knight_pos} if first_turn == "AI" else set()
    all_moves = {knight_pos}

    while True:
        play_mouse_pos = pygame.mouse.get_pos()

        screen.fill("black")
        offset_x, offset_y, tile_size = draw_board(player_moves, ai_moves)

        # Draw the goal
        screen.blit(goal_img, (offset_x + goal_pos[0] * tile_size, offset_y + goal_pos[1] * tile_size))
        # Draw the knight
        screen.blit(knight_img, (offset_x + knight_pos[0] * tile_size, offset_y + knight_pos[1] * tile_size))

        play_back = Button(image=None, pos=(1150, 50), text_input="BACK", font=get_font(75), base_color="White", hovering_color="#CF3030")
        play_back.changeColor(play_mouse_pos)
        play_back.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_back.checkInput(play_mouse_pos):
                    main_menu()
                else:
                    if current_turn == "Player":
                        board_pos = get_board_coords(play_mouse_pos, offset_x, offset_y, tile_size)
                        if board_pos not in all_moves and is_valid_knight_move(knight_pos, board_pos, all_moves):
                            knight_pos = board_pos
                            player_moves.add(knight_pos)
                            all_moves.add(knight_pos)
                            click_sound.play()
                            if knight_pos == goal_pos:
                                if show_win_message("Player"):
                                    play(first_turn)
                                else:
                                    return
                            current_turn = "AI"
                            print(f"Player moved to {knight_pos}")
                    elif current_turn == "AI":
                        _, best_move = minimax(knight_pos, goal_pos, 3, float('-inf'), float('inf'), True, all_moves)
                        if best_move and is_valid_knight_move(knight_pos, best_move, all_moves):
                            knight_pos = best_move
                            ai_moves.add(knight_pos)
                            all_moves.add(knight_pos)
                            click_sound.play()
                            
                            screen.fill("black")
                            offset_x, offset_y, tile_size = draw_board(player_moves, ai_moves)
                            screen.blit(goal_img, (offset_x + goal_pos[0] * tile_size, offset_y + goal_pos[1] * tile_size))
                            screen.blit(knight_img, (offset_x + knight_pos[0] * tile_size, offset_y + knight_pos[1] * tile_size))
                            pygame.display.update()
                            if knight_pos == goal_pos:
                                if show_win_message("AI"):
                                    play(first_turn)
                                else:
                                    return
                            current_turn = "Player"
                            print(f"AI moved to {knight_pos}")

        # Check for no legal moves
        player_legal_moves = [move for move in generate_knight_moves(knight_pos) if move not in all_moves]
        if not player_legal_moves and current_turn == "Player":
            if show_win_message("AI"):
                play(first_turn)
            else:
                return

        ai_legal_moves = [move for move in generate_knight_moves(knight_pos) if move not in all_moves]
        if not ai_legal_moves and current_turn == "AI":
            if show_win_message("Player"):
                play(first_turn)
            else:
                return

        # label
        font = get_font(20)
        ai_label = font.render("AI MOVES", True, "White")
        player_label = font.render("PLAYER MOVES", True, "White")

        screen.blit(ai_label, (80, 130))
        screen.blit(player_label, (screen.get_width() - 220, 130))
        
        font = get_font(20)
        for i, move in enumerate(player_moves):
            move_text = font.render(to_chess_notation(move), True, "White")
            screen.blit(move_text, (screen.get_width() - 150, 180 + i * 25))

        for i, move in enumerate(ai_moves):
            move_text = font.render(to_chess_notation(move), True, "White")
            screen.blit(move_text, (100, 180 + i * 25))

        pygame.display.update()

# Help function
def help():
    while True:
        help_mouse_pos = pygame.mouse.get_pos()

        screen.fill("#F2EEE3")

        help_text = get_font(75).render("GAME RULES", True, "#4C3232")
        help_rect = help_text.get_rect(center=(640, 100))
        screen.blit(help_text, help_rect)
        
        rules = [
            "Tiles that have been previously visited cannot be stepped on again.",
            "Each move must follow the knight's move pattern from chess.",
            "The first player to reach the goal tile is the winner.",
            "If a player has no legal moves left, they lose the game."
        ]

        font = get_font(30)
        spacing =100 
        for i, rule in enumerate(rules):
            rule_text = font.render(rule, True, "#8B7E74")
            rule_rect = rule_text.get_rect(center=(640, 200 + i * spacing))
            screen.blit(rule_text, rule_rect)

        # Back Button
        help_back = Button(image=None, pos=(640, 600), text_input="BACK", font=get_font(45), base_color="#F98903", hovering_color="#CF3030")
        help_back.changeColor(help_mouse_pos)
        help_back.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if help_back.checkInput(help_mouse_pos):
                    click_sound.play()
                    main_menu()

        pygame.display.update()

# Main menu
def main_menu():
    while True:
        screen.blit(BG, (0, 0))
        menu_mouse_pos = pygame.mouse.get_pos()

        menu_text = get_font(100).render("First to", True, "#c06c00")
        menu_rect = menu_text.get_rect(center=(640, 100))
        screen.blit(menu_text, menu_rect)

        menu_text2 = get_font(100).render("Neigh Neigh", True, "#c06c00")
        menu_rect2 = menu_text2.get_rect(center=(640, 200))
        screen.blit(menu_text2, menu_rect2)
        
        play_btn = Button(image=pygame.image.load("asset/bt2.png"), pos=(640, 350), text_input="PLAY GAME", font=get_font(75), base_color="#c06c00", hovering_color="#FFC60B")
        help_btn = Button(image=pygame.image.load("asset/bt1.png"), pos=(640, 500), text_input="HELP", font=get_font(75), base_color="#c06c00", hovering_color="#FDA769")
        exit_btn = Button(image=pygame.image.load("asset/bt2.png"), pos=(640, 650), text_input="EXIT GAME", font=get_font(75), base_color="#c06c00", hovering_color="#CF3030")

        screen.blit(menu_text, menu_rect)

        for button in [play_btn, help_btn, exit_btn]:
            button.changeColor(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.checkInput(menu_mouse_pos):
                    click_sound.play()
                    choose_first_player()
                elif help_btn.checkInput(menu_mouse_pos):
                    click_sound.play()
                    help()
                elif exit_btn.checkInput(menu_mouse_pos):
                    click_sound.play()
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def choose_first_player():
    while True:
        screen.fill("black")
        choose_text = get_font(75).render("Who moves first?", True, "White")
        choose_rect = choose_text.get_rect(center=(640, 100))
        screen.blit(choose_text, choose_rect)

        player_first_btn = Button(image=None, pos=(640, 300), text_input="Player", font=get_font(75), base_color="White", hovering_color="#FFC60B")
        ai_first_btn = Button(image=None, pos=(640, 400), text_input="AI", font=get_font(75), base_color="White", hovering_color="#FFC60B")
        back_btn = Button(image=None, pos=(640, 550), text_input="BACK", font=get_font(75), base_color="White", hovering_color="#CF3030")

        mouse_pos = pygame.mouse.get_pos()

        for button in [player_first_btn, ai_first_btn, back_btn]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player_first_btn.checkInput(mouse_pos):
                    click_sound.play()
                    play("Player")
                elif ai_first_btn.checkInput(mouse_pos):
                    click_sound.play()
                    play("AI")
                elif back_btn.checkInput(mouse_pos):
                    click_sound.play()
                    main_menu()

        pygame.display.update()

main_menu()