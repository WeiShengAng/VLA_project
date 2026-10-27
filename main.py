import queue
import threading

from SimEnv.MujocoEnv import MujocoEnv
from Parser.Parser import Parser
from Grounding.Grounding import Grounding
from Skill.Skill import Skill


def print_available_commands(env):
    # List the supported actions, using the colors actually present in the world.
    colors = sorted({obj["color"] for obj in env.get_objects() if obj.get("color")})
    options = "/".join(colors) if colors else "color"
    print("Available commands:")
    print(f"  pick [{options}]")
    print(f"  drop [{options}]")
    print(f"  swap [{options}] and [{options}]")
    print("  quit / exit")


def execute(command, grounding, skill):
    # Resolve the command's objects and run the matching skill.
    targets = grounding.TrackObject(command)
    action = command["action"]

    if action == "pick":
        if len(targets) == 1:
            skill.pick(targets[0])
        else:
            print("pick needs exactly one resolved object.")
    elif action == "drop":
        if len(targets) == 1:
            skill.drop(targets[0])
        else:
            print("drop needs exactly one resolved object.")
    elif action == "swap":
        if len(targets) == 2:
            skill.swap(targets[0], targets[1])
        else:
            print("swap needs exactly two resolved objects.")
    else:
        print(f"Action '{action}' is not supported yet.")


def input_reader(commands, stop):
    # Read user input in a background thread so the sim can keep stepping.
    # This thread never touches MuJoCo.
    while not stop.is_set():
        try:
            line = input("\ncommand> ")
        except EOFError:
            stop.set()
            break
        commands.put(line.strip())


def main():
    # Wire the pipeline: input -> parser -> grounding -> skill -> sim.
    env = MujocoEnv()
    skill = Skill(env)
    parser = Parser()
    grounding = Grounding()

    print_available_commands(env)

    commands = queue.Queue()
    stop = threading.Event()
    reader = threading.Thread(target=input_reader, args=(commands, stop), daemon=True)
    reader.start()

    # Main loop: step + render continuously on this thread; handle commands as
    # they arrive. Every MuJoCo call stays here; only input() runs in the reader.
    env.start_viewer()
    try:
        while env.viewer_running() and not stop.is_set():
            try:
                sentence = commands.get_nowait()
            except queue.Empty:
                sentence = None

            if sentence:
                if sentence.lower() in ("quit", "exit", "q"):
                    stop.set()
                    break
                command = parser.analyze_sentence(sentence)
                if command is not None:
                    # Parser already reports invalid input via ScreenOutput.
                    execute(command, grounding, skill)

            env.step()
            env.render()
    finally:
        env.close()


if __name__ == "__main__":
    main()
