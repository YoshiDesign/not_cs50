import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for var in self.domains:
            remove = set()

            for word in self.domains[var]:
                if len(word) != var.length:
                    remove.add(word)
                # else:
                #     print(f"Keeping {word}")

            self.domains[var] = self.domains[var] - remove


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        remove = set()
        # x and y are neighbors
        for word in self.domains[x]:
            satisfied = 0
            for other_word in self.domains[y]:

                # Enforcing word uniqueness. Will reimplement in consistent
                if word == other_word:
                    continue

                # print(f"comparing: {word} -- {other_word}")
                # print(f"x: Direction({x.direction})\tLength({x.length})\tBegins({x.i},{x.j}))")
                # print(f"y: Direction({y.direction})\tLength({y.length})\tBegins({y.i},{y.j}))")

                # Determine each index for x and y where the letters must match
                if x.i == y.i and x.j == y.j:
                    overlap_y = 0
                    overlap_x = 0 

                # The Dutch way. I forgot to punt to crossword.overlaps...

                elif x.direction == Variable.DOWN:
                    overlap_y = x.j - y.j
                    overlap_x = y.i - x.i
                    
                elif x.direction == Variable.ACROSS:
                    overlap_y = x.i - y.i
                    overlap_x = y.j - x.j

                # print(f"OverlapX: {overlap_x}")
                # print(f"OverlapY: {overlap_y}")
                # print(f"word[overlap_x] = {word[overlap_x]}\nother_word[overlap_y] = {other_word[overlap_y]}")
                # print("-----------------------")

                # exit()

                if word[overlap_x] == other_word[overlap_y]:
                    satisfied = 1

            if not satisfied:
                remove.add(word)
                revised = True
        
        # print(f"CHECKING\tLen DomX = {len(self.domains[x])}\tLen Remove = {len(remove)}.\tDiff = {int(len(self.domains[x]) - len(remove))}")
        if revised:
            self.domains[x] = self.domains[x] - remove
        # print(f"POST: {len(self.domains[x])}")
        # print(f"Revised: {revised}")
        # exit()
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # print(self.domains)
        if arcs == None:
            queue = self.makeQueue()
        else:
            queue = arcs

        # print(f"Queue:", end="")
        # print(queue)
        while queue:
            # For every pair in our queue, revise their potential words
            n = queue.pop(0)
            # print(f"Popped: {n}")
            if self.revise(n[0], n[1]):
                # print(f"Revised: {self.domains[n[0]]}")
                # No possible solution. This variable cannot satisfy constraints
                if len(self.domains[n[0]]) == 0:
                    return False

                # Since we've revised the domain of n[0] - (X) - in terms of n[1] - Y -
                # we'll need to now look at X's neighbors - (Z) - in terms of X,
                # as the previous potential for acquiring matches has decreased
                for z in self.crossword.neighbors(n[0]):
                    # Skip the variable we already evaluated with
                    if z == n[1]:
                        continue
                    queue.append((z, n[0]))

        # print("Finished!")
        # for d in self.domains:
        #     print(f"{d}\t{self.domains[d]}")

        return True


    def makeQueue(self):
        """
        Enqueue every possible set of neighboring words as tuples
        """
        queue = []
        for x in self.domains:
            for y in self.crossword.neighbors(x):
                # print(f"X: {x}\t Neighbor: {y}")
                queue.append((x,y))
        return queue


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # print(f"Len Assignment Domains: {len(assignment)}\nLen Domain Keys: {len(self.domains.keys())}")
        if len(assignment) == len(self.domains.keys()):
            return True

        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Enforce arc consistency across the assignments
        for k, v in assignment.items():
            for i, j in assignment.items():
                if k == i:
                    continue
                # Compare v and j for arc-consistency
                ovr = self.crossword.overlaps[k, i]

                # Doesn't have a neighbor identified yet.
                # We're in favor of adding it to the assignment.
                # If it doesn't work, it'll be removed
                if ovr == None:
                    continue
                # print(f"ovr = {ovr}")
                # print(f"v = {v}\tj = {j}")
                if v[ovr[0]] != j[ovr[1]]:
                    return False

        return  True
        # for var in assignment:
            

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # print(f"Assignment: {assignment}")
        if var in assignment:
            return []
        else:
            result = dict()
            # Find out which domain value leaves us with the most potential options for the next assignment
            neighbors = self.crossword.neighbors(var)
            for word in self.domains[var]:
                result[word] = 0
                for n in neighbors:
                    for w in self.domains[n]:
                        ovr = self.crossword.overlaps[var, n]
                        # print(f"Vars: \t{var}\t{n}")
                        # print(f"Overlap of {word} -_X_- {w}:")
                        # print(str(overlap[0]) + "--" + str(overlap[1]))
                        if word[ovr[0]] == w[ovr[1]]:
                            pass
                        else:
                            result[word] += 1
            sList = []
            for k, v in sorted(result.items(), key=lambda item: item[1]):
                sList.append(k)
            
            return sList
                

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        smallest = None
        for var in self.domains:
            if var not in assignment:

                # Next assignment will have the smallest domain
                if smallest == None or len(self.domains[var]) < smallest:
                    next_assignment = var
                    smallest = len(self.domains[var])
                
                # Or the next assignment will have the highest degree
                if len(self.domains[var]) == smallest \
                and var != next_assignment:

                    if len(self.crossword.neighbors(next_assignment)) \
                    < len(self.crossword.neighbors(var)):
                        pass
                    else:
                        # var has more neighbors than our previous best choice
                        next_assignment = var

        return next_assignment
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for v in self.order_domain_values(var, assignment):
            
            assignment[var] = v

            if self.consistent(assignment):
                assignment = assignment
                # print(f"Next: {assignment}")
                result = self.backtrack(assignment)
                if result:
                    return result
            else:
                del assignment[var]

        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
