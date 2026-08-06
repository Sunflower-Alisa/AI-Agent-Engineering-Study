
class ShortMemory():

    def __init__(self):
        self.short_term = []

    def save(self,data):
        self.short_term.append(data)

    def retrieve(self):
        return self.short_term[-5:]