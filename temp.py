import sys
import os

def custom_print(*args, mode="default", **kwargs):
    if mode == "file":
        with open("logs.txt", "a") as f:
            print(*args, file=f, **kwargs)
    elif mode == "suppress":
        pass
    else:
        print(*args, **kwargs)

# Example usage
custom_print("This will be printed normally.")
custom_print("This will be written to logs.txt", mode="file")
custom_print("This will not be printed", mode="suppress")