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
        #get index
        if re.match(year_pattern, item):
            start_index = index
            break
        
    data_temp = text_list[start_index-1:]
    data = []
    for line in data_temp:
        if not re.match(year_pattern, line):
            break
        else:
            data.append(line)

    data.insert(0, text_list[start_index-2])

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
            for i in range(len(columns)-1):
                if columns[i] == "#":
                    new_col = columns[i] + " " + columns[i+1]
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



# Load the existing Excel file
wb = openpyxl.load_workbook(filename="Copy of Loss Rater.xlsm")
ws = wb.active 

print("Active Cell: ", ws.active_cell)

current_df = extracted_tables[0]

start_date_df = current_df["start_date"]
target_cell = "C3"

for index, row in start_date_df.iterrows():
    ws[target_cell].value = row
    target_cell = ws.cell(row=ws[target_cell].row + 1, column=ws[target_cell].column).coordinate


