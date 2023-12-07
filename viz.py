import tkinter as tk
import copy
import argparse
from utils import *

def draw_grid(canvas, matrix_shape, agent_pos, boxes, goals, walls):
    canvas.delete("all") # Clear the canvas
    for y in range(matrix_shape[0]):
        for x in range(matrix_shape[1]):
            if walls[y, x]:
                canvas.create_rectangle(x*50, y*50, x*50+50, y*50+50, fill="gray")
            if boxes[y, x]:
                canvas.create_rectangle(x*50, y*50, x*50+50, y*50+50, fill="brown")
            if goals[y, x]:
                canvas.create_oval(x*50+10, y*50+10, x*50+40, y*50+40, fill="gold")
    canvas.create_oval(agent_pos[1]*50+10, agent_pos[0]*50+10, agent_pos[1]*50+40, agent_pos[0]*50+40, fill="green")

def process_move(move, canvas, agent_pos, boxes, goals, walls):
    directions = {0: 'Up', 1: 'Down', 2: 'Left', 3: 'Right'}
    direction = directions.get(move, '')
    if direction:
        key_pressed(direction, canvas, agent_pos, boxes, goals, walls)

def key_pressed(direction, canvas, agent_pos, boxes, goals, walls):
    dx, dy = 0, 0
    if direction == 'Up':
        dy = -1
    elif direction == 'Down':
        dy = 1
    elif direction == 'Left':
        dx = -1
    elif direction == 'Right':
        dx = 1

    # Compute new position of the agent
    new_x, new_y = agent_pos[0] + dy, agent_pos[1] + dx

    # Check if the new position is within bounds and not a wall
    if 0 <= new_x < len(walls) and 0 <= new_y < len(walls) and not walls[new_x][new_y]:
        # Check if there's a box in the new position
        if boxes[new_x][new_y]:
            # Compute new position of the box
            box_new_x, box_new_y = new_x + dy, new_y + dx
            # Check if the box can be moved
            if 0 <= box_new_x < len(walls) and 0 <= box_new_y < len(walls) and not walls[box_new_x][box_new_y] and not boxes[box_new_x][box_new_y]:
                boxes[new_x][new_y] = False
                boxes[box_new_x][box_new_y] = True
                agent_pos[0], agent_pos[1] = new_x, new_y
        else:
            # Move the agent if there's no box
            agent_pos[0], agent_pos[1] = new_x, new_y

    # Redraw the grid
    draw_grid(canvas, matrix_shape, agent_pos, boxes, goals, walls)

def animate_moves(moves, canvas, agent_pos, boxes, goals, walls, index=0):
    if index < len(moves):
        process_move(moves[index], canvas, agent_pos, boxes, goals, walls)
        root.after(200, lambda: animate_moves(moves, canvas, agent_pos, boxes, goals, walls, index + 1))

# write python basic main function
if __name__ == '__main__':
    # get required arguments --dc (default false), --problem and --plan
    parser = argparse.ArgumentParser()
    parser.add_argument('--problem', type=str, required=True)
    parser.add_argument('--plan', type=str, required=True)
    parser.add_argument('--dc', default=0, type=int)

    args = parser.parse_args()

    # Initialize Tkinter window
    root = tk.Tk()
    root.title("Sokoban")

    # Initialize Canvas
    canvas = tk.Canvas(root, width=800, height=800)
    canvas.pack()

    matrix_shape = find_matrix_shape(args.problem)
    predicates = extract_init_predicates(args.problem)
    agent_pos = get_agent_pos(predicates)
    stones_matrix, goals_matrix, walls_matrix = generate_matrices(matrix_shape, predicates)

    walls_matrix[agent_pos[0], agent_pos[1]] = False
    # Game state
    agent_pos = agent_pos
    boxes = stones_matrix
    goals = goals_matrix
    walls = walls_matrix


    draw_grid(canvas, matrix_shape, agent_pos, boxes, goals, walls)

    if args.dc:
        # Read plan from file
        with open(args.plan, 'r') as file:
            moves_list = file.read().split('\n')
        # Remove empty lines
        moves = [int(line.strip()) for line in moves_list if line.strip()]
    else:
        moves = process_pddl_plan(args.plan)

        
    # List of moves for animation
    # moves = [0, 0]
    animate_moves(moves, canvas, agent_pos, boxes, goals, walls)

    root.mainloop()
