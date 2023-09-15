from tabula import convert_into
from PyPDF2 import PdfReader, PdfWriter
from tempfile import NamedTemporaryFile
from tqdm import tqdm
import os
import csv
import re

# regex to collapse whitespaces
whitespace_re = re.compile(r'\W+')

# CSV export header fields
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


def read_pdf_rows(input_path):
    """
    Generator, Parses PDF using tabula
    and spits out rows for processing
    :param input_path:
    :return: generator
    """

    # Generate temporary PDF, removing the first two and last pages
    # makes it easier for tabula to make sense of things
    infile = PdfReader(input_path)
    outfile = PdfWriter()
    for page_num in range(2, len(infile.pages) - 1):
        outfile.addPage(infile.pages[page_num])

    with NamedTemporaryFile("wb") as f:
        outfile.write(f)
        f.flush()

        with NamedTemporaryFile("w+", encoding="utf-8") as csv_f:
            convert_into(f.name, csv_f.name, guess=False, lattice=True, pages="all", silent=True)
            csv_reader = csv.reader(csv_f, delimiter=",", )
            next(csv_reader)

            # iterate through the csv, strip out empty spaces
            # and collapse whitespace
            for row in csv_reader:
                yield [whitespace_re.sub(' ', col) for col in row if col]


def process_pdf(infile, outfile):
    """
    Processes a single pdf
    :param infile: input path
    :param outfile: output path
    :return: bool, success
    """
    errors = [infile, ]

    with open(outfile, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        for row in filter(lambda x: len(x) != 1, read_pdf_rows(infile)):
            # test for row sanity
            if len(row) != 8:
                errors.append("Invalid row count encountered")
                errors.append(str(row))
                continue

            row[6] = ascii_to_utf8(row[6], True)
            row[7] = ascii_to_utf8(row[7], True)

            writer.writerow(row)

    return "::".join(errors)


def process_pdf_dir(pdf_path="./PDF", csv_path="./CSV"):
    # Create CSV Dir in case it doesn't exist
    if not os.path.exists(csv_path):
        os.mkdir(csv_path)

    # Glob for .pdf in pdf_path, generate tuples (for input, output)
    files = [(os.path.join(pdf_path, f), os.path.join(csv_path, f"{f}.csv"))
             for f in os.listdir(pdf_path) if (f.endswith(".pdf"))]

    process_report = []
    for i in tqdm(files):
        process_report.append(process_pdf(*i))

    with open("extraction_report.log", "w") as f:
        f.write("\n".join(process_report))


if __name__ == "__main__":
    process_pdf_dir("./PDF", "./CSV")
