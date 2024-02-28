
import pygame
from shobu import ShobuAction, ShobuState, ShobuGame
from agent import Agent


SCREEN_WIDTH        = 800
SCREEN_HEIGHT       = 800
PLAYER_RADIUS       = 25
SQUARE_SIZE         = 75
GAP_BOARD           = 100
OFFSET_BOARD        = 50

BACKGROUND_COLOR    = (125, 150, 200)
BOARD_LIGHT_COLOR   = (180, 180, 180)
BOARD_DARK_COLOR    = (90, 90, 90)
LINE_COLOR          = (0, 0, 0)
PLAYER_WHITE_COLOR  = (255, 255, 255)
PLAYER_BLACK_COLOR  = (0, 0, 0)
HIGHLIGHT_COLOR     = (255, 0, 0)

screen = None
is_paused = False


def init_pygame():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Shobu")


def draw_board(top_left_corner, color_line, color_board):
    pygame.draw.rect(screen, color_board, (top_left_corner[0], top_left_corner[1], SQUARE_SIZE * 4, SQUARE_SIZE * 4))
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(screen, color_line, (top_left_corner[0] + SQUARE_SIZE * i, top_left_corner[1] + SQUARE_SIZE * j, SQUARE_SIZE, SQUARE_SIZE), 1)


