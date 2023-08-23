## Convert-Compare

> This tool provides a way for you to easily compare files between original, master and statutory

### Installation

Preferred way is to install with pipx: `pipx install git+https://github.com/aarhusstadsarkiv/convert-qa.git`

### Instructions

The script requires that you specify the paths to original and master documents:

- `convert-compare --master path/to/master/files --original path/to/original/files`

Statutory documents can also be specified with `--statutory` but is optional

The tool only reads from the metadata database for the original documents.

Default output is set to `./comparison_output`, this can be changed with `-o` and `--output`.

### Help

```
usage: main.py [-h] [--original ORIGINAL] [--statutory STATUTORY] [--master MASTER] [-o OUTPUT] [--digiarch]
               [--silent]

Easily compare files between original, master and statutory

options:
  -h, --help            show this help message and exit
  --original ORIGINAL   directory pointing to original documents containing the metadata folder
  --statutory STATUTORY
                        (optional) directory pointing to statutory documents containing the metadata folder
  --master MASTER       directory pointing to master documents containing the metadata folder
  -o, --output OUTPUT   directory to output files into
  --digiarch            generate metadata folder with digiarch
  --silent              only print errors
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
