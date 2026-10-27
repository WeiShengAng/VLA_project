# VLA Project

A simple language → grounding → skill pipeline driving a simulated Franka Emika
Panda arm (MuJoCo, with a PyBullet alternative).

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Download the robot description (required)

The official **Franka Emika Panda** model lives in `SimEnv/franka_emika_panda/`.
These files come from [Google DeepMind's MuJoCo Menagerie][menagerie] and are
**gitignored** (they are large and we don't vendor third-party assets), so a
fresh clone won't have them. Fetch them with:

```bash
python SimEnv/fetch_robot_assets.py
```

This does a sparse `git` checkout of just the `franka_emika_panda/` folder from
the Menagerie repo. Pass `--force` to re-download. (Requires `git` on PATH.)

> The custom simulation scene, `SimEnv/scenes/vla_scene.xml`, **is** tracked in
> this repo. It `include`s the official `panda.xml` via a relative path, so the
> step above must be run first or MuJoCo will fail to load the scene.

[menagerie]: https://github.com/google-deepmind/mujoco_menagerie/tree/main/franka_emika_panda

## Running

```bash
python main.py
```

## Tests

Unit tests live in `UnitTest/` (gitignored — kept local) and run with:

```bash
python -m pytest UnitTest/
```

## Layout

| Path                         | Purpose                                            |
| ---------------------------- | -------------------------------------------------- |
| `Parser/`                    | Parses natural-language commands                   |
| `Grounding/`                 | Resolves referenced objects in the world model     |
| `Skill/`                     | Executes skills (pick, swap, ...)                  |
| `SimEnv/`                    | Simulation environments (MuJoCo / PyBullet)        |
| `SimEnv/scenes/`             | Custom MJCF scenes (tracked)                        |
| `SimEnv/franka_emika_panda/` | Official robot model (gitignored — fetch it)        |
