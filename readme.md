# Convert QA

## Installation

Preferred way is to install with pipx: `pipx install git+https://github.com/aarhusstadsarkiv/convert-qa.git`

## Convert-Compare

This tool provides a way for you to easily compare files between original, master and statutory

The script requires that you specify the paths to original and master documents:

- `convert-compare --master path/to/master/files --original path/to/original/files`

Statutory documents can also be specified with `--statutory` but is optional

The tool only reads from the metadata database for the original documents.

Default output is set to `./comparison_output`, this can be changed with `-o` and `--output`.

```
convert-compare [-h] [--original ORIGINAL] [--master MASTER] [--statutory STATUTORY] [--output OUTPUT] [--digiarch]

options:
  -h, --help            show this help message and exit
  --original ORIGINAL   directory pointing to original documents containing the metadata folder
  --master MASTER       directory pointing to master documents
  --statutory STATUTORY
                        (optional) directory pointing to statutory documents
  --output OUTPUT       directory to output files into
  --digiarch            generate metadata folder with digiarch
```

## Convert-Encoding

This tool takes a list of Open Document files and check the text inside the content.xml file for unusual character
sequences.

The characters are searched within tags, they must be surrounded by ASCII characters and not included in the
optional `IGNORE` argument.

```
convert-encoding [-h] [--ignore IGNORE] files [files ...]

positional arguments:                                                                                                                                                                                                          
  files            the files to check                                                                                                                                                                                          
                                                                                                                                                                                                                               
options:                                                                                                                                                                                                                       
  -h, --help       show this help message and exit
  --ignore IGNORE  extra characters to ignore
```

## clean-empty-columns

Take a list of databases or archive folders and check each table for empty columns (all values either null or '').
Completely empty tables will also be removed.

Empty columns are removed only if the `--commit` option is used and are otherwise ignored.

```
clean-empty-columns [-h] [--commit] [--log-file LOG_FILE] {archive,sqlite} files [files ...]

positional arguments:
  {archive,sqlite}     whether the files are archives or SQLite databases
  files                the databases/archives to clean

options:
  -h, --help           show this help message and exit
  --commit             commit changes to database
  --log-file LOG_FILE  write change events to log file
```

## remove-duplicate-rows

Remove duplicate rows from a SQLite database.

Duplicate rows are removed only if the `--commit` option is used and are otherwise ignored.

```
remove-duplicate-rows [-h] [--commit] --log-file LOG_FILE file [file ...]       

positional arguments:                                                           
  file                 the path to the database file                            
                                                                                
options:                                                                        
  -h, --help           show this help message and exit
  --commit             commit changes to database
  --log-file LOG_FILE  write change events to log file
```

## remove-tables

Remove tables from a given archive.

```
remove-tables [-h] [--log-file LOG_FILE] archive tables [tables ...]

positional arguments:
  archive              the path to the archive
  tables               the tables to remove

options:
  -h, --help           show this help message and exit
  --log-file LOG_FILE  write change events to log file
```
