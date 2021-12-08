blinkerp=0
slowmode=0
import math
import random
import time

from tkinter import *
root = Tk()

import pygame
from pygame import mixer

# Intialize the pygame
pygame.init()
#bg_music = pygame.mixer.Sound('music.wav')
#bg_music.play(loops=-1)

pygame.mixer.music.load('bgm.mp3')
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.5)

blinker=0
blinkerp=0 #2021-12-01

oldscore=0
numberofcoinsoundstoplay=0
score=0

coinSound = mixer.Sound("coins.wav")#sound
coinSound.play()

#import pygame
#import random


pygame.font.init()


# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape


class Piece(object):  # *
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_pos={}):  # *
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))


def clear_rows(grid, locked):

    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))




def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as filerw: #20211129
        if int(score) > nscore:
            filerw.write(str(score))
        else:
            filerw.write(str(nscore))


def max_score():
    with open('scores.txt', 'r') as filerw: #20211129
        lines = filerw.readlines()
        score = lines[0].strip()

    return score


def draw_window(surface, grid, score=0, last_score = 0):
    global blinker
    global slowmode
    global oldscore
    global numberofcoinsoundstoplay
    surface.fill((0, 0, 0))

    pygame.font.init()
    #self.laser_sound = pygame.mixer.Sound('coin.wav')  # sound

    font = pygame.font.SysFont('comicsans', 60)
    blinker +=1
    #label = font.render('Tetris'+str(blinker)+' slowmode:'+str(slowmode)+' os:'+str(oldscore)+' s:'+str(score)+' ncstp:'+str(numberofcoinsoundstoplay), 1, (255, 255, 255))

    #2021-12-01
    #label = font.render('Tetris pause:p paused='+str(blinkerp), 1, (255, 255, 255))
    label = font.render('Tetris pause:p slowmode:'+str(slowmode), 1, (255, 255, 255))

    if (blinker % 60==0) and (numberofcoinsoundstoplay>0):
        coinSound.play()  # sound
        numberofcoinsoundstoplay = numberofcoinsoundstoplay - 1

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 20))
    #surface.blit(label, (0, 0))

    # current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render('HighScore:' + last_score, 1, (255,255,255))

    sx = top_left_x - 200
    sy = top_left_y + 200

    #surface.blit(label, (sx + 20, sy + 160))
    #surface.blit(label, (sx + 20, 0))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx - 40, sy + 190))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)
    #pygame.display.update()


def main(win):  # *
    global blinker
    global slowmode
    global blinkerp
    global oldscore
    global numberofcoinsoundstoplay
    global score
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    numberofcoinsoundstoplay=0
    oldscore=0
    score = 0


    while run:
        if (blinkerp==1) : #or ((slowmode==1) and (blinker % 10)==0) :
        #if (blinkerp == 1):# or ((slowmode == 1) and (blinker % 10)) == 0:

            score=score
            blinker+=1
            clock.tick()
            pygame.display.update()
            pygame.time.delay(1500)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()

                # 2021-12-01
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        if slowmode == 0:
                            slowmode = 1
                        else:
                            slowmode = 0

                    if event.key == pygame.K_p:
                        if blinkerp == 0:
                            blinkerp = 1


                        else:
                            blinkerp = 0
                            pygame.mixer.music.play(loops=-1)

                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not (valid_space(current_piece, grid)):
                            current_piece.x += 1
                    if event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not (valid_space(current_piece, grid)):
                            current_piece.x -= 1
                    if event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not (valid_space(current_piece, grid)):
                            current_piece.y -= 1

        else:
            grid = create_grid(locked_positions)
            fall_time += clock.get_rawtime()
            level_time += clock.get_rawtime()
            clock.tick()

            if level_time / 1000 > 5:
                level_time = 0
                if level_time > 0.12:
                    level_time -= 0.005

            if fall_time / 1000 > fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                    current_piece.y -= 1
                    change_piece = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()

                # 2021-12-01
                if event.type == pygame.KEYDOWN:
                    # if event.key == pygame.K_LEFT:
                    ##if keys[pygame.K_p]:
                    # if blinkerp == 0:
                    #    blinkerp = 1
                    # else:
                    #    blinkerp = 0

                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not (valid_space(current_piece, grid)):
                            current_piece.x += 1
                    if event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not (valid_space(current_piece, grid)):
                            current_piece.x -= 1
                    if event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not (valid_space(current_piece, grid)):
                            current_piece.y -= 1

                    if event.key == pygame.K_s:
                        if slowmode==0:
                            slowmode=1
                        else:
                            slowmode=0
                    if event.key == pygame.K_p:
                        if blinkerp == 0:
                            pygame.mixer.music.stop()
                              #stop
                            blinkerp = 1

                        else:
                            blinkerp = 0
                    if event.key == pygame.K_UP:
                        current_piece.rotation += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.rotation -= 1

            shape_pos = convert_shape_format(current_piece)

            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                if y > -1:
                    grid[y][x] = current_piece.color

            oldscore = score

            if change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    locked_positions[p] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                change_piece = False
                score += clear_rows(grid, locked_positions) * 10
                # sound
                if oldscore != score:
                    numberofcoinsoundstoplay = (score - oldscore) / 10
                    coinSound.play()  # sound
                    numberofcoinsoundstoplay = numberofcoinsoundstoplay - 1

            draw_window(win, grid, score, last_score)
            draw_next_shape(next_piece, win)
            pygame.display.update()

            if (slowmode == 1):
                for i in range(1, 250):
                    draw_window(win, grid, score, last_score)



            if check_lost(locked_positions):
                draw_text_middle(win, "YOU LOST!", 80, (255, 255, 255))
                pygame.display.update()


                pygame.time.delay(1500)
                run = False
                update_score(score)
                # self.laser_sound.play()#sound
                # coinSound.play()#sound


def main_menu(win):  # *
    run = True
    #try:
    while run:
            win.fill((0,0,0))
            draw_text_middle(win, 'Press Any Key To Play', 60, (255,255,255))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    main(win)

    pygame.display.quit()

    #except Exception:
    #    pass


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
main_menu(win)

#root.mainloop()