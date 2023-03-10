import pygame
import threading
from os import _exit
from dataclasses import dataclass
from ast import literal_eval
from config import *
import network_logic
from random import randint

pygame.init()
Icon = pygame.image.load("assets\\icon.ico")
font = pygame.font.SysFont("arial", nicknames_font_size)
chat_font = pygame.font.SysFont("arial", chat_font_size)
score_font = pygame.font.SysFont("arial", score_font_size)


@dataclass
class Snake:
    name: str
    color: tuple
    you: bool = False
    tails: list = None
    speed_x = 0
    speed_y = 0
    size = (10, 10)
    speed = 10
    offline = False

    def __post_init__(self):
        if not self.tails:
            self.reset_tails()
        self.name_rendered = font.render(
            self.name+(" (You)" if self.you else ""), True, (255, 255, 0))

    def reset_tails(self):
        self.tails = [[randint(5, 100)*10, randint(5, 70)*10]]

    def update(self, data):
        self.tails = [list(map(int, i.split(","))) for i in data[0].split(";")]
        speed = data[1].split(",")
        self.speed_x = int(speed[0])
        self.speed_y = int(speed[1])

        scores[self.name] = score_font.render(
            self.name+": "+str(len(self.tails)), 1, (255, 255, 255)
        )

    def move(self):
        for t in range(len(self.tails[::-1])):
            if t == len(self.tails)-1:
                if not all(self.tails[t]):
                    continue
                self.tails[t][0] += self.speed_x
                self.tails[t][1] += self.speed_y
                if self.tails[t][0] > (width-margin):
                    self.tails[t][0] = margin
                if self.tails[t][0] < margin:
                    self.tails[t][0] = width-margin
                if self.tails[t][1] > (height-margin):
                    self.tails[t][1] = margin
                if self.tails[t][1] < margin:
                    self.tails[t][1] = height-margin
            else:
                self.tails[t] = self.tails[t+1].copy()

    def draw(self, screen):
        if not self.tails:
            return
        else:
            for t in self.tails:
                if not all(t):
                    continue
                pygame.draw.rect(screen, self.color, [
                                 t[0], t[1], self.size[0], self.size[1]])

        if not self.offline:
            screen.blit(self.name_rendered,
                        (self.tails[-1][0]+10, self.tails[-1][1]-20))

    def get_str_pos(self):
        tails = "[UPDATE]|"+self.name+"|"
        for t in self.tails:
            tails += f"{t[0]},{t[1]}" + ";"
        tails = tails[:-1]
        speed = f"{self.speed_x},{self.speed_y}"
        return tails+"|"+speed

    def __str__(self) -> str:
        tails = ""
        for t in self.tails:
            tails += f"{t[0]},{t[1]}" + ";"
        tails = tails[:-1]
        speed = f"{self.speed_x},{self.speed_y}"
        s = f"[NEW]|{self.name}|{self.color}|{tails}|{speed}"
        return s


ip, port = input("Enter IP: "), int(input("Enter port: "))
nickname = input("Enter your nickname: ")
mySnake = Snake(nickname, tuple(randint(0, 255)
                for _ in range(3)), True)
threading.excepthook = network_logic.handle_disconnect
network_logic.connect((ip, port))
network_logic.handshake(nickname, mySnake)


display = pygame.display.set_mode((width, height), pygame.RESIZABLE)

pygame.display.set_caption(window_caption+f" ({nickname})")

pygame.display.set_icon(Icon)

clock = pygame.time.Clock()

snakes = {nickname: mySnake}  # nickname:snake_object
apples = []  # [x,y] for each apple
chat = []
scores = {mySnake.name: score_font.render(
    mySnake.name+": "+str(len(mySnake.tails)), 1, (255, 255, 255)
)}
score_text = score_font.render("SCORES:", 1, (255, 255, 255))
chat_text = chat_font.render("CHAT:", 1, (255, 255, 255))


def draw_chat(screen):
    screen.blit(chat_text, (width-200, 10))
    for i, j in enumerate(chat[::-1]):
        screen.blit(j, (width-margin*10, margin*(10-i)))


def draw_scores(screen):
    screen.blit(score_text, (10, 10))
    margin = 0
    for s in scores.values():
        screen.blit(s, (50, 50+margin))
        margin += 60


