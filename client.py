#!/usr/bin/python

import socket
import binascii
from struct import *
import struct
import sys
import time
from ctypes import *
import ctypes

#############
## Globals ##
#############
global maze
maze = {}


#############
## Classes ##
#############
class Cell:
	def __init__(self, number):
		self.number = number
		self.walls = 0
		self.borders = 0
		self.add_borders()
		self.neighbors = []
		self.set_neighbors()

	def __str__(self):
		r = "Cell Number: " + str(self.number) + "\n"
		r += "Cell Walls: " + "{0:04b}".format(self.walls) + "\n"
		r += "Cell Borders: " + "{0:04b}".format(self.borders) + "\n"
		#r += "Cell Neighbors: " + "{0:04b}".format(self.neighbors) + "\n"
		
		return r

	def set_neighbors(self):
		if (self.borders & 4 == 0): self.neighbors.append(self.number - maze["width"])
		if (self.borders & 1 == 0): self.neighbors.append(self.number + maze["width"])
		if (self.borders & 8 == 0): self.neighbors.append(self.number + 1)
		if (self.borders & 2 == 0): self.neighbors.append(self.number - 1)
		

	def add_borders(self):
		# bottom border
		if (self.number >= (maze["width"] * (maze["height"] - 1)) ): self.borders += 1
		# left border
		if (self.number%maze["width"] == 1): self.borders += 2
		# top border
		if (self.number <= maze["width"]): self.borders += 4
		# right border
		if (self.number%maze["width"] == 0): self.borders += 8

	def add_walls(self,walls):
		self.walls = walls&15


	

#############
# Functions #
#############

# maze_board: takes in maze data, updates maze with "width", "height" and "walls"
def maze_board(input_data):
	i=0
	j=2
	maze_data = []
	while (j<=len(input_data)):
		maze_data.append(input_data[i:j])
		i+=2
		j+=2	

	maze["width"] = int(maze_data[0],16)
	maze["height"] = int(maze_data[1],16)
	maze["size"] = maze["width"] * maze["height"]


	maze["cells"] = {}
	for c in range(2,len(maze_data)):
		cell = Cell(c-1)
		cell.add_walls(int(maze_data[c],16))
		maze["cells"][c-1] = cell


########################
# 	get_player_in_cell
########################
def get_player_in_cell(players, current_cell):
	"""Given the players returns the player that is in the cell 
		string for the given cell
	Returns number of player in cell, 0 if none"""

	positions = []
	for p in players:
		positions.append(players[p]['pos'])

	try:
		return positions.index(current_cell) + 1
	except ValueError:
		return 0


########################
# 	get_cell_contents
########################
def get_cell_contents(players, current_cell):
	"""Given the maze cell index and the player list returns the cell contents 
		string for the given cell
	Returns string"""
	
	player = get_player_in_cell(players, current_cell)

	if player == 0:
		return "   "

	if player < 9:
		outstr = " %d " % player
	else:
		if player < 99:
			outstr = " %d" % player
		else:
			outstr = "%d" % player

	return outstr


