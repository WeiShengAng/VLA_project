import Utility.ScreenOutput as ScreenOutput

class Parser:
    # Rule-based parser (the current "planner").
    # Extracts a single action plus its object(s) from a sentence.

    def __init__(self):
        self.actions = ['move', 'pick', 'drop', 'place', 'put', 'grab', 'swap']
        self.screen = ScreenOutput.ScreenOutput()

    def analyze_sentence(self, sentence: str) -> dict:
        # Analyze a sentence to extract {action, objects}.
        # objects is always a list, so the schema is consistent across
        # single-object actions (pick) and two-object actions (swap).

        words = sentence.lower().split()

        action = None
        for word in words:
            if word in self.actions:
                action = word
                break

        if action is None:
            self.screen.WrongInput()
            return None

        idx = words.index(action)
        # Everything after the action is an object token, except the
        # connector "and" used by the two-object swap form.
        objects = [w for w in words[idx + 1:] if w != 'and']

        # Arity check: swap needs two objects, every other action needs one.
        expected = 2 if action == 'swap' else 1
        if len(objects) != expected:
            self.screen.WrongInput()
            return None

        return {'action': action, 'objects': objects}
