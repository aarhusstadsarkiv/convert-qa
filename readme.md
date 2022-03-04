## Converqa

> This tool provides a way for you to easily compare files between original, master and statutory

### Instructions

The script requires that you specify the paths to original and master documents:

- `python main.py --master path/to/master/files --original path/to/original/files`

Statutory documents can also be specified with `--statutory` but is optional

The tool only reads from the metadata database for the original documents.

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
  -o OUTPUT, --output OUTPUT
                        directory to output files into
  --digiarch            generate metadata folder with digiarch
  --silent              only print errors
```

