import random, time, pygame, sys
from pygame.locals import *

fps = 25
window_width = 640
window_height = 480
box_size = 20
board_width = 10
board_height = 20
blank = '.'

move_side_ways_freq = 0.15
move_down_freq = 0.1

x_margin = int((window_width - board_width * box_size) / 2)
top_margin = window_height - (board_height * box_size) - 5

WHITE = (255, 255, 255)
GRAY = (185, 185, 185)
BLACK = (0, 0, 0)
RED = (155, 0, 0)
LIGHTRED = (175, 20, 20)
GREEN = ( 0, 155, 0)
LIGHTGREEN = ( 20, 175, 20)
BLUE = ( 0, 0, 155)
LIGHTBLUE = ( 20, 20, 175)
YELLOW = (155, 155, 0)
LIGHTYELLOW = (175, 175, 20)

border_color = BLUE
bg_color = BLACK
text_color = WHITE
text_shadow_color = GRAY
colors = (BLUE, GREEN, RED, YELLOW)
light_colors = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(colors) == len(light_colors) #each colors must have light colors

template_width = 5
template_height = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

shapes = {
    'S': S_SHAPE_TEMPLATE,
    'Z': Z_SHAPE_TEMPLATE,
    'J': J_SHAPE_TEMPLATE,
    'L': L_SHAPE_TEMPLATE,
    'I': I_SHAPE_TEMPLATE,
    'O': O_SHAPE_TEMPLATE,
    'T': T_SHAPE_TEMPLATE
}

def main():
    global fps_clock, display_surf, basic_font, big_font
    pygame.init()
    fps_clock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((window_width, window_height))
    basic_font = pygame.font.SysFont("timesnewroman", 18)
    big_font = pygame.font.SysFont("timesnewroman", 100)
    pygame.display.set_caption('Tetris')

    show_text_screen('Tetris')
    while True: #game loop
        if random.randint(0, 1) == 0:
            pygame.mixer.music.load('Sound/tetrisb.mid')
        else:
            pygame.mixer.music.load('Sound/tetrisc.mid')
        pygame.mixer.music.play(-1, 0.0)
        run_game()
        pygame.mixer.music.stop()
        show_text_screen('Game Over')

