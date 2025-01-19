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
TILE_LINE = Tile((0, 1))
TILE_BOMB = Tile((1, 1))

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
        while True:
            erased, _ = self.erase(generate_powerups=False)
            if erased:
                self.drop()
                self.fill()
            else:
                break

    def get_tile(self, x: int, y: int) -> Tile:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tile_list[x][y]
        else:
            return TILE_BLANK
    
    def set_tile(self, x: int, y: int, new_tile: Tile) -> None:
        self.tile_list[x][y] = new_tile

    def draw(self) -> None:
        for x in range(self.width):
            for y in range(self.height):
                self.get_tile(x, y).draw(x, y)

    def pop(self, x: int, y: int) -> tuple[int, int, int]:
        """
        1枚のタイルを消去し、連鎖的にアイテムの処理を行う
        さらに、消えたタイルの枚数、消えたボムの個数、消えたラインの回数を返す
        """
        tile = self.get_tile(x, y)
        self.set_tile(x, y, TILE_BLANK)
        if tile in BASIC_TILES:
            return (1, 0, 0)
        elif tile == TILE_BLANK:
            return (0, 0, 0)
        elif tile == TILE_BOMB:
            snt = 0
            snb = 1
            snl = 0
            left = max(x - 1, 0)
            right = min(x + 2, self.width)
            top = max(y - 1, 0)
            bottom = min(y + 2, self.height)
            for px in range(left, right):
                for py in range(top, bottom):
                    if px == x and py == y:
                        continue
                    nt, nb, nl = self.pop(px, py)
                    snt += nt
                    snb += nb
                    snl += nl
            return (snt, snb, snl)
        elif tile == TILE_LINE:
            snt = 0
            snb = 0
            snl = 1
            # 横
            for px in range(self.width):
                if px == x:
                    continue
                nt, nb, nl = self.pop(px, y)
                snt += nt
                snb += nb
                snl += nl
            # 縦
            for py in range(self.height):
                if py == y:
                    continue
                nt, nb, nl = self.pop(x, py)
                snt += nt
                snb += nb
                snl += nl
            return (snt, snb, snl)

    def erase(self, generate_powerups: bool = True) -> tuple[bool, int]:
        """直線状に3つ繋がったタイルを消去し、消去したタイルが存在したかと消去したタイルの枚数を返す"""
        erased = False
        erase_count = 0
        # パワーアップを作るループ
        for x in range(0, self.width - 1):
            for y in range(0, self.width - 1):
                tile = self.get_tile(x, y)
                if not tile in BASIC_TILES:
                    continue
                left = self.get_tile(x - 1, y)
                right = self.get_tile(x + 1, y)
                up = self.get_tile(x, y - 1)
                down = self.get_tile(x, y + 1)
                rightdown = self.get_tile(x + 1, y + 1)
                if tile == up and tile == down and tile == left and tile == right:
                    self.set_tile(x, y, TILE_LINE if generate_powerups else TILE_BLANK)
                    self.set_tile(x, y - 1, TILE_BLANK)
                    self.set_tile(x, y + 1, TILE_BLANK)
                    self.set_tile(x - 1, y, TILE_BLANK)
                    self.set_tile(x + 1, y, TILE_BLANK)
                    erase_count += 5
                    erased = True
                    continue
                if tile == right and tile == down and tile == rightdown:
                    self.set_tile(x, y, TILE_BOMB if generate_powerups else TILE_BLANK)
                    self.set_tile(x, y + 1, TILE_BLANK)
                    self.set_tile(x + 1, y, TILE_BLANK)
                    self.set_tile(x + 1, y + 1, TILE_BLANK)
                    erase_count += 4
                    erased = True
                    continue

        # その他のタイルを消すループ
        for x in range(0, self.width):
            for y in range(0, self.height):
                tile = self.get_tile(x, y)
                if not tile in BASIC_TILES:
                    continue
                left = self.get_tile(x - 1, y)
                right = self.get_tile(x + 1, y)
                up = self.get_tile(x, y - 1)
                down = self.get_tile(x, y + 1)
                if tile == up and tile == down:
                    self.set_tile(x, y - 1, TILE_BLANK)
                    self.set_tile(x, y, TILE_BLANK)
                    self.set_tile(x, y + 1, TILE_BLANK)
                    erase_count += 3
                    erased = True
                    continue
                if tile == left and tile == right:
                    self.set_tile(x - 1, y, TILE_BLANK)
                    self.set_tile(x, y, TILE_BLANK)
                    self.set_tile(x + 1, y, TILE_BLANK)
                    erase_count += 3
                    erased = True
                    continue
        return erased, erase_count

    def drop(self) -> None:
        """空白以外のタイルを下に落とす"""
        rem = []
        for x in range(self.width):
            drop_y = self.height - 1 # 次に落とす位置
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
        """
        空白のタイルをランダムに埋める
        dropしてから実行してください
        """
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

        if 0 <= self.x + dx < width:
            self.x += dx
        if 0 <= self.y + dy < height:
            self.y += dy

class App:
    def __init__(self):
        self.width = 8
        self.height = 8
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
                tiles, bombs, lines = self.field.pop(self.cursor.x, self.cursor.y)
                self.score += tiles * 100 + (bombs + lines) * 200
                self.dropping = True
                self.drop_start_frame = pyxel.frame_count

App()