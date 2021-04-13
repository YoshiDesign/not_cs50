import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # 
        if self.count and self.count == len(self.cells):
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0 and len(self.cells) > 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # Remove this cell and self.count -= 1
            self.count = self.count - 1
            self.cells =  {c for c in self.cells if c != cell}


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # Remove the safe cell. Do not update the count
            self.cells = {c for c in self.cells if c != cell}


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        # print(f"Marking Safe {cell}")
        
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)
        self.mark_safe(cell)

        # print(f"\nBEGIN MOVE: {cell} == {count}")
        new_k = set()

        # Selected cell's position
        row = cell[0]
        col = cell[1]

        # Generate the new knowledge set
        start_row = (row - 1) if row != 0 else 0
        while start_row <= row + 1 and start_row < self.height:
            # print(f"scan row -- {start_row}")
            start_col = (col - 1) if col != 0 else  0
            while start_col <= col + 1 and start_col < self.width:
                
                # print(f"[>>]({start_row}, {start_col})[<<]")

                # Skip any cells which have known states
                if \
                    (start_row, start_col) in self.mines or \
                    (start_row, start_col) in self.moves_made or \
                    (start_row, start_col) in self.safes:

                    # If we already know of a mine from this count
                    # ignore it and decrement the count
                    if (start_row, start_col) in self.mines:
                        count = count - 1
                        # print(f"[RemovingMineInfo] Count is now {count}")
                    else:
                        pass

                else:

                    # General assertion. All knowledge must fit this condition
                    if start_row >= 0 and start_row < self.height \
                    and start_col >= 0 and start_col < self.width:

                        # No need to add sentences with count == 0
                        if count == 0:
                            # Add safe cells
                            # print(f"[ZERO-COUNT] -- ALLES IS VIELIG {(start_row, start_col)}")
                            self.mark_safe((start_row, start_col))

                        else:
                            # Superflous assertion. Inverse of the first condition
                            if (start_row, start_col) not in self.moves_made or \
                            (start_row, start_col) not in self.safes or \
                            (start_row, start_col) not in self.mines:
                                new_k.add(tuple((start_row, start_col)))

                start_col += 1

            start_row += 1
        
        # Found mine(s)
        if len(new_k) == count and count:
            # print("[MINE--ALL--MINE]")
            for c in new_k:
                print(c)
                self.mark_mine(c)

        elif new_k:
            # Feed brain
            self.knowledge.append(Sentence(new_k, count))

        # Condense our knowledge and draw inferences
        self.recollect_knowledge()

        # print("\nKNOWLEDGE BASE:")
        for sent in self.knowledge:
            # Being memory friendly
            if not sent.cells:
                self.knowledge.remove(sent)
                continue

            try:
                # print(f"{sent.cells} = {sent.count}")
                for n in sent.known_safes():
                        # print(f"N - Marking Safe: {n}")
                    self.mark_safe(n)

                for n in sent.known_mines():
                        # print(f"MM - Marking Mine {n}")
                    self.mark_mine(n)

            except TypeError:
                pass

        # print("\nMINES:")
        # print(self.mines)

        # print("SAFES:")
        # print(self.safes)


    def recollect_knowledge(self):
        k_buffer = []
        updated = False

        # For every sentence, see if it contains a subset of another
        for i in range(len(self.knowledge)):

            cur_sentence = self.knowledge[i]

            # "Another"
            for j in range(len(self.knowledge)):

                # Don't compare a sentence to itself
                if j == i:
                    continue

                else:
                    # If cur_cells is a subset of [j]cells
                    if cur_sentence.cells < self.knowledge[j].cells \
                    and len(cur_sentence.cells):

                        # print("\nORIGINAL SET [J]")
                        # print(f"{self.knowledge[j].cells} ==== {self.knowledge[j].count}")
                        # print("\nCUR_SENTENCE [SUB]")
                        # print(f"{cur_sentence.cells} ==== {cur_sentence.count}")

                        # Difference of set from subset
                        new_set = self.knowledge[j].cells - cur_sentence.cells
                        # Difference in count
                        new_count = self.knowledge[j].count - cur_sentence.count

                        # print("\nNEW SET [x]")
                        # print(f"{new_set} ==== {new_count}")

                        self.knowledge[j].cells = new_set
                        self.knowledge[j].count = new_count


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        c_safes = self.safes.copy()
        debug_safes = {safe for safe in c_safes if safe not in self.moves_made}
        # print("UNUSED SAFES")
        # print(debug_safes)
        while len(c_safes) >= 1:
            mv = c_safes.pop()
            if mv in self.mines or \
            mv in self.moves_made:
                pass
            else:
                return mv

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        total_cells = self.height * self.width
        buffer = set()
        while len(buffer) <= total_cells:
            i = random.randint(0, self.height - 1)
            j = random.randint(0, self.width - 1)

            if tuple((i,j)) not in self.moves_made \
            and tuple((i,j)) not in self.mines:
                return tuple((i,j))

            else:
                buffer.add(tuple((i,j)))
                # No moves left to be made. Being explicit
                if len(buffer) == total_cells:
                    return None

        return None