from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from xmltodict import parse as parse_xml
from xmltodict import unparse as unparse_xml

from ..clean_empty_columns.main import print_with_file


def table_xsd_add_key(path: Path, out_path: Optional[Path] = None) -> Path:
    out_path = out_path or path.with_suffix(".new" + path.suffix)

    with path.open("rb") as fi:
        xsd = parse_xml(fi, "utf-8", force_list=True)

        xsd["xs:schema"][0]["xs:complexType"][0]["xs:sequence"][0]["xs:element"].append({
            "@minOccurs": "1",
            "@name": f'c{len(xsd["xs:schema"][0]["xs:complexType"][0]["xs:sequence"][0]["xs:element"]) + 1}',
            "@nillable": "false",
            "@type": "xs:integer"
        })

        with out_path.open("wb") as fo:
            unparse_xml(xsd, fo, "utf-8")

    return out_path


# noinspection HttpUrlsUsage
def table_xml_add_key(path: Path, index: int, out_path: Optional[Path] = None) -> Path:
    out_path = out_path or path.with_suffix(".new" + path.suffix)

    with path.open("rb") as fi:
        with out_path.open("w", encoding="utf-8") as fo:
            fo.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
            fo.write(
                f'<table '
                f'xsi:schemaLocation="http://www.sa.dk/xmlns/siard/1.0/schema0/table{index}.xsd ./table{index}.xsd" '
                f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                f'xmlns="http://www.sa.dk/xmlns/siard/1.0/schema0/table{index}.xsd">\n')

            key_index: dict[str, int] = {"k": 1}

            def callback(_, row: dict):
                row[f"c{len(row) + 1}"] = key_index["k"]
                key_index["k"] = key_index["k"] + 1
                unparse_xml({"row": row}, fo, "utf-8", full_document=False)
                fo.write("\n")
                return True

            parse_xml(fi, item_depth=2, item_callback=callback, force_list=True)
            fo.write('</table>')

    return out_path


def main(archive: Path, log_file: Path):
    echo = print_with_file(log_file)

    tables_index_path: Path = archive.joinpath("Indices", "tableIndex.xml")
    tables_index: dict = parse_xml(tables_index_path.read_text("utf-8"), force_list=True)
    tables: list[dict] = tables_index["siardDiark"][0]["tables"][0]["table"]
    tables_new: list[dict] = []

    for table in tables:
        if table["primaryKey"][0]["name"][0].lower() != "missing":
            tables_new.append(table)
            continue

        index: int = int(table["folder"][0].removeprefix("table"))
        table_folder: Path = archive.joinpath("tables", table["folder"][0])

        print(f"{archive.name}/{table['folder'][0]}/adding key... ", end="", flush=True)

        xml_path: Path = table_folder.joinpath(table["folder"][0]).with_suffix(".xml")
        xml_path_tmp = table_xml_add_key(xml_path, index, xml_path.with_name("." + xml_path.name))
        xml_path_tmp.replace(xml_path)

        xsd_path: Path = xml_path.with_suffix(".xsd")
        xsd_path_tmp = table_xsd_add_key(xsd_path, xsd_path.with_name("." + xsd_path.name))
        xsd_path_tmp.replace(xsd_path)

        table["primaryKey"][0]["name"][0] = f"pk_{table['name'][0]}"
        table["primaryKey"][0]["column"][0] = "aca_id__"
        table["columns"][0]["column"].append({
            "name": [table["primaryKey"][0]["column"][0]],
            "columnID": [f'c{len(table["columns"][0]["column"]) + 1}'],
            "type": ["INTEGER"],
            "nullable": ["false"],
            "description": ["Primær nøgle genereret af Aarhus stadsarkiv"],
        })

        tables_new.append(table)

        echo(f'\r{archive.name}/{table["folder"][0]}/added '
             f'{table["columns"][0]["column"][-1]["columnID"][0]} '
             f'{table["primaryKey"][0]["column"][0]}')

    tables_index["siardDiark"][0]["tables"][0]["table"] = tables_new
    with tables_index_path.open("wb") as fh:
        unparse_xml(tables_index, fh, "utf-8")


def cli():
    """
    Add missing primary keys to an archive.
    """

    parser = ArgumentParser("primary-keys", description=cli.__doc__)
    parser.add_argument("archive", type=Path, help="the path to the archive")
    parser.add_argument("--log-file", type=Path, required=True, help="write change events to log file")

    args = parser.parse_args()

    main(args.archive, args.log_file)
