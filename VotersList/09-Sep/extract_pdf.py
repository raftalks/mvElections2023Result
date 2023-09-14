from tabula import read_pdf
import pandas as pd
import os
import glob
from tqdm import tqdm
import csv

fields = ["#", "Island", "House Name", "Name", "Sex", "National ID", "Address_DV", "Name_DV"]

# a mapping of ascii character to the unicode integer value
# of the corresponding Thaana character as on the Phonetic keyboard layout
AsciiToUnicode = {'h': 1920, 'S': 1921, 'n': 1922, 'r': 1923,
                  'b': 1924, 'L': 1925, 'k': 1926, 'a': 1927,
                  'v': 1928, 'm': 1929, 'f': 1930, 'd': 1931,
                  't': 1932, 'l': 1933, 'g': 1934, 'N': 1935,
                  's': 1936, 'D': 1937, 'z': 1938, 'T': 1939,
                  'y': 1940, 'p': 1941, 'j': 1942, 'C': 1943,
                  'X': 1944, 'H': 1945, 'K': 1946, 'J': 1947,
                  'R': 1948, 'x': 1949, 'B': 1950, 'F': 1951,
                  'Y': 1952, 'Z': 1953, 'A': 1954, 'G': 1955,
                  'q': 1956, 'V': 1957, 'w': 1958, 'W': 1959,
                  'i': 1960, 'I': 1961, 'u': 1962, 'U': 1963,
                  'e': 1964, 'E': 1965, 'o': 1966, 'O': 1967,
                  'c': 1968, ',': 1548, ';': 1563, '?': 1567,
                  ')': 41, '(': 40, 'Q': 65010}


def ascii_to_utf8(text: str, reverse=False):
    """
    Converts Ascii thaana (left to right) to Utf8.
    accepts byte-string returns unicode-string
    """
    spam = u""
    if reverse:
        text = "".join(reversed(text))

    for c in text:
        spam += chr(AsciiToUnicode[c]) if c in AsciiToUnicode else c

    return spam


def process_pdf(input_file, output_file):
    ls = read_pdf(
        input_file,
        guess=False, pages='all',
        multiple_tables=True,
        lattice=True, pandas_options={'header': None},
        silent=True
    )

    df = pd.DataFrame()

    for frame in ls:
        frame = frame.dropna(axis=1, how='all')
        frame = frame.replace('\\s+', ' ', regex=True)
        df = df._append(frame, ignore_index=True)

    df.to_csv(output_file, index=False, header=False)


def process_pdf_dir(pdf_path="./PDF", csv_path="./CSV"):
    # Glob for .pdf in pdf_path
    files = [f for f in os.listdir(pdf_path) if (f.endswith(".pdf"))]

    if not os.path.exists(csv_path):
        os.mkdir(csv_path)

    for f in tqdm(files):
        process_pdf(os.path.join(pdf_path, f), os.path.join(csv_path, f"{f}.csv"))


# def cleancsv():
#     print("Sanitizing and combining csvs")
#     files = glob.glob("./csv/*.csv")
#     df = pd.DataFrame(columns=["File"].extend(fields))
#
#     rows = []
#     for csv_file in tqdm(files):
#
#         with open(csv_file, 'r') as f:
#             reader = csv.DictReader(f, fieldnames=fields)
#             for row in reader:
#                 # sanity check
#                 if len(row.keys()) != 8:
#                     print(f"error in {csv_file}")
#
#                 # skip if dirty header
#                 if "#" in row.values():
#                     continue
#
#                 # thaanafy the weird fields
#                 for n in ["csercDea", "cnwn"]:
#                     row[n] = ascii_to_utf8(row[n][::-1])
#
#                 row["File"] = f.name.replace(".csv", "").replace(".pdf", "").replace("./csv/", "")
#
#                 rows.append(row)
#
#     df = df.append(rows, ignore_index=True)
#     df.to_csv("sanitized_output.csv", index=False)


if __name__ == "__main__":
    process_pdf_dir("./PDF", "./CSV")
