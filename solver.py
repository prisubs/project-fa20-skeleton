import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness
import sys
from os.path import basename, normpath
import glob

def solve(G, s, magic):
    """
    Args:
        G: networkx.Graph
        s: stress_budget
    Returns:
        D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
        k: Number of breakout rooms
    """
    # helper function to do assignments
    def assign(u, v, room):
        assignments[u] = room
        assignments[v] = room
        assigned[u] = True
        assigned[v] = True
        inhabitants.extend([u, v])

    # Initializing data structures
    n = len(G)
    hap = [[0] * n] * n
    strez = [[0] * n] * n
    ratio_pairs = []

    # Fill hapiness and stress matrices
    # Build priority queue of ratios
    for i, j, a in G.edges(data=True):
         h_ij = a['happiness']
         s_ij = a['stress']

         # Initialize matrices
         hap[i][j] = h_ij
         hap[j][i] = h_ij
         strez[i][j] = s_ij
         strez[j][i] = s_ij

         # Calculate ratio, put in ratio pq
         if s_ij == 0:
            rat = h_ij
         else:
            rat = h_ij/s_ij

         ratio_pairs.append((i, j, rat))

    # Set up data structures for assignment phase
    ratio_pairs = sorted(ratio_pairs, key = lambda g: -1*g[2])
    assignments, assigned = {}, [False] * n
    current_room, current_room_stress, inhabitants = 0, 0, []

    # TODO change this threshold, could check at every possible value of k
    # s/n is the lowest possible value it can take on
    threshold = s/magic

    # Iterate through pairs and perform assignments
    for student_pair in ratio_pairs:
        if current_room > magic:
            return {}, 0
        u, v = student_pair[0], student_pair[1]
        stress = strez[u][v]

        # If either are already assigned, we don't disturb that assignment
        if assigned[u] or assigned[v]:
            continue

        # Calculate the new room stress after adding this pair
        # TODO: maybe better to evaluate stress after adding u, adding v, adding both
        potential_stress = current_room_stress + stress
        for i in inhabitants:
            potential_stress += strez[u][i]
            potential_stress += strez[v][i]

        # Case 1: potential stress is lower than the threshold
        if potential_stress < threshold:
            current_room_stress = potential_stress
            assign(u, v, current_room)
        # Case 2: potential stress is equal to the threshold
        elif potential_stress == threshold:
            assign(u, v, current_room)
            current_room_stress, inhabitants = 0, []
            current_room += 1
        # Case 3: potential stress exceeds threshold
        else:
            if stress > threshold:
                u_stress = sum([strez[u][i] for i in inhabitants])
                v_stress = sum([strez[v][i] for i in inhabitants])
                smaller = min(u_stress, v_stress)

                if current_room_stress + smaller > threshold:
                    assignments[u] = current_room + 1
                    assignments[v] = current_room + 2
                    assigned[u] = True
                    assigned[v] = True
                    current_room += 3
                    current_room_stress = 0
                    inhabitants = []
                else:
                    # put smaller in room, open new room
                    continue
            else:
                current_room_stress = stress
                current_room += 1
                assign(u, v, current_room)

    return assignments, len(set(list(assignments.values()))) + 1

# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
#     assert len(sys.argv) == 2
#     path = sys.argv[1]
#     G, s = read_input_file(path)
#     D, k = solve(G, s, 30)
#     assert is_valid_solution(D, G, s, k)
#     print("Total Happiness: {}".format(calculate_happiness(D, G)))
#     write_output_file(D, 'samples/10.out')

def dummy_solution(n):
    result = {}
    for i in range(n):
        result[i] = i
    return result
# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
if __name__ == '__main__':
    inputs = glob.glob('inputs/*')
    solved = 0
    defaulted = 0
    for input_path in inputs:
        output_path = 'outputs/' + basename(normpath(input_path))[:-3] + '.out'
        G, s = read_input_file(input_path)
        n = len(G)
        best_sol, best_happiness = None, 0
        for i in range(1, n+1):
            D, k = solve(G, s, i)
            if len(D) == n and is_valid_solution(D, G, s, k):
                happiness = calculate_happiness(D, G)
                if happiness > best_happiness:
                    best_sol = D
            else:
                continue
        if not best_sol:
            defaulted += 1
            print("Was not able to solve {}".format(input_path))
            best_sol = dummy_solution(n)
            write_output_file(best_sol, output_path)
        else:
            # Find highest happiness solution and write to file
            solved += 1
            print("Successfully solved {}".format(input_path))
            write_output_file(best_sol, output_path)
    print("TOTAL: SOLVED {}/{} OF THE INPUTS".format(solved, len(inputs)))
    print("TOTAL: DEFAULTED {}/{} OF THE INPUTS".format(defaulted, len(inputs)))
