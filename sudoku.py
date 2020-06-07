# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class csp(object):
    def __init__(self,puzzle):
        self.variables = [] 
        self.adjencyList = {}
        self.domains = {}
        self.createInstance(puzzle)

    #Create a csp based on the variables, domains and constraints
    def createInstance(self, puzzle):
        self.initVariables()
        self.initDomains(puzzle)
        self.initAdjencyList(puzzle)
    
    #Convert list of lists into a 1D list
    def convertTo1D(self,puzzle):
        puzzle1D = []
        for i in range(9):
            for j in range(9):
                puzzle1D.append((i,j))
        return puzzle1D

    #Set the variables(coordinates) in the CSP
    def initVariables(self):
        for i in range(9):
            for j in range(9):
                self.variables.append((i,j))
    
    #Set the domain of each variable in the CSP
    def initDomains(self,puzzle):
        d = 0
        puzzle1D = self.convertTo1D(puzzle)
        for var in self.variables:
            # If original number is 0, set the domain of the variable to contain 1-9
            if puzzle1D[d] == 0:
                for num in range(1, 10):
                    self.domains[var].add(num)
            # If original number is NOT 0, set the domain of the variable to only contain that number
            else:
                self.domains[var].add(puzzle1D[d])
            d += 1
    
    #Set the adjency list (neighbours are variables which are affected by the same constraints) in the CSP
    def initAdjencyList(self, puzzle):
        #Remember that var is a pair of coordinates (x,y)
        for var in self.variables:
            for i in range(len(puzzle)):
                #Add neighbours based on row
                if (var[0], i) != var:
                    self.adjencyList[var].add((var[0], i))
                #Add neighbours based on col
                if (i, var[1]) != var:
                    self.adjencyList[var].add((i, var[1]))
                #Add neighbours based on 3x3 box (rowStart and colStart is the x and y coordinates of the specific box)
                rowStart = (var[0] // 3) * 3
                colStart = (var[1] // 3) * 3
                for i in range(rowStart, rowStart + 3):
                    for j in range(colStart, colStart + 3):
                        if (i, j) != var and (i, j) not in self.adjencyList[var]:
                            self.adjencyList[var].add((i, j))

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    def solve(self):
        return self.ans

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
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
