# from shared.frame_stack
# frame.py

class Frame:

    def __init__(self):
        self.c = set()
        self.v = set()
        self.d = set()
        self.f = []
        self.f_labels = {}
        self.e = []
        self.e_labels = {}
        self.e_statements = []
        self.type_code_by_var = {}
