
TOKEN = "5365673398:AAH7tmtdq2dVHfviZFeIOOMHyOWZMhPcW2w"

from dataclasses import dataclass, field
from time import sleep
import os


class WrongMoveException(Exception):
    pass


class OutOfBoardException(WrongMoveException):
    pass


class BusyCellException(WrongMoveException):
    pass


@dataclass(frozen=True)
class Dot:
    x: int
    y: int

    def __repr__(self):
        return f'Dot({self.x + 1}, {self.y + 1})'


@dataclass
class Ship:
    nose: Dot
    horizontal: bool
    length: int
    hp: int = field(init=False)

    def __post_init__(self):
        self.hp = self.length

    @property
    def dots(self):
        dot_list = [self.nose]
        x, y = self.nose.x, self.nose.y
        for i in range(self.length - 1):
            y += self.horizontal
            x += not self.horizontal
            dot_list.append(Dot(x, y))
        return dot_list


class Board:
    def __init__(self, size):
        self.size = size
        self.field = [['.'] * size for _ in range(size)]
        self.ships = []
        self.busy = set()

    def is_out(self, dot: Dot):
        # if not isinstance(dot, Dot):
        #     raise TypeError(f"expected 'Dot', got '{dot.__class__.__name__}' instead")

        return not (0 <= dot.x < self.size) or not (0 <= dot.y < self.size)

    def contour(self, ship: Ship):
        # if not isinstance(ship, Ship):
        #     raise TypeError(f"expected 'Ship', got '{ship.__class__.__name__}' instead")

        dots_around = (
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        )
        contour_dot_list = []
        for dot in ship.dots:
            for x, y in dots_around:
                contour_dot = Dot(dot.x + x, dot.y + y)
                if self.is_out(contour_dot) or contour_dot in ship.dots:
                    continue
                contour_dot_list.append(contour_dot)
        return contour_dot_list

    def add_ship(self, ship: Ship):
        for dot in ship.dots:
            if self.is_out(dot):
                raise OutOfBoardException("Корабль за пределами доски")
            if dot in self.busy:
                raise BusyCellException("Корабль пересекается с другими")

        for dot in ship.dots:
            # self.field[dot.x][dot.y] = '#'
            self.busy.add(dot)

        self.ships.append(ship)
        contour_dots = self.contour(ship)
        self.busy.update(contour_dots)

    def shot(self, target_dot: Dot):
        if self.is_out(target_dot):
            raise OutOfBoardException("Выстрел за пределы доски")
        if target_dot in self.busy:
            raise BusyCellException("Вы уже стреляли по указанным координатам")

        for ship in self.ships:
            for dot in ship.dots:
                if target_dot == dot:
                    ship.hp -= 1
                    if ship.hp:
                        self.field[target_dot.x][target_dot.y] = '\033[33mx\033[39m'
                        self.shot_animation(hit='hit')
                        print("Ранил!")
                    else:
                        for contour_dot in self.contour(ship):
                            self.field[contour_dot.x][contour_dot.y] = '\033[38;5;69m~\033[39m'
                        for s_dot in ship.dots:
                            self.field[s_dot.x][s_dot.y] = '\033[31mX\033[39m'
                        self.shot_animation(hit='sunk')
                        print("Убил!")
                    return True
        self.shot_animation()
        self.field[target_dot.x][target_dot.y] = '\033[38;5;69m~\033[39m'
        print("Промахнулся")
        return False

    @staticmethod
    def shot_animation(*, hit=None):
        size = 5  # расстояние, которое визуально пролетает ядро

        print('🖐', end='\r', flush=True)
        sleep(0.5)
        print('✊', end='\r', flush=True)
        sleep(0.5)
        for i in range(size):
            # собирается строка из точек
            # на каждой итерации "бомба" смещается вправо
            string = '👉 ' + '•' * i + '💣'
            string += '•' * (size - i) + '❓'
            print(string, end='\r', flush=True)  # специальная печать
            sleep(0.25)  # задержка

        # результат выстрела
        string = '👉 ' + '•' * (size + 2)
        if hit == 'hit':
            string += '💥'
        elif hit == 'sunk':
            string += '💀'
        else:
            string += '🌀'
        print(string)
        sleep(0.75)

    def __str__(self):
        string = '\n  ' + ' '.join(map(str, range(1, self.size + 1)))
        for i in range(self.size):
            string += f'\n{i + 1} {" ".join(self.field[i])}'
        string += '\n'
        return string


b = Board(6)
ship = Ship(Dot(2, 2), True, 3)
b.add_ship(ship)
print(b)
b.busy = set()
os.system('cls')
for i in range(5):
    print(b)
    x, y = map(int, input("Выстрел в ").split())
    dot = Dot(x - 1, y - 1)
    b.shot(dot)
    sleep(0.75)
    os.system('cls')
print(b)
input()