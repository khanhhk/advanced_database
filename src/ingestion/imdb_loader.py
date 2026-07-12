import csv
import gzip
from pathlib import Path


def load_tsv(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            yield {key: (None if value == "\\N" else value) for key, value in row.items()}
