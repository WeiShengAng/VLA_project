"""Download the official Franka Emika Panda robot description.

These files come from Google DeepMind's MuJoCo Menagerie and are gitignored in
this project (they are large and we don't want to vendor them). Run this script
once after cloning to pull the `franka_emika_panda/` folder into `SimEnv/`.

Usage:
    python SimEnv/fetch_robot_assets.py          # download if missing
    python SimEnv/fetch_robot_assets.py --force  # re-download, overwriting

Requires `git` on PATH. A sparse checkout is used so only the Panda folder is
fetched, not the whole Menagerie repo.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

REPO = "https://github.com/google-deepmind/mujoco_menagerie.git"
SUBDIR = "franka_emika_panda"

# Install target: SimEnv/franka_emika_panda (next to this script).
TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), SUBDIR)


def _run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="re-download even if the folder already exists")
    args = parser.parse_args()

    if os.path.isdir(TARGET) and os.listdir(TARGET) and not args.force:
        print(f"[skip] {TARGET} already exists (use --force to re-download).")
        return 0

    if shutil.which("git") is None:
        print("[error] git is required but was not found on PATH.", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        clone = os.path.join(tmp, "menagerie")
        print(f"[1/3] Cloning {SUBDIR} from MuJoCo Menagerie (sparse)...")
        _run(["git", "clone", "--depth", "1", "--filter=blob:none",
              "--sparse", REPO, clone])
        _run(["git", "sparse-checkout", "set", SUBDIR], cwd=clone)

        src = os.path.join(clone, SUBDIR)
        if not os.path.isdir(src):
            print(f"[error] '{SUBDIR}' not found in the repo.", file=sys.stderr)
            return 1

        print(f"[2/3] Installing into {TARGET} ...")
        if os.path.isdir(TARGET):
            shutil.rmtree(TARGET)
        shutil.copytree(src, TARGET)

    print("[3/3] Done. Robot assets are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
