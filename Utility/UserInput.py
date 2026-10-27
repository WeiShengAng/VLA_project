
class UserInput:
    # Parser class for reading sentence input and storing it in a list

    def __init__(self):
        self.sentences = []

    def read_input(self):
        # Read user input and break on enter
        line = input().strip()
        if line:
            self.sentences = line

    def get_sentences(self) -> str:
        # Getter to retrieve the list of sentences
        return self.sentences
    
    def print_sentences(self):
        # Utility method to print the stored sentences
        print(self.sentences)