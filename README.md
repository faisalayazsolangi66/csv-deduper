# CSV Deduper

Remove duplicate rows from a CSV file. Two rows count as duplicates
when their values match on the chosen key columns (all columns by
default). The first occurrence is kept unless `--keep last` is
used. Removed rows can be saved separately with
`--duplicates-out`, and a short report is printed.

## Requirements

- Python 3 (standard library only, no extra packages)

## Usage

```bash
python3 main.py data.csv -o clean.csv
python3 main.py data.csv --in-place
python3 main.py data.csv -o clean.csv --columns email --keep last
python3 main.py data.csv -o clean.csv --case-insensitive --duplicates-out dups.csv
```

## Example

```bash
$ cat people.csv
name,email
Ayesha,ayesha@example.com
Bilal,bilal@example.com
Ayesha,ayesha@example.com

$ python3 main.py people.csv -o clean.csv
Removed 1 duplicate row(s); kept 2 of 3 row(s)
Wrote clean.csv

$ cat clean.csv
name,email
Ayesha,ayesha@example.com
Bilal,bilal@example.com
```

## License

MIT — see [LICENSE](LICENSE).
