# What is this?

A very simple implementation of the game [Wordle](https://www.powerlanguage.co.uk/wordle/) in Python. This is not built for _playing_ Wordle. Rather, it is meant as a way to test automated Wordle solvers. The notebook `SolutionStrategies` illustrates a couple of basic examples.

To implement a new solver, inherit from the class `WordleSolver`. You need to provide `update` and a `guess` methods. The class `FilterWords` provides tools for filtering a corpus of words based on Wordle clues. My included word list consists of all five-letter words from https://github.com/dwyl/english-words/, but any other word list could be substituted.

The only dependencies are base Python 3, except for the Jupyter notebook examples.