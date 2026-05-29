from __future__ import annotations

import argparse

import startup


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage Julian Today login startup.")
    parser.add_argument(
        "action",
        choices=("add", "remove", "status"),
        nargs="?",
        default="add",
        help="Startup action to perform. Defaults to add.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.action == "add":
        path = startup.add_to_startup()
        print(f"Added startup entry: {path}")
        return

    if args.action == "remove":
        path = startup.remove_from_startup()
        print(f"Removed startup entry: {path}")
        return

    state = "enabled" if startup.is_startup_enabled() else "disabled"
    print(f"Startup is {state}.")


if __name__ == "__main__":
    main()
