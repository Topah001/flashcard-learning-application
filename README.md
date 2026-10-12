# Flashcard Learning Application

A small Python 3.13-compatible command-line flashcard app. Cards and known/unknown progress are stored as JSON locally (by default in `~/.flashcard-learning/cards.json`). No third-party packages are required.

## Use

```text
python flashcards.py add "What is a closure?" "A function with access to its lexical scope."
python flashcards.py progress
python flashcards.py study
python flashcards.py known 1
```

Use `--data PATH` before the command to choose a deck, for example `python flashcards.py --data deck.json add "Question" "Answer"`. Card numbers are one-based. `study` reveals each unmastered answer after Enter and lets you mark it known with `y`.

## Tests

```text
python -m unittest discover -s tests -v
```

Tests use temporary directories and never access the default user deck.