def run_game():
    #setup variables for the start of the game
    board = get_blank_board()
    last_move_down_time = time.time()
    last_move_sideways_time = time.time()
    last_fall_time = time.time()
    moving_down = False #note: there is no moving_up variable
    moving_left = False
    moving_right = False
    score = 0
    level, fall_freq = calculate_level_and_fall_freq(score)

    falling_piece = get_new_piece()
    next_piece = get_new_piece()

    while True: #main game loop
        if falling_piece == None:
            #no falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece = get_new_piece()
            last_fall_time = time.time() #reset last_fall_time

            if not is_valid_position(board, falling_piece):
                return #can't fit a new piece on the board, so game over
        
        check_for_quit()
        for event in pygame.event.get(): #event handling loop
            if event.type == KEYUP:
                if (event.key == K_p):
                    #pausing the game
                    display_surf.fill(bg_color)
                    pygame.mixer.music.stop()
                    show_text_screen('Paused') #pause until a key press
                    pygame.mixer.music.play(-1, 0.0)
                    last_fall_time = time.time()
                    last_move_down_time = time.time()
                    last_move_sideways_time = time.time()
                elif (event.key == K_LEFT or event.key == K_a):
                    moving_left = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    moving_right = False
                elif (event.key == K_DOWN or event.key == K_s):
                    moving_down = False
            
            elif event.type == KEYDOWN:
                #moving the block sideways
                if (event.key == K_LEFT or event.key == K_a) and is_valid_position(board, falling_piece, adjX = -1):
                    falling_piece['x'] -= 1
                    moving_left = True
                    moving_right = False
                    last_move_sideways_time = time.time()
                
                elif (event.key == K_RIGHT or event.key == K_d) and is_valid_position(board, falling_piece, adjX = 1):
                    falling_piece['x'] += 1
                    moving_right = True
                    moving_left = False
                    last_move_sideways_time = time.time()
                
                #rotating the block, if there is room to rotate
                elif (event.key == K_UP or event.key == K_w):
                    falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(shapes[falling_piece['shape']])
                    
                    if not is_valid_position(board, falling_piece):
                        falling_piece['rotation'] = (falling_piece['rotation'] - 1) % len(shapes[falling_piece['shape']])
                
                elif (event.key == K_q): #rotate the other direction
                    falling_piece['rotation'] = (falling_piece['rotation'] - 1) % len(shapes[falling_piece['shape']])
                    
                    if not is_valid_position(board, falling_piece):
                        falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(shapes[falling_piece['shape']])
                #making the block fall faster with down key
                elif (event.key == K_DOWN or event.key == K_s):
                    moving_down = True
                    if is_valid_position(board, falling_piece, adjY = 1):
                        falling_piece['y'] += 1
                    last_move_down_time = time.time()

                #move the current block all the way down
                elif event.key == K_SPACE:
                    moving_down = False
                    moving_left = False
                    moving_right = False
                    for i in range(1, board_height):
                        if not is_valid_position(board, falling_piece, adjY = i):
                            break
                    falling_piece['y'] += i - 1
        #handle moving the block because of user input
        if (moving_left or moving_right) and time.time() - last_move_sideways_time > move_side_ways_freq:
            if moving_left and is_valid_position(board, falling_piece, adjX =- 1):
                falling_piece['x'] -= 1
            elif moving_right and is_valid_position(board, falling_piece, adjX = 1):
                falling_piece['x'] += 1
            last_move_sideways_time = time.time()

        if moving_down and time.time() - last_move_down_time > move_down_freq and is_valid_position(board, falling_piece, adjY = 1):
            falling_piece['y'] += 1
            last_move_down_time = time.time()
        #let the piece fall if it is time to fall
        if time.time() - last_fall_time > fall_freq:
            #see if the piece has landed
            if not is_valid_position(board, falling_piece, adjY = 1):
                #falling piece has landed, set it on the board
                add_to_board(board, falling_piece)
                score += remove_complete_lines(board)
                level, fall_freq = calculate_level_and_fall_freq(score)
                falling_piece = None
            else:
                #piece did not land, just move the block down
                falling_piece['y'] += 1
                last_fall_time = time.time()
        #drawing everything on the screen
        display_surf.fill(bg_color)
        draw_board(board)
        draw_status(score, level)
        draw_next_piece(next_piece)
        if falling_piece != None:
            draw_piece(falling_piece)
        pygame.display.update()
        fps_clock.tick(fps)

def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

def terminate():
    pygame.quit()
    sys.exit()

def check_for_key_press():
    #go through event queue looking for keyup event
    #grab keydown events to remove them from the event queue
    check_for_quit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None

def show_text_screen(text):
    #this function displays large text in the
    #center of the screen until a key is pressed.
    #draw the text drop shadow
    title_surf, title_rect = make_text_objs(text, big_font, text_shadow_color)
    title_rect.center = (int(window_width / 2), int(window_height / 2))
    display_surf.blit(title_surf, title_rect)

    #draw the text
    title_surf, title_rect = make_text_objs(text, big_font, text_color)
    title_rect.center = (int(window_width / 2) - 3, int(window_height / 2) - 3)
    display_surf.blit(title_surf, title_rect)

    #draw the additional "Press a key to play" text
    press_key_surf, press_key_rect = make_text_objs('Press a key to play.', basic_font, text_color)
    press_key_rect.center = (int(window_width / 2), int(window_height / 2) + 100)
    display_surf.blit(press_key_surf, press_key_rect)

    while check_for_key_press() == None:
        pygame.display.update()
        fps_clock.tick()

def check_for_quit():
    for event in pygame.event.get(QUIT): #get all the quit events
        terminate() #terminate if any quit events are present
    for event in pygame.event.get(KEYUP): #get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() #terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) #put the other KEYUP event objects back

def calculate_level_and_fall_freq(score):
    #based on the score, return the level the player is on and
    #how many seconds pass untill a falling piece falls one space
    level = int(score / 10) + 1
    fall_freq = 0.27 - (level * 0.02)
    return level, fall_freq

def get_new_piece():
    #return a random new piece in a random rotation and color
    shape = random.choice(list(shapes.keys()))
    new_piece = {
        'shape': shape,
        'rotation': random.randint(0, len(shapes[shape]) - 1),
        'x': int(board_width / 2) - int(template_width / 2),
        'y': -2, #start it above the board
        'color': random.randint(0, len(colors) - 1)
    }
    return new_piece

def add_to_board(board, piece):
    #fill the board based on piece's location, shape, and rotation
    for x in range(template_width):
        for y in range(template_height):
            if shapes[piece['shape']][piece['rotation']][y][x] != blank:
                board[x + piece['x']][y + piece['y']] = piece['color']