########################
# 	print_maze
########################
def print_maze(amaze, players):
	"""Print the maze to the screen
	Returns None"""

	line = "+"
	column = 1

	# Handle the top border of the maze
	#
	while column <= amaze["width"]:
		line += "---"
		if (amaze["cells"][column].walls & 0x01) <> 0:
			line += "-"
		else:
			line += "+"

		column += 1
	print line

	# Now we handle generating the row of cell data and bottom border
	#
	row = 1
	while row <= amaze["height"]:
		row_offset = (row - 1) * amaze["width"]
		next_row_offset = row_offset + amaze["width"]

		column = 1
		line = "|"

		# Now we build the string for the insides of the cells
		#
		while column <= amaze["width"]:

			this_cell = row_offset + column
			
			line += get_cell_contents(players, this_cell)
			if (amaze["cells"][this_cell].walls & 0x01) == 0:
				line += "|"
			else:
				line += " "

			column += 1

		# Output the row of cells
		print line


		# Now we need to build a string for the lower border of the cell row
		# But don't output the bottom border for the last row, we do that seperately
		if row < amaze["height"]:
			column = 1
			this_cell = row_offset + column

			if (amaze["cells"][this_cell].walls & 0x08) == 0:	# wall below, this cell
				line = "+"
			else:
				line = "|"

			# Now the rest of the bottom borders for the cells
			#
			while column < amaze["width"]:

				this_cell = row_offset + column
				cell_right = row_offset + column + 1
				cell_below = next_row_offset + column


				# build the bottom of the current cell
				if (amaze["cells"][row_offset + column].walls & 0x08) == 0:
					line += "---"
				else:
					line += "   "

				
				outstr = "*"

				# Now for the char between the cells
				#
				if (amaze["cells"][this_cell].walls & 0x08) == 0:	# wall below, this cell		
					# wall below, this cell	
					outstr = "+"
					if (amaze["cells"][cell_right].walls & 0x08) == 0:	# wall below, cell to the right	

						outstr = "+"
						if (amaze["cells"][this_cell].walls & 0x01) <> 0:	# open right, this cell
							outstr = "-"

				else:

					# open below this cell
					outstr = "+"
					if (amaze["cells"][cell_right].walls & 0x08) <> 0:	# open below, cell to the right

						outstr = "+"
						if (amaze["cells"][this_cell].walls & 0x01) == 0:	# wall right, this cell
							if (amaze["cells"][cell_below].walls & 0x01) == 0:	# wall right, cell below

								outstr = "|"
							else:
								outstr = "+"
				
				line += outstr
				column += 1

			# Handle the last filling and char of the border
			if (amaze["cells"][row_offset + column].walls & 0x08) == 0:
				line += "---+"
			else:
				line += "   |"

			# Output the bottom border of the row of cells
			print line

		row += 1



	# To finish it off we need to output the botton border
	#		
	line = "+"
	column = 1
	while column < amaze["width"]:
		row_offset = (amaze["height"] - 1) * amaze["width"]
		line += "---"

		if (amaze["cells"][row_offset + column].walls & 0x01) <> 0:
			line += "-"
		else:
			line += "+"

		column += 1
	line += "   +"
	print line

	return None


########################
# get_jump_right_value
########################
def	get_jump_right_value(amaze, players, our_position):
	"""Calculated the value of a jump to the right
		Return values:
			0 : illegal move
			x : valid jump will advance x spaces
	Returns integer"""

	target_pos = our_position + 1
	value = 1

	# start one to the right then check for consecutive players
	while target_pos < amaze["width"]:
		# Is there a player in the cell we are inspecting
		if get_player_in_cell(players, target_pos) <> 0:
			value += 1
		else:
			break
		target_pos += 1

	# Calc the position of the last cell of our row
	last_position_of_row = ((our_position / amaze["width"]) + 1) * amaze["width"]

	# Check to see if we are outside of the maze
	if (our_position + value) > last_position_of_row:
		value = 0
	else:
		# Check for an open landing space
		if get_player_in_cell(players, our_position + value) <> 0:
			value = 0

	return value
	

########################
# get_jump_down_value
########################
def	get_jump_down_value(amaze, players, our_position):
	"""Calculated the value of a jump down
		Return values:
			0 : illegal move
			x : valid jump will advance x spaces
	Returns integer"""

	target_pos = our_position + amaze["width"]
	value = 1

	# start one to the right then check for consecutive players
	while target_pos < amaze["width"] * amaze["height"]:
		# Is there a player in the cell we are inspecting
		if get_player_in_cell(players, target_pos) <> 0:
			value += 1
		else:
			break
		target_pos += amaze["width"]

	# Calc the position of the last cell of our row
	last_position_of_row = amaze["width"] * amaze["height"]

	# Check to see if we are outside of the maze
	if target_pos > last_position_of_row:
		value = 0
	else:
		# Check for an open landing space
		if get_player_in_cell(players, our_position + (value * amaze["height"])) <> 0:
			value = 0

	return value
	
	
