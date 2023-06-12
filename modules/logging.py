import os


class logger:
    path = ""

    def __init__(self):
        self.path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(self.path):
            os.mkdir(self.path)
