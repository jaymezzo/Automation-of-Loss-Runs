import pandas as pd
from pdfminer.high_level import extract_text
import pdfplumber
import re
import openpyxl
from openpyxl import load_workbook

# =====================
# extract text from pdf
# =====================
pdf_folder = "submission_pdfs/"
txt_folder = "text_files/"

pdf = "submission_pdfs/Namdar Realty Group_ LLC_Submission_GL_2024-04-12_133114_458.pdf"
text_file_name = pdf.split("/")[-1].split(" ")[0].strip("_")
pdf_text = ""

# Extract the text
with pdfplumber.open(pdf) as pdf:
    for page in pdf.pages:
        pdf_text += page.extract_text()


# =============
# extract table
# =============

lower_text = pdf_text.lower()
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
print(df)

# ==================
# import df to excel
# ==================

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


# target cells
START_DATE_TARGET = "C9"
END_DATE_TARGET = "D9"
INCURRED_LOSSES_TARGET = "G9"
PAID_LOSSES_TARGET = "I9"
CLAIMS_COUNT_TARGET = "K9"


for i in range(len(df["start_date"])):
    ws[START_DATE_TARGET].value = df["start_date"][i]
    START_DATE_TARGET = ws.cell(
        row=ws[START_DATE_TARGET].row + 1, column=ws[START_DATE_TARGET].column
    ).coordinate

    ws[END_DATE_TARGET].value = df["end_date"][i]
    END_DATE_TARGET = ws.cell(
        row=ws[END_DATE_TARGET].row + 1, column=ws[END_DATE_TARGET].column
    ).coordinate

    ws[CLAIMS_COUNT_TARGET].value = (
        df["# claims"][i] if "# claims" in df.columns else df["number"][i]
    )
    CLAIMS_COUNT_TARGET = ws.cell(
        row=ws[CLAIMS_COUNT_TARGET].row + 1, column=ws[CLAIMS_COUNT_TARGET].column
    ).coordinate

    ws[INCURRED_LOSSES_TARGET].value = df["incurred"][i]
    INCURRED_LOSSES_TARGET = ws.cell(
        row=ws[INCURRED_LOSSES_TARGET].row + 1, column=ws[INCURRED_LOSSES_TARGET].column
    ).coordinate

    ws[PAID_LOSSES_TARGET].value = (
        df["paid"][i] if "paid" in df.columns else df["indemnity"][i]
    )
    PAID_LOSSES_TARGET = ws.cell(
        row=ws[PAID_LOSSES_TARGET].row + 1, column=ws[PAID_LOSSES_TARGET].column
    ).coordinate

print("Saving new file...")
wb.save(filename=copy_file)
print("File saved!")