########################
# move_value
########################
def	move_value(amaze, players, our_player, move):
	"""Calculated the value of the given move with the current maze and players
		Return values:
			0 : illegal move
			x : valid move will advance x spaces
	Returns integer"""

	playerIdx = our_player
	playerPos = players[our_player]['pos']

	borders = amaze["cells"][playerPos].borders
	walls = amaze["cells"][playerPos].walls

	at_right_wall = (playerPos % amaze["width"]) == 0
	at_bottom_wall = playerPos > (amaze["width"] * (amaze["height"]-1))
	winnersCircle = amaze["width"] * amaze["height"]

	# Right move requested
	#
	if move == 'd':
		player2right = get_player_in_cell(players, playerPos+1) <> 0

		# At right maze border and asking to go right
		if at_right_wall:
			return 0

		# Wall to right and asking to go right
		if walls & 0x01 == 0:
			return 0
	
		# Check for a player to the right
		if player2right:
			return 0

		return 1


	# Right Jump requested
	#
	if move =='D':
		player2right = get_player_in_cell(players, playerPos+1) <> 0

		# At right maze border and asking to jump it
		if at_right_wall:
			return 0

		# No wall to right and asking to jump
		if walls & 0x01 <> 0 and not player2right:
			return 0
		else:
			return get_jump_right_value(amaze, players, playerPos)

		

	# Down move requested
	#
	if move == 's':
		player_below = get_player_in_cell(players, playerPos + amaze["width"]) <> 0

		if at_bottom_wall:
			return 0

		# Wall to right and asking to go right
		if walls & 0x08 == 0:
			return 0

		# Check for a player below
		if player_below:
			return 0
	
		return 1


	# Down Jump requested
	#
	if move =='S':
		player_below = get_player_in_cell(players, playerPos + amaze["width"]) <> 0

		# At bottom maze border and asking to jump it
		if at_bottom_wall:
			return 0

		# No wall to right and asking to jump
		if walls & 0x08 <> 0 and not player_below:
			return 0
		else:
			return get_jump_down_value(amaze, players, playerPos)


	return 0

	
########################
# make_move
########################
def	make_move(amaze, players, player_number, favored_direction):
	"""Selects the next movefor our player
	Returns the code for the selected move"""

	# Get the value of each move and select the best one
	#	
	jump_right = move_value(amaze, players, player_number, "D")
	move_right = move_value(amaze, players, player_number, "d")
	jump_down = move_value(amaze, players, player_number, "S")
	move_down = move_value(amaze, players, player_number, "s")


	if favored_direction == "RIGHT":

		# When we have a good high value jump Right take it
		if jump_right > jump_down:
			return 0x12	#"D"		Jump Right

		# When we have a, good enough, move right take it
		if (move_right >= jump_down) and move_right > 0:
			return 0x0e	#"d"		Move Right

		# When we have a good jump Right take it
		if jump_right > 0:
			return 0x12	#"D"		Jump Right
	
		# When we have a move right take it
		if move_right > 0:
			return 0x0e	#"d"		Move Right

		# When we have a good jump Down take it
		if jump_down > 0:
			return 0x15	#"S"		Jump Down
	
		# Out of good options hoping this is legal, it should be
		return 0x11		#"s"			Move Down

	else:

		# When we have a good high value jump Right take it
		if jump_down > jump_right:
			return 0x15	#"S"		Jump Down

		# When we have a, good enough, move down take it
		if (move_down >= jump_right) and move_down > 0:
			return 0x11	#"s"		Move Down

		# When we have a good jump Down take it
		if jump_down > 0:
			return 0x15	#"S"		Jump Down
	
		# When we have a move right take it
		if move_down > 0:
			return 0x11	#"s"		Move Down

		# When we have a good jump Right take it
		if jump_right > 0:
			return 0x12	#"D"		Jump Right
	
		# Out of good options hoping this is legal, it should be
		return 0x0e		#"d"		Move Right


########################
# test_update_player_with_move
########################
def	test_update_player_with_move(amaze, players, player_moving, player_move):

	the_player = player_moving-1
	current_position = players[the_player]

	if player_move == "d":
		players[the_player] = current_position + 1
		return

	if player_move == 's':
		players[the_player] = current_position + amaze["width"]
		return

	if player_move == "D":
		players[the_player] = current_position + get_jump_right_value(amaze, players, current_position)
		return

	if player_move == 'S':
		players[the_player] = current_position + (amaze["width"] * get_jump_down_value(amaze, players, current_position))
		return


########################
# get_bytes
########################
def get_bytes(client, count):

	input = []
	i = 0
	while i < count:
		input.append(binascii.hexlify(client.recv(1)))
		i += 1

	return input

