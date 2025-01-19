import pyxel
import random

class Tile:
    def __init__(self, img: tuple[int, int] | None = None, blank: bool = False):
        self.img = img
        self.blank = blank

    def draw(self, x: int, y: int) -> None:
        if self.img == None:
            return
        pyxel.blt(x * 8, y * 8, 0, self.img[0] * 8, self.img[1] * 8, 8, 8, 0)

    def is_blank(self) -> bool:
        return self.blank

TILE_BLANK = Tile(None, True)
TILE_RED = Tile((0, 0))
TILE_ORANGE = Tile((1, 0))
TILE_GREEN = Tile((2, 0))
TILE_BLUE = Tile((3, 0))
TILE_PURPLE = Tile((4, 0))

BASIC_TILES = (
    TILE_RED, TILE_ORANGE, TILE_GREEN, TILE_BLUE, TILE_PURPLE,
)

class Field:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tile_list: list[list[Tile]] = []
        for x in range(self.width):
            self.tile_list.append([])
            for y in range(self.height):
                self.tile_list[x].append(random.choice(BASIC_TILES))

    def get_tile(self, x: int, y: int) -> Tile:
        return self.tile_list[x][y]
    
    def set_tile(self, x: int, y: int, new_tile: Tile) -> None:
        self.tile_list[x][y] = new_tile

    def draw(self) -> None:
        for x in range(self.width):
            for y in range(self.height):
                self.get_tile(x, y).draw(x, y)

    def pop(self, x: int, y: int) -> None:
        self.set_tile(x, y, TILE_BLANK)

    def erase(self) -> tuple[bool, int]:
        erase_count = 0
        for x in range(1, self.width - 1):
            for y in range(0, self.height):
                tile = self.get_tile(x, y)
                if tile.is_blank():
                    continue
                left = self.get_tile(x - 1, y)
                right = self.get_tile(x + 1, y)
                if tile == left and tile == right:
                    self.set_tile(x - 1, y, TILE_BLANK)
                    self.set_tile(x, y, TILE_BLANK)
                    self.set_tile(x + 1, y, TILE_BLANK)
                    erase_count += 1
        for x in range(0, self.width):
            for y in range(1, self.height - 1):
                tile = self.get_tile(x, y)
                if tile.is_blank():
                    continue
                up = self.get_tile(x, y - 1)
                down = self.get_tile(x, y + 1)
                if tile == up and tile == down:
                    self.set_tile(x, y - 1, TILE_BLANK)
                    self.set_tile(x, y, TILE_BLANK)
                    self.set_tile(x, y + 1, TILE_BLANK)
                    erase_count += 1
        return erase_count > 0, erase_count

    def drop(self) -> None:
        rem = []
        for x in range(self.width):
            drop_y = self.height - 1
            for bottom in range(self.height):
                y = self.height - bottom - 1
                tile = self.get_tile(x, y)
                if not tile.is_blank():
                    self.set_tile(x, y, TILE_BLANK)
                    self.set_tile(x, drop_y, tile)
                    drop_y -= 1
            rem.append(drop_y)
        self.dropped_spaces = rem

    def fill(self) -> None:
        """dropを呼び出してから実行してください"""
        for x, rem in enumerate(self.dropped_spaces):
            for y in range(rem + 1):
                self.set_tile(x, y, random.choice(BASIC_TILES))

class Cursor:
    def __init__(self, x: int, y: int, horizontal: bool = True):
        self.x = x
        self.y = y
        self.horizontal = horizontal
        self.img = (0, 2)

    def draw(self) -> None:
        pyxel.blt(self.x * 8, self.y * 8, 0, self.img[0] * 8, self.img[1] * 8, 8, 8, 0)

    def update(self, width: int, height: int) -> None:
        dx = 0
        dy = 0
        if pyxel.btnp(pyxel.KEY_LEFT):
            dx -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT):
            dx += 1
        if pyxel.btnp(pyxel.KEY_UP):
            dy -= 1
        if pyxel.btnp(pyxel.KEY_DOWN):
            dy += 1

        if 0 <= self.x + dy < width:
            self.x += dx
        if 0 <= self.y + dy < height:
            self.y += dy

class App:
    def __init__(self):
        self.width = 6
        self.height = 6
        pyxel.init(self.width * 8, self.height * 8 + 10, "Pixel Puzzle")
        pyxel.load("./my_resource.pyxres")
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self) -> None:
        self.field = Field(self.width, self.height)
        while True:
            erased, _ = self.field.erase()
            if erased:
                self.field.drop()
                self.field.fill()
            else:
                break

        self.cursor = Cursor(0, 0)
        self.dropping = False
        self.drop_start_frame = pyxel.frame_count
        self.score = 0

    def draw(self) -> None:
        pyxel.cls(0)
        self.field.draw()
        if not self.dropping:
            self.cursor.draw()
        pyxel.text(2, self.height * 8 + 2, f"SCORE: {self.score}", 6)

    def update(self) -> None:
        if self.dropping:
            # pop -> drop & fill -> erase -> (repeat)
            dropping_frames = pyxel.frame_count - self.drop_start_frame
            if dropping_frames % 20 == 10:
                self.field.drop()
                self.field.fill()
            elif dropping_frames % 20 == 0:
                erased, erase_count = self.field.erase()
                if erased:
                    self.score += erase_count * (100 + dropping_frames)
                else:
                    self.dropping = False
        else:
            self.cursor.update(self.width, self.height)
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.field.pop(self.cursor.x, self.cursor.y)
                self.dropping = True
                self.drop_start_frame = pyxel.frame_count

App()