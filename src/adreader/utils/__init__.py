import os

RATIO = 0.5


def chown(path, id: int, gid: int):
    # Change permissions for the top-level folder
    os.chown(path, id, gid)

    for root, dirs, files in os.walk(path):
        # set perms on sub-directories
        for momo in dirs:
            os.chown(os.path.join(root, momo), id, gid)

        # set perms on files
        for momo in files:
            os.chown(os.path.join(root, momo), id, gid)


def ratio(*args):
    return [int(x * RATIO) for x in args]