########################
# get_cmd
########################
def get_cmd(client):

	input = []
	temp_bytes = []

	input = get_bytes(client, 1)

	cmd = int(input[0],16)

	if cmd == 0:
		# Game welcome
		input.extend(get_bytes(client, 2))

	elif cmd == 1:
		# Board layout information
		temp_bytes = get_bytes(client, 2)	# size of compressed board
		size = (int(temp_bytes[1],16) * 256) + int(temp_bytes[0],16)
		input.append(size)
		input.extend(get_bytes(client, size))
		
	elif cmd == 4:
		# 
		print "We have been naughty!"

	elif cmd == 6:
		# Player position information
		input.extend(get_bytes(client, 3))

	elif cmd == 7:
		# Whos turn is it
		input.extend(get_bytes(client, 1))

	elif cmd == 9:
		# New player joined
		input.extend(get_bytes(client, 1))

	elif cmd == 10:
		input.extend(get_bytes(client, 1))

	elif cmd == 11:
		input.extend(get_bytes(client, 1))	



	return input


########################
# 
########################
def maze_path():
	paths = {}
	end = maze["width"] * maze["height"]

#################################################
# Use to pack a variable length array of numbers
#################################################
def pack_variable(*args):
	return struct.pack('%dB' % len(args), *args)


class genMazeStruct(Structure):
	_fields_ = [
		("Field1", c_ulonglong),
		("Field2", c_ulonglong),
		("Field3", c_ulonglong),
		("MazeAddr", POINTER(c_ulonglong))
		]
	

def decompress_maze(layout_size,data,maze_size):
	

	##########################################################
	# Obtain Compressed Structure of maze
	# Return address and ptr
	
	compress_data = ctypes.c_ulonglong(int(binascii.hexlify(data),16))
	
	# Get address of the compress_data
	compress_data_address = ctypes.addressof(compress_data)
	
	# Create pointer to compress_data_address
	compress_data_pointer = ctypes.cast(compress_data_address, POINTER(c_ulonglong))
	
	
	##############################################################
	# Create C structure for RDI: return address and pointer
	
	# Create Instance of genMazeStruct
	size = ctypes.c_ulonglong(layout_size)
	huh = ctypes.c_ulonglong(0x0000010000000000)
	
	maze_struct = genMazeStruct(0,huh,size,compress_data_pointer)
	
	#print binascii.hexlify(string_at(compress_data_address,8))
	
	# Get address for this structure
	struct_addr = ctypes.addressof(maze_struct)
	
	#print binascii.hexlify(string_at(compress_data_address,8))
	# Create Pointer for structure
	struct_pointer = ctypes.cast(struct_addr, POINTER(c_ulonglong))
	
	##############################################
	# Build and send call to generate_maze
	
	# Var to libmaze.so
	libmaze = cdll.LoadLibrary("libmaze.so")
	
	# var to generate_maze function
	gen_maze = libmaze.generate_maze
	
	# Setting arg types of gen_maze -- SIGNATURE 
	gen_maze.argtypes = [c_uint,c_uint,c_ulonglong,c_uint,c_uint,c_uint,c_uint,c_uint,c_ulonglong]
	
	# Call function
	uncompress_data = gen_maze(0,0,struct_addr,0,0,0,0,0,compress_data_address)
	uncompress_string =  binascii.hexlify(string_at(uncompress_data,maze_size+2 ))
	return uncompress_string


		
