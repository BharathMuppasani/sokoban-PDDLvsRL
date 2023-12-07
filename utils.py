import numpy as np
import os
import glob

def get_shape(positions):
    max_row = 0
    max_col = 0

    for pos in positions:
        parts = pos.split('-')
        if len(parts) == 3:
            col, row = int(parts[1]), int(parts[2])
            max_col = max(max_col, col)
            max_row = max(max_row, row)

    # Assuming one-indexed positions, the shape of the matrix is max_row x max_col
    return max(max_row, max_col), max(max_row, max_col)

def find_matrix_shape(pddl_file):

    # Read the PDDL file
    with open(pddl_file, 'r') as file:
        pddl_content = file.read()

    # Find the (:objects) section
    start = pddl_content.find("(:objects")
    end = pddl_content.find(")", start)
    objects_section = pddl_content[start:end]

    # Split the objects section by newline and strip each line
    lines = objects_section.split('\n')
    objects = [line.strip() for line in lines if line.strip()]

    # Extract the object name (before the hyphen) from each line
    object = [obj.split(' - ')[0].strip() for obj in objects if ' - ' in obj]

    matrix_pos_items = [pos_item for pos_item in object if 'pos-' in pos_item]

    return get_shape(matrix_pos_items)

def extract_init_predicates(pddl_file):
    # Find the (:init) section
    with open(pddl_file, 'r') as file:
        pddl_content = file.read()
    start = pddl_content.find("(:init")
    end = pddl_content.find("(:goal")
    init_section = pddl_content[start:end]
    # Split the init section by newline and strip each line
    lines = init_section.split('\n')
    predicates = [line.strip() for line in lines 
                  if line.strip() and line.strip().startswith("(") and line.strip().endswith(")")]

    return predicates


def get_agent_pos(predicates):

    for pred in predicates:
        if '(at player' in pred:
            y, x = [int(item.strip(')')) for item in pred.split(' ')[2].split('-')[1:]]
            return np.array([x-1, y-1])

def generate_matrices(matrix_shape, predicates):
    # Initialize matrices with False values
    # if matrix_shape[0] > 10 or matrix_shape[1] > 10:
    #     print('Too large environment for DeepCubeA rep. - Matrix shape: ', matrix_shape)
    #     return None, None, None
    
    # print(matrix_shape)
    matrix_shape = (max(matrix_shape[0], matrix_shape[1]), max(matrix_shape[0], matrix_shape[1]))
    # print(matrix_shape)

    stones_matrix = np.full(matrix_shape, False, dtype=bool)
    goals_matrix = np.full(matrix_shape, False, dtype=bool)
    walls_matrix = np.full(matrix_shape, True, dtype=bool)  # Initially all positions are walls

    # print(matrix_shape)
    # print(stones_matrix)

    for pred in predicates:
        if '(at stone' not in pred and '(IS-GOAL ' not in pred and '(clear ' not in pred:
            continue

        # Extract position and predicate type
        pred_type = pred.split(' ')[0].strip()
        if '(at stone' in pred:
            y, x = [int(item.strip(')')) for item in pred.split(' ')[2].split('-')[1:]]
        else:
            y, x = [int(item.strip(')')) for item in pred.split(' ')[1].split('-')[1:]]

        # print(pred, pred_type, y, x)
        y, x = int(y) - 1, int(x) - 1  # Adjust for zero-indexing
        
        if pred_type == '(at':
            # Update stones matrix
            stones_matrix[x , y] = True
            walls_matrix[x, y] = False
        elif pred_type == '(IS-GOAL':
            # Update goals matrix
            goals_matrix[x, y] = True
            walls_matrix[x, y] = False
        elif pred_type == '(clear':
            # Update walls matrix
            walls_matrix[x, y] = False

    return stones_matrix, goals_matrix, walls_matrix

def process_pddl_plan(plan_file):

    dir_dict = {
        'dir-up': 0,
        'dir-down': 1,
        'dir-left': 2,
        'dir-right': 3,
    }

    with open(plan_file, 'r') as f:
        cont = f.read()

    plan_list = [item.split(' ')[-1].replace(')', '') for item in cont.split('\n') if '; cost' not in item and item.strip()]
    plan_list = [dir_dict[item] for item in plan_list]
    return plan_list
