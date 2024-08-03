import inspect
import datetime

registered_functions = []


def register_function(cat, method):
    print(f"[{cat}] ", method, "subscribed")
    registered_functions.append((cat, method))


def call_registered_functions(icat, data=None):
    for cat, method in registered_functions:
        if callable(method):
            if icat == cat:
                print(
                    f"{datetime.datetime.now()} ", "[{:<10}] calling update".format(cat)
                )
                if data is None:
                    method()
                else:
                    # print("with args, data:", data)
                    # print(inspect.signature(method))
                    method(data)
