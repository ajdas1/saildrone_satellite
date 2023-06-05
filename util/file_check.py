import os

def check_for_product(
        datadir: str = "/Users/asavarin/Desktop/work/saildrone_satellite/data/",
        format: str = ".nc",
        ) -> list[str]:

    """
    files = check_for_product(datadir: str)

    Arguments:
    - datadir: directory where data files are located
    - format: what format should be looked for

    Returns:
    - files: list of files in directory with provided format
    """

    if os.path.isdir(datadir):
        files = sorted([fl for fl in os.listdir(datadir) if format in fl])
        return files
    else:
        print(f"The provided data directory does not exist.")
