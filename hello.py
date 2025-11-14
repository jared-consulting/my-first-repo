import sys
import traceback


def main() -> None:
 print("Hello from WSL!")


if __name__ == "__main__":
 try:
  main()
 except Exception:
  traceback.print_exc(file=sys.stderr)
  sys.exit(1)