def main():
	
	# Do some initializations
	done = False
	wins = 0
	loses = 0
	illegal_moves = 0
	total_illegal_moves = 0
	jumps_attempted = 0
	favored_direction = "RIGHT"
	sleepy_time = 0
	the_players = {}
	our_player_num = -1	# player number start at 0	

	if len(sys.argv) < 2:
		print "\nUsage: Client ip_address {sleep seconds between moves}\n"
		return
	elif len(sys.argv) > 2:
		sleepy_time = sys.argv[2]


	# setup the socket to communicate with the server then connect
	#
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	IP = sys.argv[1]
	PORT = 8008
	sock = (IP, PORT)
	client.connect(sock)

	# main loop

	# so we know when it will be our turn
	whos_turn = -1

	while not done:

		# Get a command from the server
		cmd_bytes = get_cmd(client)

		cmd = int(cmd_bytes[0],16)

		# Game welcome
		if cmd == 0:
			# bytes: our player#, max players
			our_player_num = int(cmd_bytes[1],16)

			the_players[our_player_num] = {"x": 0, "y": 0, "pos": 0}

		# Board layout information
		elif cmd == 1:
			illegal_moves = 0
			jumps_attempted = 0

			layout_size = cmd_bytes[1]

			height = int(cmd_bytes[2],16)
			width = int(cmd_bytes[3],16)
			maze_size = height * width

			s = []
			f = 'B' * layout_size
			struct_format = Struct(f)
			for i in range(0,layout_size):
				s.append(int(cmd_bytes[layout_size+1-i],16))

			maze_struct = struct_format.pack(*s)

			uncompress_maze_data = decompress_maze(layout_size,maze_struct,maze_size)

			# setup the maze
			maze_board(uncompress_maze_data)

			for p in the_players:
				the_players[p]['pos'] = (the_players[p]['y'] * maze["height"]) + (the_players[p]['x'] + 1)

			# setup our favored direction flag
			if maze["height"] > maze["width"]:
				favored_direction = "DOWN"
			else:
				favored_direction = "RIGHT"
			
		# We sent a bad command!
		elif cmd == 4:
			print "We have been naughty! Oh My!!"
			illegal_moves += 1
			total_illegal_moves += 1

			# may help if we are lost
			if move == 18 or move == 14:
				favored_direction = "DOWN"
			else:
				favored_direction = "RIGHT"

		elif cmd == 5:
			# no idea, meditate on it
			time.sleep(1)
			

		# Player position information
		elif cmd == 6:
			p = int(cmd_bytes[1],16)
			p_x = int(cmd_bytes[2],16)
			p_y = int(cmd_bytes[3],16)

			# When this is true we have the maze dimensions
			try:
				p_pos = (p_y * maze["height"]) + (p_x + 1)
			except KeyError:
				p_pos = 0

			the_players[p] = {"x": p_x, "y": p_y, "pos": p_pos}

		elif cmd == 7:
			# Whos turn is it, based 1
			whos_turn = int(cmd_bytes[1],16)
			if (whos_turn == int(our_player_num)): 
				print "Hey it's my turn now!"
			else:
				print "It is %d's turn" % (int(whos_turn)+1)

		# New player joined
		elif cmd == 9:
			player_num = int(cmd_bytes[1],16)
			if (player_num != our_player_num): print "I Will Crush Player %d" % (int(player_num)+1)
			the_players[player_num] = {"x": 0, "y": 0, "pos": 0}

		# Player left the game
		elif cmd == 10:
			p = int(cmd_bytes[1],16)
			print "Player %d is going home to cry" % p + 1
			the_players.remove(p)
			print "the Players: ", the_players	

		# We have a winner, check to see if it is us
		elif cmd == 11:
			winner = int(cmd_bytes[1],16)
			if winner == our_player_num:
				wins += 1
				print "***** We WIN!! With a record of %d WINS and %d loses *****" % (wins, loses)
				print "With only %d Illegal moves, total illegals %d" % (illegal_moves, total_illegal_moves)
			else:
				print "I can't believe I lost to player %d" % (winner)
				loses += 1

			print "We have %d Illegal moves this game, total Illegals all games: %d" % (illegal_moves, total_illegal_moves)

			if (wins + loses) >= 10:
				break

		elif cmd == 12:
			# no idea, meditate on it
			time.sleep(1)
			
		else:
			print "Got ILLEGAL command code (%d)" % cmd


		# Handle our turn, if it is time
		#
		if whos_turn == our_player_num:

			print_maze(maze, the_players)

			our_move = make_move(maze, the_players, our_player_num, favored_direction)
			move = our_move
			if our_move == 0x12 or our_move == 0x15:
				jumps_attempted += 1
			client.send(chr(our_move))

			if sleepy_time:
				time.sleep(float(sleepy_time))

			# flip over to prefering the other direction
			if move == 18 or move == 14:
				favored_direction = "DOWN"
			else:
				favored_direction = "RIGHT"

			whos_turn = -1


	print "***** With a record of %d WINS and %d loses *****" % (wins, loses)
	print "With only %d Illegal moves, total illegals %d" % (illegal_moves, total_illegal_moves)
	print "Players: ", the_players
	print "We were last at position %d" % (the_players[our_player_num])
	print "Cell Data: ", hex(maze["cells"][the_players[our_player_num]].walls)
	print "cell: ", maze["cells"][the_players[our_player_num]]

	client.shutdown(socket.SHUT_RDWR)
	client.close()

	#return

if __name__ == "__main__":
	main()

