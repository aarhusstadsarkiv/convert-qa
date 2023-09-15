from argparse import ArgumentParser
from functools import reduce
from pathlib import Path
from typing import Optional

from xmltodict import parse as parse_xml

from ..clean_empty_columns.main import print_with_file
from ..clean_empty_columns.main import rmdir
from ..clean_empty_columns.main import table_index_update
from ..clean_empty_columns.main import table_xml_update
from ..clean_empty_columns.main import table_xsd_update


# noinspection DuplicatedCode
def main(archive: Path, table_names: list[str], log_file: Optional[Path]):
    echo = print_with_file(log_file)

    table_names = list(map(str.lower, table_names))

    tables_index_path: Path = archive.joinpath("Indices", "tableIndex.xml")
    tables_index: dict = parse_xml(tables_index_path.read_text())

    tables: list[dict] = tables_index["siardDiark"]["tables"]["table"]
    tables_to_remove: list[int] = []

    for table_name in table_names:
        table = next((t for t in tables if t["name"].lower() == table_name), None)

        if not table:
            echo(f"{archive.name}/-------/{table_name}/not found")
            continue

        echo(f"{archive.name}/{table['folder']}/{table['name']}/removed")
        index: int = int(table["folder"].removeprefix("table"))
        rmdir(archive.joinpath("tables", table["folder"]))
        tables_to_remove.append(index)

    table_index_update(tables_index_path, [], tables_to_remove, tables_index_path)

    for table in tables:
        index = int(table["folder"].removeprefix("table"))
        if index <= min(tables_to_remove):
            continue
        index_diff: int = reduce(lambda p, c: (p + 1) if c < index else p, tables_to_remove, 0)
        new_index: int = index - index_diff
        echo(f"{archive.name}/{table['folder']}/{table['name']}/moved to table{new_index}")
        xml_path: Path = archive.joinpath("tables", table["folder"], table["folder"]).with_suffix(".xml")
        xsd_path: Path = xml_path.with_suffix(".xsd")
        xml_path = xml_path.rename(xml_path.with_name(f"table{new_index}.xml"))
        xsd_path = xsd_path.rename(xsd_path.with_name(f"table{new_index}.xsd"))
        table_xml_update(xml_path, new_index, [], xml_path.with_name("." + xml_path.name))
        table_xsd_update(xsd_path, new_index, [], xsd_path)
        xml_path.unlink(missing_ok=True)
        xml_path.with_name("." + xml_path.name).rename(xml_path)
        if new_index != index:
            xml_path.parent.rename(f"table{new_index}")


def cli():
    """
    Remove tables from a given archive.
    """

    parser = ArgumentParser("clean-empty-columns", description=cli.__doc__)
    parser.add_argument("archive", type=Path, help="the path to the archive")
    parser.add_argument("tables", nargs="+", help="the tables to remove")
    parser.add_argument("--log-file", type=Path, default=None, help="write change events to log file")

    args = parser.parse_args()

    main(args.archive, args.tables, args.log_file)
