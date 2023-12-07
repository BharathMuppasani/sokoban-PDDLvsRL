import os
import glob
import json

planner_path = '/work/bharath/rubiks_cube/scorpion2/'

problems_path = '/work/bharath/sokoban/sokoban_problem_files/'

results_path = '/work/bharath/sokoban/sokoban_results/'
domain_file = '/work/bharath/sokoban/domain.pddl'

search_dict = {
# 'max-manual-pdb': 'astar(maximize([projections(manual_patterns([[ 455, 431, 407, 479]]), create_complete_transition_system=true), projections(manual_patterns([[ 335, 383, 359, 311]]), create_complete_transition_system=true), projections(manual_patterns([[ 239, 287, 215, 263]]), create_complete_transition_system=true), projections(manual_patterns([[ 143, 167, 119, 191]]), create_complete_transition_system=true), projections(manual_patterns([[ 47, 95, 23, 71]]), create_complete_transition_system=true)]))',
'merge-and-shrink': 'astar(merge_and_shrink(shrink_strategy=shrink_bisimulation(greedy=false),merge_strategy=merge_sccs(order_of_sccs=topological, merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order])),label_reduction=exact(before_shrinking=true,before_merging=false),max_states=50000,threshold_before_merge=1))',
# 'max-systematic-pdb': 'astar(maximize([projections(systematic(3), create_complete_transition_system=true)]))'
}

def extract_params(output_file):
    with open(output_file, 'r') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    for line in lines:
        if 'Expanded' in line and 'until' not in line:
            expanded = int(line.split('Expanded')[-1].strip().split(" ")[0].strip())
        elif 'Evaluated' in line and 'until' not in line:
            evaluated = int(line.split('Evaluated')[-1].strip().split(" ")[0].strip())
        elif 'Generated' in line and 'until' not in line:
            generated = int(line.split('Generated')[-1].strip().split(" ")[0].strip())
        elif 'Search time' in line:
            search_time = round(float(line.split(':')[-1].strip().replace('s', '')), 6)
        elif 'Total time' in line:
            total_time = round(float(line.split(':')[-1].strip().replace('s', '')), 6)

    return expanded, evaluated, generated, search_time, total_time

def execute_planner(plan, domain, problem, output, search, planner_path):
    current_path = os.getcwd()
    os.chdir(planner_path)
    command_str = f'python fast-downward.py --overall-memory-limit 8192M --plan-file {plan} {domain} {problem} --search "{search}" > {output}'
    os.system(f'timeout 30m {command_str}')
    os.chdir(current_path)

def get_output(domain_file, problem_file, output_file, plan_file, params_file, search_algorithm, planner_path):

    output_dict = {}
    execute_planner(plan_file, domain_file, problem_file, output_file, search_dict[search_algorithm], planner_path)
    if "Solution found" in open(output_file).read(): 
        with open(plan_file, 'r') as f:
            plan = f.readlines()
        plan = [item.strip().replace('(', '').replace(')', '').strip() for item in plan if ';' not in item]
        # for i in range(len(plan)):
        #     if 'rev' in plan[i]:
        #         plan[i] = plan[i].replace('rev',"'")
        #         plan[i] = plan[i].capitalize()
        #     else:
        #         plan[i] = plan[i].capitalize()
        
        output_dict['plan'] = plan
        output_dict['plan_length'] = len(plan)

        expanded, evaluated, generated, search_time, total_time = extract_params(output_file)
        output_dict['expanded'] = expanded
        output_dict['evaluated'] = evaluated
        output_dict['generated'] = generated
        output_dict['search_time'] = search_time
        output_dict['total_time'] = total_time

        # save output_dict to json file params_file
        json.dump(output_dict, open(params_file, 'w'), indent=4)

    return None

if __name__ == '__main__':

    problem_files = glob.glob(problems_path + '*.pddl')
    for key in search_dict.keys():
        # create a folder with search algorithm name
        print(f'Running {key} search algorithm on {problems_path}')
        results_folder = os.path.join(results_path, key)
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        
        for problem_file in problem_files:
            problem_name = problem_file.split('/')[-1].replace('.pddl', '')
            output_file = os.path.join(results_folder, problem_name.replace('instance', 'output') + '.txt')
            plan_file = os.path.join(results_folder, problem_name.replace('instance', 'plan') + '.txt')
            params_file = os.path.join(results_folder, problem_name.replace('instance', 'params') + '.json')
            get_output(domain_file, problem_file, output_file, plan_file, params_file, key, planner_path)
    

