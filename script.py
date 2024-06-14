import pandas as pd
from pdfminer.high_level import extract_text
import glob
import os
import re
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows


# =====================
# extract text from pdf
# =====================
pdf_folder = "submission_pdfs/"
txt_folder = "text_files/"

# creates a list of pdf files from the folder
pdf_list = glob.glob(os.path.join(pdf_folder, "*"))

# # for each pdf, extract text and put into corresponding txt file
# for pdf in pdf_list:
#     pdf_text = extract_text(pdf)
#     text_file_name = pdf.split("\\")[1].split(" ")[0].strip("_")
#     with open(txt_folder + text_file_name + ".txt", "w") as file:
#         file.write(pdf_text)


# pdfplumber
import pdfplumber

for pdf in pdf_list:
    text_file_name = pdf.split("\\")[1].split(" ")[0].strip("_")
    with pdfplumber.open(pdf) as pdf:
        # Extract the text from all pages
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()
        with open(txt_folder + text_file_name + ".txt", "w") as file:
            file.write(pdf_text)


# =============
# extract table
# =============

txt_folder_list = glob.glob(os.path.join(txt_folder, "*"))

extracted_tables = list()


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
    start_index = -1

    year_pattern = "\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}"

    for index, item in enumerate(text_list, start=1):
        # get index
        if re.match(year_pattern, item):
            start_index = index
            break

    data_temp = text_list[start_index - 1 :]
    data = []
    for line in data_temp:
        if not re.match(year_pattern, line):
            break
        else:
            data.append(line)

    data.insert(0, text_list[start_index - 2])

    # print("\n\n" + name + "\n")
    # print("\tData")
    # for line in data:
    #     print("\t" + line)

    # cleaing columns
    columns = []
    for line in data:
        if re.match("year", line):
            # creating columns from line
            columns = line.split(" ")
            # fixing claims column
            for i in range(len(columns) - 1):
                if columns[i] == "#":
                    new_col = columns[i] + " " + columns[i + 1]
                    columns.pop(i)
                    columns.pop(i)
                    columns.insert(i, new_col)
                    break

    columns.pop(0)
    columns.insert(0, "end_date")
    columns.insert(0, "start_date")

    row_data = []

    for line in data:
        row = []
        if re.match(year_pattern, line):
            row = line.split(" ")
            for i in range(len(row)):
                if re.match(year_pattern, row[i]):
                    years = row[i].split("-")
                    row.pop(i)
                    row.insert(0, years[1])
                    row.insert(0, years[0])
                    break
            row_data.append(row)

    df = pd.DataFrame(row_data, columns=columns)
    # print(df)
    extracted_tables.append(df)


from openpyxl import load_workbook

# Load the original Excel file
original_file = "Copy of Loss Rater.xlsx"
print("Loading origianl workbook...")
origianl_workbook = load_workbook(filename=original_file)
print("Workbook successfully loaded.\n")

# Save the workbook as a new file
copy_file = "test_loss_rater_copy.xlsx"
print("Copying file...")
origianl_workbook.save(filename=copy_file)
print(f"File copied as {copy_file}.\n")

origianl_workbook.close()

print("Loading coppied filed...")
wb = load_workbook(filename=copy_file)
print("\Copied file loaded.\n")
ws = wb["GL_LossExperience_Input"]

current_df = extracted_tables[0]

start_date_data = current_df["start_date"]
start_date_df = pd.DataFrame(start_date_data, columns=["start_date"])

# target cells
START_DATE_TARGET = "C9"
END_DATE_TARGET = "D9"
INCURRED_LOSSES_TARGET = "G9"
PAID_LOSSES_TARGET = "I9"
CLAIMS_COUNT_TARGET = "K9"


for i in range(len(current_df["start_date"])):
    ws[START_DATE_TARGET].value = current_df["start_date"][i]
    START_DATE_TARGET = ws.cell(
        row=ws[START_DATE_TARGET].row + 1, column=ws[START_DATE_TARGET].column
    ).coordinate

    ws[END_DATE_TARGET].value = current_df["end_date"][i]
    END_DATE_TARGET = ws.cell(
        row=ws[END_DATE_TARGET].row + 1, column=ws[END_DATE_TARGET].column
    ).coordinate

    ws[CLAIMS_COUNT_TARGET].value = (
        current_df["# claims"][i]
        if "# claims" in current_df.columns
        else current_df["number"][i]
    )
    CLAIMS_COUNT_TARGET = ws.cell(
        row=ws[CLAIMS_COUNT_TARGET].row + 1, column=ws[CLAIMS_COUNT_TARGET].column
    ).coordinate

    ws[INCURRED_LOSSES_TARGET].value = current_df["incurred"][i]
    INCURRED_LOSSES_TARGET = ws.cell(
        row=ws[INCURRED_LOSSES_TARGET].row + 1, column=ws[INCURRED_LOSSES_TARGET].column
    ).coordinate

    ws[PAID_LOSSES_TARGET].value = (
        current_df["paid"][i]
        if "paid" in current_df.columns
        else current_df["indemnity"][i]
    )
    PAID_LOSSES_TARGET = ws.cell(
        row=ws[PAID_LOSSES_TARGET].row + 1, column=ws[PAID_LOSSES_TARGET].column
    ).coordinate

print("Saving new file...")
wb.save(filename=copy_file)
print("File saved!")
