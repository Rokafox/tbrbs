
def fine_print(*args, mode="default", **kwargs):
    if mode == "file":
        with open("logs.txt", "a") as f:
            print(*args, file=f, **kwargs)
    elif mode == "suppress":
        pass
    else:
        print(*args, **kwargs)