def draw_piece(board_index, piece_index, color):
    
    if board_index < 0 or board_index > 3:
        raise Exception(f"Board index {board_index} is invalid")
    if piece_index < 0 or piece_index > 15:
        raise Exception(f"Piece index {piece_index} is invalid")

    x = OFFSET_BOARD + (GAP_BOARD + SQUARE_SIZE * 4) * (board_index % 2) + SQUARE_SIZE * (piece_index % 4) + SQUARE_SIZE/2
    y = OFFSET_BOARD + (GAP_BOARD + SQUARE_SIZE * 4) * (abs((board_index // 2) - 1)) + SQUARE_SIZE * (abs((piece_index // 4) - 3)) + SQUARE_SIZE/2
    pygame.draw.circle(screen, color, (x, y), PLAYER_RADIUS)


def draw_state(state: ShobuState):
    # draw the boards
    draw_board((OFFSET_BOARD, OFFSET_BOARD), LINE_COLOR, BOARD_LIGHT_COLOR)
    draw_board((OFFSET_BOARD, OFFSET_BOARD + GAP_BOARD + SQUARE_SIZE * 4), LINE_COLOR, BOARD_LIGHT_COLOR)
    draw_board((OFFSET_BOARD + GAP_BOARD + SQUARE_SIZE * 4, OFFSET_BOARD), LINE_COLOR, BOARD_DARK_COLOR)
    draw_board((OFFSET_BOARD + GAP_BOARD + SQUARE_SIZE * 4, OFFSET_BOARD + GAP_BOARD + SQUARE_SIZE * 4), LINE_COLOR, BOARD_DARK_COLOR)
    
    for i_b in range(4):
        white_stones, black_stones = state.board[i_b]
        for w_stone in white_stones:
            draw_piece(i_b, w_stone, PLAYER_WHITE_COLOR)
        for b_stone in black_stones:
            draw_piece(i_b, b_stone, PLAYER_BLACK_COLOR)

def highlight_square(board_index, square_index, color):
    x = OFFSET_BOARD + (GAP_BOARD + SQUARE_SIZE * 4) * board_index[1] + SQUARE_SIZE * square_index[1]
    y = OFFSET_BOARD + (GAP_BOARD + SQUARE_SIZE * 4) * board_index[0] + SQUARE_SIZE * square_index[0]
    pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE), 5)


def show_text(text: str, color=(0, 0, 0)):
    font = pygame.font.SysFont("Arial", 50)
    surface = font.render(text, True, color)
    x = SCREEN_WIDTH/2 - surface.get_width()/2
    y = SCREEN_HEIGHT/2 - surface.get_height()/2
    screen.blit(surface, (x, y))


def convert_click_to_square_index(pos: tuple[int, int], board_index: tuple[int, int]):
    x = pos[0]
    y = pos[1]

    top_left_corner = (OFFSET_BOARD + (GAP_BOARD + SQUARE_SIZE * 4) * board_index[1], OFFSET_BOARD + (GAP_BOARD + SQUARE_SIZE * 4) * board_index[0])
    x = x - top_left_corner[0]
    y = y - top_left_corner[1]
    for i in range(4):
        for j in range(4):
            if i * SQUARE_SIZE <= x <= (i+1) * SQUARE_SIZE and j * SQUARE_SIZE <= y <= (j+1) * SQUARE_SIZE:
                return (j, i)
    return None


def convert_click_to_board_index(pos: tuple[int, int]):
    x = pos[0]
    y = pos[1]

    if OFFSET_BOARD <= x <= OFFSET_BOARD + 4 * SQUARE_SIZE:
        if OFFSET_BOARD <= y <= OFFSET_BOARD + 4 * SQUARE_SIZE:
            return (0, 0)
        elif OFFSET_BOARD + SQUARE_SIZE * 4 + GAP_BOARD <= y <= OFFSET_BOARD + SQUARE_SIZE * 4 + GAP_BOARD + 4 * SQUARE_SIZE:
            return (1, 0)
        else:
            return None
    
    elif OFFSET_BOARD + SQUARE_SIZE * 4 + GAP_BOARD <= x <= OFFSET_BOARD + SQUARE_SIZE * 4 + GAP_BOARD + 4 * SQUARE_SIZE:
        if OFFSET_BOARD <= y <= OFFSET_BOARD + 4 * SQUARE_SIZE:
            return (0, 1)
        elif OFFSET_BOARD + SQUARE_SIZE * 4 + GAP_BOARD <= y <= OFFSET_BOARD + SQUARE_SIZE * 4 + GAP_BOARD + 4 * SQUARE_SIZE:
            return (1, 1)
        else:
            return None
    
    else:
        return None


def convert_click_to_position():
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            board_idx = convert_click_to_board_index(mouse_pos)
            if board_idx is None:
                return None
            square_idx = convert_click_to_square_index(mouse_pos, board_idx)
            if square_idx is None:
                return None
            return (board_idx, square_idx)
    return None


def get_human_move(state):
    highlight_squares = []

    # get stone for passive move
    passive_stone = None
    passive_board = None
    passive_board_id = None
    passive_stone_id = None
    print("Select passive stone")
    while passive_stone is None and passive_board is None:
        pos = convert_click_to_position()
        if pos is not None:
            board_idx, piece_idx = pos

            board_id = (abs(board_idx[0] - 1)) * 2 + board_idx[1]
            piece_id = (abs(piece_idx[0] - 3)) * 4 + piece_idx[1]

            if (board_id, piece_id) in [(b, p) for b, p, _, _, _, _ in state.actions]:
                passive_stone = piece_idx
                passive_board = board_idx
                passive_board_id = board_id
                passive_stone_id = piece_id


                
        run = update_ui(state, text="Select passive stone")
        if run == -1:
            return None
        if run == -2:
            print("move reset")
            return -2
    highlight_squares.append((passive_board, passive_stone))

    # get direction and length for passive move
    direction = None
    length = None
    print("Select target square for passive move")
    while direction is None and length is None:
        pos = convert_click_to_position()
        if pos is not None:
            board_idx, piece_idx = pos

            board_id = (abs(board_idx[0] - 1)) * 2 + board_idx[1]
            piece_id = (abs(piece_idx[0] - 3)) * 4 + piece_idx[1]

            dir = (piece_id - passive_stone_id)
            le = 1
            if abs(dir) in [1, 3, 4, 5]:
                le = 1
            elif abs(dir) in [2, 6, 8, 10]:
                dir //= 2
                le = 2
            else:
                continue
            if board_id == passive_board_id and (passive_board_id, passive_stone_id, dir, le) in [(b, p, d, l) for b, p, _, _, d, l in state.actions]:
                direction = dir
                length = le
        run = update_ui(state, text="Select target passive move", highlight=highlight_squares)
        if run == -1:
            return None
        if run == -2:
            print("move reset")
            return -2
    highlight_squares.append((board_idx, piece_idx))

    # get stone for active move
    active_stone = None 
    active_board = None
    active_board_id = None
    active_stone_id = None
    print("Select active stone")
    while active_stone is None and active_board is None:
        pos = convert_click_to_position()
        if pos is not None:
            board_idx, piece_idx = pos
            
            board_id = (abs(board_idx[0] - 1)) * 2 + board_idx[1]
            piece_id = (abs(piece_idx[0] - 3)) * 4 + piece_idx[1]

            if (passive_board_id, passive_stone_id, board_id, piece_id, direction, length) in state.actions:
                active_stone = piece_idx
                active_board = board_idx
                active_board_id = board_id
                active_stone_id = piece_id
        run = update_ui(state, text="Select active stone", highlight=highlight_squares)
        if run == -1:
            return None
        if run == -2:
            return -2
    highlight_squares.append((active_board, active_stone))

    return ShobuAction(passive_board_id, passive_stone_id, active_board_id, active_stone_id, direction, length)

def update_ui(state: ShobuState, text: str = None, highlight: list = []):
    global is_paused
    screen.fill(BACKGROUND_COLOR)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return -1
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            is_paused = not is_paused
        if pressed[pygame.K_ESCAPE]:
            pygame.quit()
            return -1
        if pressed[pygame.K_u]:
            return -2

    draw_state(state)

    for board_idx, square_idx in highlight:
        highlight_square(board_idx, square_idx, HIGHLIGHT_COLOR)

    if is_paused:
        show_text("PAUSED")

    game = ShobuGame()
    if game.is_terminal(state):
        
        if game.utility(state, 0) == 1:
            show_text(f"Winner: {'White'}")
        elif game.utility(state, 0) == -1:
            show_text(f"Winner: {'Black'}")
        else:
            show_text("Draw...")
    if text is not None:
        color = (255, 255, 255) if state.to_move == 0 else (0, 0, 0)
        show_text(text, color=color)

    pygame.display.update()

    if is_paused or game.is_terminal(state):
        return 0
    return 1



class HumanAgent(Agent):

    def __init__(self, player):
        self.player = player

    def play(self, state, remaining_time):
        return get_human_move(state)

