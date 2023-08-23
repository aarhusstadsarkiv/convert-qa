import re
from argparse import ArgumentParser
from pathlib import Path
from shutil import get_terminal_size
from zipfile import ZipFile


# noinspection SpellCheckingInspection
def main(files: list[Path], ignore: str):
    """
    Take a list of Open Document files and check the text inside the content.xml file for unusual character sequences.

    The characters are searched within tags, they must be surrounded by ASCII characters
    and not included in the optional `ignore` argument.
    """

    # Compile the expressions for the general match and to capture the specific characters
    expression = re.compile(fr"(?<=>)[^<>]*(\w+[^\x20-\x7e{ignore}]+\w+)[^<>]*(?=<)")
    expression_single = re.compile(fr"(?<=\w)([^\x20-\x7e{ignore}]+)(?=\w)")
    terminal_size = get_terminal_size((0, 0)).columns
    file: Path

    for i, file in enumerate(files, 1):
        # Ensure that the file has an Open Document extension
        if file.suffix not in (".odt", ".ods", ".odp"):
            raise Exception(f"File {file!r} is not an Open Document file")

        # Print the file path and a horizontal line
        #   with minimum length equal to the table header but smaller than the terminal width
        print(file)
        hr = min(len(str(file)), terminal_size)
        hr = max(hr, 9 + 3 + 9 + 3 + 5)
        print("-" * hr)

        # Open file as zip and extract text from content.xml file inside it
        file_zip = ZipFile(file, "r")
        text = file_zip.open("content.xml", "r").read().decode()

        # Match the expression for unusual characters
        matches = list(expression.finditer(text))

        if not matches:
            print("No errors found in file.")
        else:
            print(f"{'Start':<9} | {'End':<9} | Match")

        for match in matches:
            # Highlight the unusual characters with bold (1), red (31) text.
            match_highlight = expression_single.sub("\x1b[31;1m" + r"\1" + "\x1b[0m", match.group(0))

            # Print the start and end of the match and the highlighted match within the terminal width.
            print(f"{match.span()[0]:<9} | {match.span()[1]:<9} | {match_highlight} "[:terminal_size or -1])

        # Print an extra newline if the file is not the last
        if i < len(files):
            print()


def cli():
    parser = ArgumentParser("convert-encoding", description=main.__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="the files to check")
    parser.add_argument("--ignore", type=str, required=False, default="", help="extra characters to ignore")

    args = parser.parse_args()

    main(args.files, args.ignore)

