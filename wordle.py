from collections import Counter
from math import log2 as log
from random import choice

# Define a global corpus for consistency.
corpus = [l.rstrip() for l in open('five_letter.txt').readlines()]

class Wordle:

    def __init__(self, soln, verbose=False) -> None:
        self.soln = soln 
        self.row = 0
        self.solved = False
        self.clues = []
        self.guesses = []
        self.verbose = verbose

    def make_guess(self, guess):
        if len(guess) != 5:
            print(f'Guess "{guess}" is not a five-letter word!')
            return None
        if guess in corpus:
            self.row += 1
            self.guesses.append(guess)
            clue = self.get_clue(guess)
            self.clues.append(clue)
            if sum(clue) == 5:
                self.solved = True
                if self.verbose:
                    print(f'Correct! Puzzle completed in {self.row} guesses.')
            return clue
        else:
            print(f'Guess \"{guess}\" not an allowed word!')
            return None
        
    def get_clue(self, guess):
        clue = 5*[0]
        letters = [l for l in self.soln]
        # Match letters in exact position.
        for i in range(5):
            if guess[i] == self.soln[i]:
                clue[i] = 1
                letters.remove(guess[i])
        # Match letters in wrong position.
        for i in range(5):
            if guess[i] in letters and guess[i] != self.soln[i]:
                clue[i] = -1
                letters.remove(guess[i])
        return clue

    def autoplay(self, solver):
        while not self.solved:
            guess = solver.guess()
            clue = self.make_guess(guess)
            solver.update(clue, guess)
            if self.row > 1000:
                print(f"Guessing timed out.")
                break
        if self.verbose:
            print(f"Guesses: {self.guesses}")
            print(f"Clues: {self.clues}")
        return self.row

class FilterWords:

    def __init__(self) -> None:
        self.words = corpus
        self.counts = self.get_letter_counts()
        self.positional_counts = self.get_positional_letter_counts()
        self.n_words = len(self.words)

    def filter(self, clue, guess):
        tried = []
        for i in range(5):
            if clue[i] == 1:
                self.words = list(filter(lambda x : x[i] == guess[i],
                                        self.words))
                tried.append(guess[i])
            elif clue[i] == -1:
                self.words = list(filter(lambda x : x[i] != guess[i]
                    and guess[i] in x, self.words))
                tried.append(guess[i])
        # Do a separate removal loop in case of duplicate letters.
        for i in range(5):
            if clue[i] == 0 and guess[i] in tried:
                self.words = list(filter(lambda x : x[i] != guess[i],
                    self.words))
            if clue[i] == 0 and not guess[i] in tried:
                self.words = list(filter(lambda x : guess[i] not in x,
                                        self.words))
        return len(self.words)

    def recount(self):
        self.counts = self.get_letter_counts()
        self.positional_counts = self.get_positional_letter_counts()
        self.n_words = len(self.words)
        return None

    def filter_recount(self, clue, guess):
        n = self.filter(clue, guess)
        self.recount()
        return n

    def get_letter_counts(self):
        c = Counter(''.join(self.words))
        return c

    def get_positional_letter_counts(self):
        cs = [Counter(''.join([w[i] for w in self.words])) for i in range(5)]
        return cs




class WordleSolver:
    """Base class for wordle solvers."""

    def __init__(self) -> None:
        self.word_list = FilterWords()

    def guess(self):
        pass

    def update(self, clue, guess):
        pass


class RandomSolver(WordleSolver):
    """Solve by randomly guessing from valid word list."""
    def guess(self):
        return choice(self.word_list.words)

    def update(self, clue, guess):
        _ = self.word_list.filter(clue, guess)


class MaxLikelihoodSolver(WordleSolver):
    """Guess the most probable valid word."""

    def guess(self):
        """Word with maximum probability by letter counts."""
        return max(self.word_list.words, key=self.word_probability)

    def update(self, clue, guess):
        _ = self.word_list.filter(clue, guess)

    def word_probability(self, w): 
        c = self.word_list.counts
        p = 1
        for i in w:
            p *= c[i]/(5 * self.word_list.n_words)
        return p


class MaxEntropySolver(WordleSolver):
    """Guess the maximum entropy valid word.
    
    The current implementation is dumb and does essentially the same thing as
    `MaxLikelihoodSolver`.
    """

    def guess(self):
        return max(self.word_list.words, key=self.word_entropy)

    def update(self, clue, guess):
        _ = self.word_list.filter(clue, guess)

    def word_entropy(self, w):
        c = self.word_list.counts
        H = 0
        for i in w:
            p = c[i] / (5 * self.word_list.n_words)
            H -= p * log(p)
        return H