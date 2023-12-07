import os
import glob
import json

planner_path = '/work/bharath/rubiks_cube/downward5/'

problems_path = '/work/bharath/sokoban/sokoban_problem_files/'

results_path = '/work/bharath/sokoban/sokoban_results/'
domain_file = '/work/bharath/sokoban/domain.pddl'

search_dict = {
    # 'lm_count': 'astar(lmcount(lm_rhw(disjunctive_landmarks=true, verbosity=normal, use_orders=true, only_causal_landmarks=false), admissible=false, optimal=false, pref=false, alm=true, lpsolver=CPLEX, verbosity=normal, transform=no_transform(), cache_estimates=true))',
    # 'lm_cost': "astar(landmark_cost_partitioning(lm_rhw(disjunctive_landmarks=true, verbosity=normal, use_orders=true, only_causal_landmarks=false), pref=false, verbosity=normal, transform=no_transform(), cache_estimates=true, optimal=false, alm=true, lpsolver=cplex))",
    # 'ff': "astar(ff(verbosity=normal, transform=no_transform(), cache_estimates=true))",
    # 'causal_graph': "astar(cg(max_cache_size=1000000, verbosity=normal, transform=no_transform(), cache_estimates=true))",
    # 'goal_count': "astar(goalcount(verbosity=normal, transform=no_transform(), cache_estimates=true))",
    'blind': "astar(blind(verbosity=normal, transform=no_transform(), cache_estimates=true))",
    # 'context_enhanced_additive': "astar(cea(verbosity=normal, transform=no_transform(), cache_estimates=true))",
    # 'max': "astar(hmax(verbosity=normal, transform=no_transform(), cache_estimates=true))"
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
    
    