def draw_all(screen):
    screen.fill(bg_col)
    for apple in apples:
        pygame.draw.rect(screen, (randint(150, 255), randint(0, 70), randint(0, 70)), [
                         apple[0], apple[1], apple_size[0], apple_size[1]])
    for snake in snakes.values():
        snake.draw(screen)
    # Border
    pygame.draw.rect(screen, (0, 100, 255),
                     (margin, margin, width-1.5*margin, height-1.5*margin), 3, 5)

    # Chat
    draw_chat(screen)

    # Scores
    draw_scores(screen)


def live_update():
    global score
    while 1:
        data = network_logic.receive()
        data = data.split("|")

        if data[0] == "[ASK_POS]":
            network_logic.send(str(mySnake))
        elif data[0] == "[CHAT]":
            chat.append(font.render(data[1], True, (255, 255, 255)))
        elif data[0] == "[UPDATE]":
            snakes[data[1]].update(data[2:])
        elif data[0] == "[NEW]":
            new_snake = Snake(data[1], literal_eval(data[2]), False)
            new_snake.update(data[3:])
            snakes[new_snake.name] = new_snake
            scores[data[1]] = score_font.render(
                f"{data[1]}: {len(new_snake.tails)}", 1, (255, 255, 255))
        elif data[0] == "[APPLE+]":
            apples.append(list(map(int, data[1].split(","))))
        elif data[0] == "[APPLE-]":
            apples.remove(list(map(int, data[1].split(","))))
        elif data[0] == "[LEFT]":
            left_snake = snakes[data[1]]
            left_snake.speed_x = 0
            left_snake.speed_y = 0
            left_snake.color = (185, 183, 183)
            left_snake.tails[-1] = [None, None]
            left_snake.offline = True
            scores[left_snake.name] = score_font.render(
                left_snake.name+": " +
                str(len(left_snake.tails))+"(LEFT)", 1, (255, 255, 255)
            )


def read_input_and_send_to_chat():
    while 1:
        if msg := input("Write to chat: "):
            network_logic.send("[CHAT]|"+f"{nickname}: {msg}")


user_input_chat_thread = threading.Thread(
    target=read_input_and_send_to_chat).start()
live_update_thread = threading.Thread(target=live_update).start()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            _exit(0)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP) and mySnake.speed_y == 0:
                mySnake.speed_x = 0
                mySnake.speed_y = -mySnake.speed
                network_logic.send(mySnake.get_str_pos())
            if event.key in (pygame.K_a, pygame.K_LEFT) and mySnake.speed_x == 0:
                mySnake.speed_y = 0
                mySnake.speed_x = -mySnake.speed
                network_logic.send(mySnake.get_str_pos())
            if event.key in (pygame.K_d, pygame.K_RIGHT) and mySnake.speed_x == 0:
                mySnake.speed_y = 0
                mySnake.speed_x = mySnake.speed
                network_logic.send(mySnake.get_str_pos())
            if event.key in (pygame.K_s, pygame.K_DOWN) and mySnake.speed_y == 0:
                mySnake.speed_x = 0
                mySnake.speed_y = mySnake.speed
                network_logic.send(mySnake.get_str_pos())
    for s in snakes.values():
        s.move()

        # checking collisions
        # other snakes
        for t in s.tails:
            if ((mySnake.tails[-1][0] == t[0]) and (mySnake.tails[-1][1] == t[1])
                    and t is not mySnake.tails[-1]):
                mySnake.speed_x, mySnake.speed_y = 0, 0
                mySnake.reset_tails()
                scores[mySnake.name] = score_font.render(
                    mySnake.name+": "+str(len(mySnake.tails)), 1, (255, 255, 255))
                network_logic.send(mySnake.get_str_pos())
                break
    # apples
    for a in apples:
        if (mySnake.tails[-1][0] == a[0]) and (mySnake.tails[-1][1] == a[1]):
            mySnake.tails.append(a)
            apples.remove(a)
            scores[mySnake.name] = score_font.render(
                mySnake.name+": "+str(len(mySnake.tails)), 1, (255, 255, 255))
            network_logic.send(mySnake.get_str_pos())
            network_logic.send(f"[APPLE-]|{','.join(map(str,a))}")
            break
    draw_all(display)
    pygame.display.update()
    clock.tick(fps)
