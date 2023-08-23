import argparse
from glob import glob
import os
import shutil
import sqlite3
import traceback
from typing import Union
from pathlib import Path
from dataclasses import dataclass

DRY = False

parser = argparse.ArgumentParser(
    description="Easily compare files between original, master and statutory"
)
parser.add_argument(
    "--original",
    help="directory pointing to original documents containing the metadata folder",
)
parser.add_argument("--master", help="directory pointing to master documents")
parser.add_argument(
    "--statutory",
    default="",
    help="(optional) directory pointing to statutory documents",
)

parser.add_argument(
    "--output",
    default="./comparison_output",
    help="directory to output files into",
)
parser.add_argument(
    "--digiarch", action="store_true", help="generate metadata folder with digiarch"
)
# parser.add_argument("--silent", action="store_true", help="only print errors")


@dataclass
class PUIDFolder:
    """
    Represents data for a single puid
    """

    puid: str
    smallest: str
    biggest: str
    smallest_doc_path: Union[str, Path] = ""
    biggest_doc_path: Union[str, Path] = ""


class PUIDFolders:
    def __init__(self, path: str) -> None:
        self.path = path

        self._puids: list[PUIDFolder] = []

        # check if files db exists
        self.db_path = os.path.join(path, "_metadata", "files.db")
        if not os.path.exists(self.db_path):
            raise SystemExit(f"ERROR: Could not find db file at '{self.db_path}'")

    def collect(self) -> list[PUIDFolder]:
        """
        Collects information about smallest and biggest files for each PUID in the given files db
        """
        if self._puids:
            return self._puids

        print(f"Collecting puid data from {self.path}")
        # conn: sqlite3.Connection = None
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            stmts = [
                "SELECT id, relative_path, puid, min(file_size_in_bytes) FROM Files WHERE is_binary=1 GROUP BY puid",
                "SELECT id, relative_path, puid, max(file_size_in_bytes) FROM Files WHERE is_binary=1 GROUP BY puid",
            ]

            results = []
            for s in stmts:
                cur.execute(s)
                results.append(cur.fetchall())

            for (id_min, path_min, puid_min, size_min), (
                id_max,
                path_max,
                puid_max,
                size_max,
            ) in zip(*results):
                if not puid_min:
                    continue
                p = PUIDFolder(
                    puid_min, path_min, "" if path_max == path_min else path_max
                )
                p.smallest_doc_path = Path(p.smallest).parent
                p.smallest = os.path.join(self.path, p.smallest)
                p.biggest_doc_path = Path(p.biggest).parent
                p.biggest = os.path.join(self.path, p.biggest) if p.biggest else ""
                self._puids.append(p)

        except Exception:
            traceback.print_exc()
            raise SystemExit(f"ERROR: above error occurred in {self.path}")

        finally:
            if conn:
                conn.close()

        return self._puids


def output_files(root: str, folders: list[PUIDFolder], others: dict[str, str]):
    """
    Copy over the files per PUID folder
    """
    os.makedirs(root, exist_ok=True)

    errs = []  # error messages

    print("Found", len(folders), "PUIDs to copy files for")

    for p in folders:
        print("Copying files for PUID", p.puid)
        for n, (file_path, doc_path) in enumerate(
            ((p.smallest, p.smallest_doc_path), (p.biggest, p.biggest_doc_path))
        ):
            if not file_path:
                continue
            if not os.path.exists(file_path):
                errs.append(
                    f"Expected file for PUID {p.puid} in original to exist: {file_path}"
                )
                continue
            doc_id = Path(doc_path).name
            doc_id_path = os.path.join(root, p.puid.replace("/", "_"), doc_id)
            os.makedirs(doc_id_path, exist_ok=True)

            name = "smallest" if n == 0 else "biggest"
            shutil.copy2(
                file_path,
                os.path.join(doc_id_path, f"original_{name}{Path(file_path).suffix}"),
            )

            # look in others
            for other_name, other_path in others.items():
                if not other_path:
                    continue
                other_files = glob(os.path.join(other_path, doc_path, "*"))
                for f in other_files:
                    shutil.copy2(
                        f, os.path.join(doc_id_path, f"{other_name}{Path(f).suffix}")
                    )

                if not other_files:
                    errs.append(
                        f"Could not find file for PUID {p.puid} in {other_name}, PUID file in question: {file_path}"
                    )

    if errs:
        print("A few errors occured while copying:")
        for e in errs:
            print("- " + e)


def main():
    # global log
    args = parser.parse_args()

    # if args.silent:
    #     log = lambda *a, **kw: None

    paths = [
        ("master", args.master),
        ("original", args.original),
        ("statutory", args.statutory),
    ]
    # ensure paths are directories
    for a, d in paths:
        if a == "statutory" and not d:
            continue
        if not d or not os.path.isdir(d):
            raise SystemExit(f"ERROR: expected a valid directory for '--{a}'")

    # run digiarch if necessary
    if args.digiarch:
        os.system(f'digiarch "{args.original}" process')

    # collect the data for each puid
    print("Collecting info on all files")
    puidfolders = PUIDFolders(args.original)
    puids = puidfolders.collect()
    print("Copying files to puid-folders")
    output_files(
        args.output, puids, {"master": args.master, "statutory": args.statutory}
    )

    print("Finished!")


if __name__ == "__main__":
    main()
