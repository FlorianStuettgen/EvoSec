"""Backward-compatible entry point for the renamed deterministic bundle verifier."""

from verify_deterministic_bundles import main


if __name__ == "__main__":
    raise SystemExit(main())
