import sys
import time
import copy
from collections import defaultdict

# Running script: given code can be run with the command:
# python file.py ./path/to/init_state.txt ./output/output.txt

import collections


class Sudoku(object):

    def __init__(self, puzzle):
        self.puzzle = puzzle 
        self.domains, self.constraints = self.csp(puzzle)

    def csp(self, state):
        var_domain = {}
        var_constraints = defaultdict(list)
        var_unassigned = 0

        # Initialize var_domain
        for row in range(9):
            for col in range(9):
                value = state[row][col]
                if value == 0:
                    var_domain[(row, col)] = set(range(1,10))
                else:
                    var_domain[(row, col)] = set([value])

        # Initialize var_constraints
        for row in range(9):
            for col in range(9):
                position = (row, col)
                neighbours = set()

                for i in range(0, 9):
                    #check neighbours in rows and cols
                    if i != row:
                        neighbours.add((i, col))
                    if i != col:
                        neighbours.add((row, i))
                #check neighbours in the small 3X3 grids
                start_row = (row // 3) * 3
                start_col = (col // 3) * 3
                for current_row in range(start_row, start_row + 3):
                    for current_col in range(start_col, start_col + 3):
                        if current_col == col or current_row == row:
                            continue  # if its the same position ignore it
                        else:
                            neighbours.add((current_row, current_col))
                var_constraints[position] = neighbours
                  
        return var_domain, var_constraints

    def solve(self):
        state = self.puzzle
        assigned_pos, unassigned_pos = self.get_assigned_unsigned_positions(state)     
        deque = self.initialize_arc_deque(assigned_pos, unassigned_pos)        
        self.domains = self.forward_checking(deque, self.domains)              
        return self.backtrack(state, self.domains, unassigned_pos)

    def backtrack(self, state, domains, unassigned_positions):
        if not unassigned_positions:
            return state

        variable = self.select_unassigned_variable(unassigned_positions, domains)
        row = variable[0]
        col = variable[1]
        removed = defaultdict(set)

        for value in self.order_domain_value(variable, domains):
            if self.is_consistent(value, variable, state):
                state[row][col] = value  # assign to value to the corresponding position on the puzzle
                original_variable_domain = domains[variable]  # original doamin saved to restore the initial state
                domains[variable] = set([value])

                if self.inference(domains, variable, value, removed):
                    result = self.backtrack(state, domains, unassigned_positions)
                    # make a assignment successfully 
                    if result:
                        return result
                # restoring the inferences and original states
                for position in removed:
                    domains[position] |= removed[position]
                domains[variable] = original_variable_domain
            state[row][col] = 0

        unassigned_positions.add(variable)
        return []  # fail

    def select_unassigned_variable(self,  unassigned_positions, domains):
        # choose the Most constrained variable, minimum-remaining-values (MRV) heuristic with 
        # most Constraining Variable as a tie breaker
        most_constrained_var = set()
        fewest_domain_size = 10

        for unassigned_position in unassigned_positions:
            domain_length = len(domains[unassigned_position])
            if domain_length < fewest_domain_size:
                most_constrained_var = set() 
                fewest_domain_size = domain_length

            if domain_length == fewest_domain_size:
                   most_constrained_var.add(unassigned_position)  
        
        most_constraining_var = None
        most_constraints = 0

        for var in most_constrained_var:
            num_constraints = 0
            for constraint in self.constraints[var]:
                if isinstance(domains[constraint], set):
                    num_constraints += 1

            if num_constraints >= most_constraints:
                most_constraining_var = var
                most_constraints = num_constraints

        unassigned_positions.remove(most_constraining_var)
        return most_constraining_var

    def order_domain_value(self, variable, domains):
        # order the domain by Least Constraining Value 
        neighbours = self.constraints[variable]  
        value_count_tuples = set()

        for value in domains[variable]:
            count = 0
            for neighbour in neighbours:
                if value in domains[neighbour]:
                    count += 1
            value_count_tuples.add((value, count))

        sorted_by_count = sorted(value_count_tuples, key=lambda tup: tup[1], reverse=False)
        result = [value[0] for value in sorted_by_count]
        return result

    # checks whether a variable-value assignment is consistent with the current state
    def is_consistent(self, value, position, state):
        neighbours = self.constraints[position]
        return True
        for neighbour in neighbours:
            (row, col) = neighbour
            if state[row][col] == value:
                return False

    def forward_checking(self, deque, domains, removed=defaultdict(set)):
        #forward checking for all the tuples in the deque
        while deque:  
            (neighbour, position) = deque.popleft()
            i = next(iter(domains[position]))  
            if i in domains[neighbour]:
                domains[neighbour].remove(i)
                removed[neighbour].add(i)
        return domains

    def inference(self, domains, position, value, removed):
        neighbours = self.constraints[position]
        for neighbour in neighbours:
            if value in domains[neighbour]:
                domains[neighbour].remove(value)
                removed[neighbour].add(value)
                if not domains[neighbour]:
                    return []
        return domains    

    # initialize a deque which is arc consistent
    def initialize_arc_deque(self, assigned_positions, unassigned_positions):
        deque = collections.deque()
        for position in assigned_positions:
            neighbours = self.constraints[position]
            for neighbour in neighbours:
                if neighbour in unassigned_positions:
                    deque.append((neighbour, position))
        return deque
    
    #get the position tuple of the assigned and unassigned variables
    def get_assigned_unsigned_positions(self, state):
        assigned_positions = set()
        unassigned_positions = set()
        for row in range(9):
            for col in range(9):
                position = (row, col)
                value = state[row][col]
                if value != 0:
                    assigned_positions.add(position)
                else:
                    unassigned_positions.add(position)
        return assigned_positions, unassigned_positions

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
