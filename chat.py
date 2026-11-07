"""Command-line interface for MovieUp's RAG chatbot."""

import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
MOVIE_UP_DIR = PROJECT_ROOT / "movie_up"
sys.path.insert(0, str(MOVIE_UP_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from chatbot import services  # noqa: E402


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def ask_once(question: str) -> int:
    if not services.is_available():
        _print_json(
            {
                "error": "Chatbot is unavailable; configure GROQ_API_KEY and ingest the knowledge document."
            }
        )
        return 1
    try:
        answer = services.responder(question, history=[])
    except services.ChatbotUnavailable as exc:
        _print_json({"error": str(exc)})
        return 1
    _print_json({"answer": answer})
    return 0


def run_interactive() -> int:
    if not services.is_available():
        _print_json(
            {
                "error": "Chatbot is unavailable; configure GROQ_API_KEY and ingest the knowledge document."
            }
        )
        return 1

    history = []
    print("MovieUp RAG chat is ready. Type 'exit' to quit.")
    while True:
        try:
            question = input("You: ").strip()
        except EOFError:
            return 0
        if question.lower() in {"exit", "quit", "salir", "chau"}:
            return 0
        if not question:
            continue

        try:
            answer = services.responder(question, history=history[-10:])
        except services.ChatbotUnavailable as exc:
            print(f"Chatbot unavailable: {exc}")
            continue
        history.extend(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ]
        )
        print(f"MovieUp: {answer}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask MovieUp's RAG chatbot.")
    parser.add_argument(
        "--question",
        help="Ask one question and print a JSON result; omit for interactive mode.",
    )
    args = parser.parse_args()
    if args.question is not None:
        question = args.question.strip()
        if not question:
            _print_json({"error": "Question cannot be empty."})
            return 2
        return ask_once(question)
    return run_interactive()


if __name__ == "__main__":
    raise SystemExit(main())
