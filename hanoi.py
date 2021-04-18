import ssd1306
import time
from machine import I2C, Pin


i2c = I2C(scl=Pin(5), sda=Pin(4))
display = ssd1306.SSD1306_I2C(64, 48, i2c)
display.poweron()

state = [[], [], []]
max_piece = 0  # size of largest piece (i.e. number of rows)


def length(piece):
	return 2*piece + 2


def sleep():
	#time.sleep_ms(50)
	pass


def position_col(col):
	col_width = length(max_piece) + 3
	return 2 + col * col_width + length(max_piece)//2


def position_x(piece, col):
	return position_col(col) - length(piece)//2


def position_y(index):
	return 10 + 2*(max_piece - index)


# piece: piece size (0 = smallest)
# col: column (0 = first)
# index: in-column index (0 = lowest)
def position(piece, col, index):
	return position_x(piece, col), position_y(index)


def draw_piece(piece, x, y, color):
	display.hline(x, y, length(piece), color)


def draw_all():
	display.fill(0);
	for i, col in enumerate(state):
		col_x = position_col(i)
		col_y = position_y(0)
		display.rect(col_x-1, col_y + 2, 2, 5, 1)

		for j, piece in enumerate(col):
			x, y = position(piece, i, j)
			draw_piece(piece, x, y, 1)

	display.show()


def move_piece(piece, a, b):
	state[a].pop()
	sindex = len(state[a])
	tindex = len(state[b])
	state[b].append(piece)

	sx, sy = position(piece, a, sindex)
	tx, ty = position(piece, b, tindex)

	tops = [sy, ty]
	if a != 1 and b != 1:
		index = len(state[1])
		tops.append(position_y(index))
	top_y = min(*tops) - 2

	cur_x, cur_y = sx, sy
	def move(x, y):
		nonlocal cur_x, cur_y
		draw_piece(piece, cur_x, cur_y, 0)
		cur_x, cur_y = x, y
		draw_piece(piece, cur_x, cur_y, 1)
		display.show()
		sleep()

	for y in range(sy, top_y-1, -1):
		move(sx, y)
	for x in range(cur_x, tx+1, 2*(1 if tx > sx else -1)):
		move(x, cur_y)
	for y in range(cur_y, ty+1):
		move(tx, y)


def move_stack(bottom_piece, a, b):
	if bottom_piece == 0:
		move_piece(bottom_piece, a, b)
	else:
		tmp = 3 - (a+b)
		move_stack(bottom_piece-1, a, tmp)
		move_piece(bottom_piece, a, b)
		move_stack(bottom_piece-1, tmp, b)

def play(count):
	global max_piece
	max_piece = count-1
	for i in range(count):
		state[0].insert(0, i)
	#	state[2].insert(0, i)
	# state[1].append(3)
	# state[2].append(4)

	draw_all()
	time.sleep_ms(1000)
	move_stack(max_piece, 0, 2)

play(9)