def get_blank_board():
    #create and return a new blank board data structure
    board = []
    for i in range(board_width):
        board.append([blank] * board_height)
    return board

def is_on_board(x, y):
    return x >= 0 and x < board_width and y < board_height

def is_valid_position(board, piece, adjX = 0, adjY = 0):
    #return true if the piece is within the board and not colliding
    for x in range(template_width):
        for y in range(template_height):
            is_above_board = y + piece['y'] + adjY < 0
            if is_above_board or shapes[piece['shape']][piece['rotation']][y][x] == blank:
                continue
            if not is_on_board(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != blank:
                return False
    return True

def is_complete_line(board, y):
    #return True if the line filled with boxes with no gaps
    for x in range(board_width):
        if board[x][y] == blank:
            return False
    return True

def remove_complete_lines(board):
    #remove any completed lines on the board,
    #move everything above them down, and return the number
    #of complete lines
    num_lines_removed = 0
    y = board_height - 1 #start y at the bottom of the board
    while y >= 0:
        if is_complete_line(board, y):
            #remove the line and pull boxes down the line
            for pull_down_y in range(y, 0, -1):
                for x in range(board_width):
                    board[x][pull_down_y] = board[x][pull_down_y - 1]
            #set very top line to blank
            for x in range(board_width):
                board[x][0] = blank
            num_lines_removed += 1
            #note on the next iteration of the loop, y is the same
            #this is so that if the line that was pulled down is also
            #complete, it will be removed
        else:
            y -= 1 #move on to check next row up
    return num_lines_removed

def convert_to_pixel_coords(boxx, boxy):
    '''convert the given xy coordinates of the board to xy
    coordinates of the location on the screen'''
    return(x_margin + (boxx * box_size)), (top_margin +(boxy * box_size))

def draw_box(boxx, boxy, color, pixelx = None, pixely = None):
    '''draw a single box (each tetris piece has four boxes)
    at xy coordinates on the board. Or, if pixelx & pixely 
    are specified, draw to the pixel coordinates stored in 
    pixelx & pixely (this is used for the "Next" piece)'''
    if color == blank:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convert_to_pixel_coords(boxx, boxy)
    pygame.draw.rect(display_surf, colors[color], (pixelx + 1, pixely + 1, box_size - 1, box_size - 1))
    pygame.draw.rect(display_surf, light_colors[color], (pixelx + 1, pixely + 1, box_size - 4, box_size - 4))

def draw_board(board):
    #draw the border around the board
    pygame.draw.rect(display_surf, border_color, (x_margin - 3, top_margin - 7, (board_width * box_size) + 8, (board_height * box_size) + 8), 5)
    #fill the background of the board
    pygame.draw.rect(display_surf, bg_color, (x_margin, top_margin, box_size * board_width, box_size * board_height))
    #draw the individual boxes on the board
    for x in range(board_width):
        for y in range(board_height):
            draw_box(x, y, board[x][y])

def draw_status(score, level):
    #draw the score text
    score_surf = basic_font.render('Score: %s' % score, True, text_color)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (window_width - 150, 20)
    display_surf.blit(score_surf, score_rect)

    #draw the level text
    level_surf = basic_font.render('Level: %s' % level, True, text_color)
    level_rect = level_surf.get_rect()
    level_rect.topleft = (window_width - 150, 50)
    display_surf.blit(level_surf, level_rect)

def draw_piece(piece, pixelx = None, pixely = None):
    shape_to_draw = shapes[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        #if pixelx & pixely hasn't been specified, use the location
        #stored in the piece data structure
        pixelx, pixely = convert_to_pixel_coords(piece['x'], piece['y'])
    #draw each of the blocks that make up the piece
    for x in range(template_width):
        for y in range(template_height):
            if shape_to_draw[y][x] != blank:
                draw_box(None, None, piece['color'], pixelx + (x * box_size), pixely + (y * box_size))

def draw_next_piece(piece):
    #draw the "next" text
    next_surf = basic_font.render('Next: ', True, text_color)
    next_rect = next_surf.get_rect()
    next_rect.topleft = (window_width - 120, 80)
    display_surf.blit(next_surf, next_rect)
    #draw the 'next' piece
    draw_piece(piece, pixelx = window_width - 120, pixely = 100)

if __name__ == '__main__':
    main()