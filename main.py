import pyb

SWIDTH = 127
SHEIGHT = 31
TILE_WIDTH = 4

CTRL_SENS = 3

BEGIN_COORDS = [15, 15]
BEGIN_DIR = [1, 0]

lcd_screen = pyb.LCD("X")
# lcd_screen.light(True)
lcd_screen.fill(0)
lcd_screen.show()


class Tile(object):
    def draw(self, x, y, color=1):
        for i in range(TILE_WIDTH):
            for j in range(TILE_WIDTH):
                lcd_screen.pixel(x + i, y + j, color)
    
    def render(self):
        return [self.draw(*args) for args in self.points]


class Snake(Tile):
    def __init__(self, controller):
        self.head = BEGIN_COORDS
        self.direction = BEGIN_DIR
        self.points = [self.head]
        self.ctrl = controller

    def _read_dir(self):
        if self.ctrl.x() > CTRL_SENS:
            self.direction = [-1, 0]
        elif self.ctrl.x() < -CTRL_SENS:
            self.direction = [1, 0]
        elif self.ctrl.y() > -CTRL_SENS:
            self.direction = [0, 1]
        elif self.ctrl.y() < CTRL_SENS:
            self.direction = [0, -1]
        x, y = self.direction
        x *= TILE_WIDTH
        y *= TILE_WIDTH
        return x, y

    def move(self):
        dx, dy = self._read_dir()
        hx = self.head[0] + dx
        hy = self.head[1] + dy
        self.head = [hx, hy]
        self.points.insert(0, self.head)
        self.points.pop()

    def eat(self):
        if len(self.points) == 1:
            newlast = self.head[:]
            newlast[0] -= (self.direction[0] * TILE_WIDTH)
            newlast[1] -= (self.direction[1] * TILE_WIDTH)
        else: 
            plast, last = self.points[-2:]
            newlast = last[:]
            if plast[0] == last[0]:
                if plast[1] > last[1]:
                    newlast[1] -= TILE_WIDTH
                else:
                    newlast[1] += TILE_WIDTH
            else:
                if plast[0] > last[0]:
                    newlast[0] -= TILE_WIDTH
                else:
                    newlast[0] += TILE_WIDTH
        self.points.append(newlast)
        self.render()

    def _bite(self):
        return self.head in self.points[1:]

    def _fall_out(self):
        x, y = self.head
        out_width = x > SWIDTH + TILE_WIDTH or x < -TILE_WIDTH
        out_height = y > SHEIGHT + TILE_WIDTH or y < -TILE_WIDTH
        return  out_width or out_height

    def isdead(self):
        return self._fall_out() or self._bite()


class Apple(Tile):
    def __init__(self):
        self.fall()

    def fall(self):
        x = pyb.rng() % SWIDTH // TILE_WIDTH * TILE_WIDTH - 1
        y = pyb.rng() % SHEIGHT // TILE_WIDTH * TILE_WIDTH - 1
        self.points = [[x, y]]
        self.render()


def main():
    snake = Snake(pyb.Accel())
    apple = Apple()

    while not snake.isdead():
        lcd_screen.fill(0)
        apple.render()
        snake.render()
        lcd_screen.show()
        pyb.delay(200)

        if snake.head == apple.points[0]:
            snake.eat()
            apple.fall()
            snake.render()
            lcd_screen.show()
        snake.move()

    lcd_screen.write("death...\n")
    pyb.delay(100)


main()
