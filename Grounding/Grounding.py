from SimEnv.ObjectFactory import factory

class Grounding:
    # Resolve symbolic references (color tokens) to concrete world-model objects.

    def __init__(self):
        self.CmdDict = {}
        self.targets = []

    # Resolve each object token in the parsed command to a world-model object.
    # Returns the list of resolved object records; a token with no match is
    # reported and skipped so the caller can decide how to handle a miss.
    def TrackObject(self, inputDict: dict) -> list:
        self.CmdDict = inputDict or {}
        colors = self.CmdDict.get("objects") or []

        resolved = []
        for color in colors:
            target = factory.get_object_by_color(color)
            if target is None:
                print(f"Grounding: no object found for '{color}'")
            else:
                resolved.append(target)

        self.targets = resolved
        return resolved
