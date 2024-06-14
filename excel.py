from openpyxl import load_workbook
 
# Load the original Excel file
original_file = "Copy of Loss Rater.xlsx"
workbook = load_workbook(filename=original_file)
 
# Save the workbook as a new file
copy_file = "test_loss_rater_copy.xlsx"
workbook.save(filename=copy_file)
 
print(f"The file has been copied successfully as {copy_file}.")
 
