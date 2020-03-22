"""
Solve Sudoku puzzles by backtracking.
"""
from argparse import ArgumentParser


def parse_input(fp):
    """
    Here we use the following format to store Sudoku puzzles:
    one_sudoku = name_line, 9 * grid_line;
    name_line = name_string, "\n";
    name_string = (printable_char | " "), { (printable_char | " ") };
    grid_line = 9 * decimal_digit, "\n";
    decimal_digit = "0", "1", ..., "9";
    """
    sudoku_collection = []
    while True:
        line = fp.readline()
        if not line:
            break
        name = line.strip()
        grid = []
        for n in range(9):
            grid.append(_verify_grid(fp.readline().strip()))
        sudoku_collection.append(Sudoku(name, ''.join(grid)))
    return sudoku_collection


class Sudoku:
    def __init__(self, name, encoded_grid):
        self.name = name
        self.puzzle = _verify_grid(encoded_grid)

    def __repr__(self):
        return 'Sudoku({!r}, {!r})'.format(self.name, self.puzzle)


def solve(puzzle):
    row_chances, column_chances, box_chances = _all_chances()
    unsolved_fields = _all_unsolved()
    solved = _init_fields(puzzle, row_chances, column_chances, box_chances, unsolved_fields)
    if not _solve(row_chances, column_chances, box_chances, unsolved_fields, solved):
        raise ValueError('Puzzle is not solvable:\n{}'.format(puzzle))
    return ''.join(map(str, solved))


def _verify_grid(encoded_grid: str) -> str:
    for c in encoded_grid:
        if c not in '0123456789':
            raise ValueError('Grid lines may only contain decimal digits.')
    return encoded_grid


def _positions(field):
    """Given an index into the puzzle (i.e. a single field, calculate and return
    a 3-tuple (row, column, box) of the units the field belongs to.
    """
    row = field // 9
    column = field % 9
    box = (field // 3) % 3 + 3 * ((field // 9) // 3)
    return row, column, box


def _all_chances():
    row_chances = []
    column_chances = []
    box_chances = []
    all_chances = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for _ in range(9):
        row_chances.append(set(all_chances))
        column_chances.append(set(all_chances))
        box_chances.append(set(all_chances))
    return row_chances, column_chances, box_chances


def _all_unsolved():
    unsolved_fields = set()
    for f in range(81):
        unsolved_fields.add(_positions(f))
    return unsolved_fields


def _init_fields(puzzle, row_chances, column_chances, box_chances, unsolved_fields):
    solution = [0] * 81
    for field, digit in enumerate(puzzle):
        if digit not in '.0':
            _set_field(
                (row_chances, column_chances, box_chances),
                unsolved_fields,
                solution,
                _positions(field),
                int(digit)
            )
    return solution


def _set_field(chances, unresolved_fields, solution, positions, digit):
    row_chances, column_chances, box_chances = chances
    row, column, box = positions
    row_chances[row].remove(digit)
    column_chances[column].remove(digit)
    box_chances[box].remove(digit)
    unresolved_fields.remove(positions)
    solution[row * 9 + column] = digit


def _reset_field(chances, unresolved_fields, solution, positions, digit):
    row_chances, column_chances, box_chances = chances
    row, column, box = positions
    row_chances[row].add(digit)
    column_chances[column].add(digit)
    box_chances[box].add(digit)
    unresolved_fields.add(positions)
    solution[row * 9 + column] = 0


def _choose_next_unsolved(row_chances, column_chances, box_chances, unsolved_fields):
    best_field = None
    least_candidates_so_far = 9
    for row, column, box in unsolved_fields:
        candidates = row_chances[row] & column_chances[column] & box_chances[box]
        if len(candidates) < 2:
            return (row, column, box), list(candidates)
        if len(candidates) < least_candidates_so_far:
            least_candidates_so_far = len(candidates)
            best_field = ((row, column, box), list(candidates))
    return best_field


def _solve(row_chances, column_chances, box_chances, unsolved_fields, solution):
    if len(unsolved_fields) == 0:
        return True
    positions, candidates = _choose_next_unsolved(
        row_chances, column_chances, box_chances, unsolved_fields)
    for candidate in candidates:
        _set_field(
            (row_chances, column_chances, box_chances),
            unsolved_fields,
            solution,
            positions,
            candidate
        )
        if _solve(row_chances, column_chances, box_chances, unsolved_fields, solution):
            return True
        _reset_field(
            (row_chances, column_chances, box_chances),
            unsolved_fields,
            solution,
            positions,
            candidate
        )
    return False


def nice(puzzle):
    lines = list()
    for n in range(0, len(puzzle), 9):
        lines.append(puzzle[n:n + 9])
    return '\n'.join(lines)


def main():
    parser = ArgumentParser(description='Solve Sudoku puzzles from the input file.')
    placeholder = 'puzzle_input'
    puzzles = 'puzzles'
    help_text = 'A file with a sequence of Sudoku puzzles'
    parser.add_argument(placeholder, metavar=puzzles, type=str, nargs=1, help=help_text)
    with open(parser.parse_args().puzzle_input.pop()) as fp:
        sudoku_collection = parse_input(fp)
        for sudoku in sudoku_collection:
            solved_puzzle = solve(sudoku.puzzle)
            print(sudoku.name + '\n' + nice(solved_puzzle))


if __name__ == '__main__':
    main()

# last line of code
