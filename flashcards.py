"""A small persistent flashcard practice CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
from typing import Any

DEFAULT_DATA = Path.home() / ".flashcard-learning" / "cards.json"


def load_cards(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Cannot read card data at {path}: {exc}") from exc
    if not isinstance(data, list) or any(
        not isinstance(card, dict)
        or not isinstance(card.get("front"), str)
        or not isinstance(card.get("back"), str)
        or not isinstance(card.get("known"), bool)
        for card in data
    ):
        raise ValueError(f"Card data at {path} has an invalid format.")
    return data


def save_cards(path: Path, cards: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cards, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_card(path: Path, front: str, back: str) -> None:
    if not front.strip() or not back.strip():
        raise ValueError("Front and back must not be blank.")
    cards = load_cards(path)
    cards.append({"front": front.strip(), "back": back.strip(), "known": False})
    save_cards(path, cards)


def mark_known(path: Path, index: int) -> None:
    cards = load_cards(path)
    if index < 1 or index > len(cards):
        raise ValueError(f"Card number must be between 1 and {len(cards)}.")
    cards[index - 1]["known"] = True
    save_cards(path, cards)


def progress(path: Path) -> tuple[int, int]:
    cards = load_cards(path)
    return sum(card["known"] for card in cards), len(cards)


def study(path: Path, shuffle: bool = False) -> None:
    cards = load_cards(path)
    pending = [(index, card) for index, card in enumerate(cards, start=1) if not card["known"]]
    if shuffle:
        random.shuffle(pending)
    if not pending:
        print("No cards to study. Add cards or reset known cards in cards.json to practice again.")
        return
    print(f"Studying {len(pending)} card(s). Type 'q' to stop. Mark a card known after answering it.")
    for index, card in pending:
        print(f"\nCard {index}: {card['front']}")
        try:
            answer = input("Press Enter to reveal, or q to quit: ")
        except (EOFError, KeyboardInterrupt):
            print("\nStudy session ended.")
            return
        if answer.strip().lower() == "q":
            break
        print(f"Answer: {card['back']}")
        try:
            known = input("Mark known? [y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nStudy session ended.")
            return
        if known in {"y", "yes"}:
            mark_known(path, index)
            print("Marked known.")
    mastered, total = progress(path)
    print(f"Progress: {mastered}/{total} known.")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create and study a local flashcard deck.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help=f"card storage path (default: {DEFAULT_DATA})")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="add a new card")
    add.add_argument("front", help="question or prompt")
    add.add_argument("back", help="answer")
    commands.add_parser("study", help="study cards that are not yet known")
    commands.add_parser("progress", help="show mastered and total card counts")
    known = commands.add_parser("known", help="mark a card as known by its listed number")
    known.add_argument("number", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            add_card(args.data, args.front, args.back)
            print(f"Added card. Deck: {args.data}")
        elif args.command == "study":
            study(args.data)
        elif args.command == "progress":
            mastered, total = progress(args.data)
            print(f"Progress: {mastered}/{total} known ({total - mastered} to practice).")
        elif args.command == "known":
            mark_known(args.data, args.number)
            print(f"Marked card {args.number} known.")
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
