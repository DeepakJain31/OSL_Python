from random import randrange as randrange
import pygame, sys, os
from pygame.locals import *
pygame.init()
pygame.mixer.music.load("music.ogg")
pygame.mixer.music.play(-1)

block_size = 18
cols = 20
rows = 20
frames_per_sec = 30

colors = [
(0,   0,   0  ),
(245, 75,  75),
(110, 210, 125),
(130, 118, 255),
(245, 130, 40 ),
(60,  130, 62 ),
(156, 212, 83 ),
(140, 151, 208 ),
(45,  45,  45) 
]

tetris_shapes = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]
]

def rotate_blocks_clockwise(block_shape):
	return [ [ block_shape[y][x]
			for y in range(len(block_shape)) ]
		for x in range(len(block_shape[0]) - 1, -1, -1) ]

def check_blocks_collision(tetris_board, block_shape, curr_offset):
	offset_x, offset_y = curr_offset
	for curr_y, curr_row in enumerate(block_shape):
		for curr_x, curr_cell in enumerate(curr_row):
			try:
				if curr_cell and tetris_board[ curr_y + offset_y ][ curr_x + offset_x ]:
					return True
			except IndexError:
				return True
	return False

def remove_entire_row(tetris_board, curr_row):
	del tetris_board[curr_row]
	return [[0 for i in range(cols)]] + tetris_board
	
def join_block_matrices(matrix1, matrix2, matrix2_offset):
	offset_x, offset_y = matrix2_offset
	for curr_y, curr_row in enumerate(matrix2):
		for curr_x, val in enumerate(curr_row):
			matrix1[curr_y+offset_y-1	][curr_x+offset_x] += val
	return matrix1

def new_board():
	tetris_board = [ [ 0 for x in range(cols) ]
			for y in range(rows) ]
	tetris_board += [[ 1 for x in range(cols)]]
	return tetris_board

class TetrisGame(object):
	def __init__(self):
		pygame.init()
		pygame.key.set_repeat(250,25)
		self.width = block_size*(cols+6)
		self.height = block_size*rows
		self.rlim = block_size*cols
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in range(cols)] for y in range(rows)]
		
		self.default_font =  pygame.font.Font(
			pygame.font.get_default_font(), 14)
		
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.event.set_blocked(pygame.MOUSEMOTION)
		self.next_stone = tetris_shapes[randrange(len(tetris_shapes))]
		self.init_game()
	
	def new_stone(self):
		self.stone = self.next_stone[:]
		self.next_stone = tetris_shapes[randrange(len(tetris_shapes))]
		self.stone_x = int(cols / 2 - len(self.stone[0])/2)
		self.stone_y = 0
		
		if check_blocks_collision(self.tetris_board,
		                   self.stone,
		                   (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.tetris_board = new_board()
		self.new_stone()
		self.level = 1
		self.score = 0
		self.lines = 0
		pygame.time.set_timer(pygame.USEREVENT+1, 1000)
	
	def display_msg(self, msg, topleft):
		x,y = topleft
		for line in msg.splitlines():
			self.screen.blit(
				self.default_font.render(
					line,
					False,
					(255,255,255),
					(0,0,0)),
				(x,y))
			y+=14
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  self.default_font.render(line, False,
				(255,255,255), (0,0,0))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (
			  self.width // 2-msgim_center_x,
			  self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix, curr_offset):
		offset_x, offset_y  = curr_offset
		for y, curr_row in enumerate(matrix):
			for x, val in enumerate(curr_row):
				if val:
					pygame.draw.rect(
						self.screen,
						colors[val],
						pygame.Rect(
							(offset_x+x) *
							  block_size,
							(offset_y+y) *
							  block_size, 
							block_size,
							block_size),0)
	
	def add_cl_lines(self, n):
		linescores = [0, 40, 100, 300, 1200]
		self.lines += n
		self.score += linescores[n] * self.level
		if self.lines >= self.level*6:
			self.level += 1
			newdelay = 1000-50*(self.level-1)
			newdelay = 100 if newdelay < 100 else newdelay
			pygame.time.set_timer(pygame.USEREVENT+1, newdelay)
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > cols - len(self.stone[0]):
				new_x = cols - len(self.stone[0])
			if not check_blocks_collision(self.tetris_board,
			                       self.stone,
			                       (new_x, self.stone_y)):
				self.stone_x = new_x
	def quit(self):
		self.center_msg("Exiting...")
		pygame.display.update()
		sys.exit()
	
	def drop(self, manual):
		if not self.gameover and not self.paused:
			self.score += 1 if manual else 0
			self.stone_y += 1
			if check_blocks_collision(self.tetris_board,
			                   self.stone,
			                   (self.stone_x, self.stone_y)):
				self.tetris_board = join_block_matrices(
				  self.tetris_board,
				  self.stone,
				  (self.stone_x, self.stone_y))
				self.new_stone()
				cleared_rows = 0
				while True:
					for i, curr_row in enumerate(self.tetris_board[:-1]):
						if 0 not in curr_row:
							self.tetris_board = remove_entire_row(
							  self.tetris_board, i)
							cleared_rows += 1
							break
					else:
						break
				self.add_cl_lines(cleared_rows)
				return True
		return False
	
	def instant_drop(self):
		if not self.gameover and not self.paused:
			while(not self.drop(True)):
				pass
	
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate_blocks_clockwise(self.stone)
			if not check_blocks_collision(self.tetris_board,
			                       new_stone,
			                       (self.stone_x, self.stone_y)):
				self.stone = new_stone
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False
	
	def run(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			'RETURN':	self.instant_drop
		}
		
		self.gameover = False
		self.paused = False
		
		dont_burn_my_cpu = pygame.time.Clock()
		while 1:
			self.screen.fill((0,0,0))
			if self.gameover:
				self.center_msg("""Game Over!\nYour score: %d
Press space to continue""" % self.score)
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					pygame.draw.line(self.screen,
						(255,255,255),
						(self.rlim+1, 0),
						(self.rlim+1, self.height-1))
					self.display_msg("Next:", (
						self.rlim+block_size,
						2))
					self.display_msg("Score: %d\n\nLevel: %d\
\nLines: %d" % (self.score, self.level, self.lines),
						(self.rlim+block_size, block_size*5))
					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.tetris_board, (0,0))
					self.draw_matrix(self.stone,
						(self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone,
						(cols+1,2))
			pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.drop(False)
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_"
						+key):
							key_actions[key]()
					
			dont_burn_my_cpu.tick(frames_per_sec)

if __name__ == '__main__':
	App = TetrisGame()
	App.run()
tetris.py
