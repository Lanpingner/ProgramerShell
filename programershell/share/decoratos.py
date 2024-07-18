# List to store functions
registered_functions = []

def register_function(cat, ins, method):
    registered_functions.append((cat, ins, method))

def call_registered_functions(cat):
    for cat, ins, method in registered_functions:
        if cat == cat:
            method()
