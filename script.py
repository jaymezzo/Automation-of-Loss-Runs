import pandas as pd
from pdfminer.high_level import extract_text
import glob
import os
import re


# =====================
# extract text from pdf
# =====================
pdf_folder = "submission_pdfs/"
txt_folder = "text_files/"

# creates a list of pdf files from the folder
pdf_list = glob.glob(os.path.join(pdf_folder, "*"))

# for each pdf, extract text and put into corresponding txt file
for pdf in pdf_list:
    pdf_text = extract_text(pdf)
    text_file_name = pdf.split("\\")[1].split(" ")[0].strip("_")
    with open(txt_folder + text_file_name + ".txt", "w") as file:
        file.write(pdf_text)

# =============
# extract table
# =============

txt_folder_list = glob.glob(os.path.join(txt_folder, "*"))


def open_text_file(text_file):
    with open(text_file, "r") as file:
        text = file.read()
        return text


for file in txt_folder_list:
    name = file.split("\\")[1].strip(".txt")
    text = open_text_file(file)
    lower_text = text.lower()
    text_list = lower_text.split("\n")

    end_index = "\n\n"
    index_year = -1
    index_claims = -1

    # patterns
    year_pattern = "\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}"
    claims_patterns = "^-?\d+$"
    for index, item in enumerate(text_list, start=1):
        if item == "year":
            if re.match(year_pattern, text_list[index + 1]):
                index_year = index
        if item == "# claims":
            index_claims = index
        if "number" in item:
            if re.match(claims_patterns, text_list[index + 1]):
                index_claims = index

    year = text_list[index_year:]
    claims = text_list[index_claims:]

    year_list = []
    claims_list = []
    # year list
    for line in year:
        if re.match(year_pattern, line):
            year_list.append(line)
        if line == "":
            break
    # claims list
    for line in claims:
        if re.match(claims_patterns, line):
            claims_list.append(line)
        if line == "":
            break

    print("\n\n" + name + "\n")
    print("\tYear Range")
    for year in year_list:
        print("\t" + year)

    print("\n\t# of Claims")
    for claims in claims_list:
        print("\t" + claims)
