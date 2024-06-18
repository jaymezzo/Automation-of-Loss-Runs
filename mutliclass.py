import pdfplumber
import re
import pandas as pd
import sys
import os

# Move to the folder of submissions, redefine path as you need
# Get the current working directory
current_directory = os.getcwd()

print(f"Current directory is: {current_directory}")

# # Define the target directory
# target_directory = "submissions"

# # Move the current file to the target directory
# os.rename(current_directory, target_directory)

# Print a success message
# print(f"Current directory moved to {target_directory}")


def PDFtoText(path_to_pdf: str):
    """
    converts PDF to a string variable

    input: string
    output: string variable containing losses with labels from PDF
    """
    # initiate text variable

    text = " "

    with pdfplumber.open(path_to_pdf) as pdf:
        pages = pdf.pages
        for page in pages:
            new = page.extract_text()
            text += new

    # Find the index positions of 'LOSSES' and 'ADDITIONAL INFORMATION'
    losses_index = text.find("LOSSES")
    additional_info_index = text.find("ADDITIONAL INFORMATION")

    # Find the index position of 'LARGE LOSSES'
    large_losses_index = text.find("LARGE LOSSES")

    # Slice the string to get the portions after 'LOSSES' and 'ADDITIONAL INFORMATION'
    losses = (
        text[losses_index + len("LOSSES") : large_losses_index]
        if losses_index != -1
        else ""
    )

    # Slice the string to get the parts after 'LARGE LOSSES'
    large_losses = (
        text[large_losses_index + len("LARGE LOSSES") : additional_info_index]
        if large_losses_index != -1
        else ""
    )

    print("LOSSES:\n", losses)
    print("\nLARGE LOSSES:\n", large_losses)

    return losses


def multiclass_count(text: str):
    """
    Determines how many classes there are in the text.
    There are 4 classes in total: Gen'l Liab, Auto liab, Excess Auto Liab, and Professional Liab

    input:
    string that contains the labels extracted from pdf

    outputs:
    - count of how many unique claases there are (int)
    - names of the unique classes (list of strings)
    """
    # Regular expression to find patterns that look like the labels
    # We assume labels consist of one or two words ending with 'Liab'
    # -> if there are new classes, change the following line of code
    pattern = re.compile(r"(Gen'l Liab|Auto Liab|Excess Auto Liab|Professional Liab)")

    # Find all matches in the text
    matches = pattern.findall(text)

    # Convert list of matches to a set to remove duplicates
    unique_labels = set(matches)

    # Return the count of unique labels and the list of unique labels
    return len(unique_labels), list(unique_labels)


def match_start(losses):
    """
    Goes through all lines
    in the variables "lines" (losses without headers) and attemtps
    to match each line to the default pattern. It then calls the function match_round2()

    inputs:
    - losses: string
    """
    # First round: Extracting data from the text

    # define default data_pattern based on num_classes
    num_classes, _ = multiclass_count(losses)

    if num_classes == 3:
        data_pattern = re.compile(
            r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)"
        )
    elif num_classes == 4:
        data_pattern = re.compile(
            r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)"
        )
    elif num_classes == 2:
        data_pattern = re.compile(
            r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)"
        )

    # find matches
    matches = data_pattern.findall(losses)

    # check if any expected data is missing
    if not matches:
        print("No data captured. Please check the losses string format.")
    else:
        print("Captured Matches:")
        for match in matches:
            print(match)

    final_matches = match_round2(matches, losses, data_pattern)

    return final_matches


def reformat(line, pattern: re.Pattern, matches: list, pattern_ind: int, line_ind: int):
    """
    This function takes in a unmatched line in round 1 (due to missing values)
    and reformats it so that
    (1) It's in the standarized format
    (2) missing value defaults to 0
    (3) Adds the reformatted line to the list named "matches"

    inputs:
    - line (str): a line from the list "unmatched". Lines contains all lines in the loss run table
    - pattern (re.Pattern): the pattern that the unmatched line matched to in the 2nd round
    - matches (list): the list that contains all lines that matched with the default pattern from the 1st round. Example:
        ('06/01/2021-06/01/2022', '$2,245', '4', '$21,845', '10', '$0', '0')
        ('06/01/2020-06/01/2021', '$3,298', '7', '$1,094,083', '4', '$1,762,338', '1')
        ('06/01/2019-06/01/2020', '$4,826', '4', '$2,681', '5', '$0', '0')
        ('06/01/2018-06/01/2019', '$106,121', '7', '$26,007', '5', '$0', '0')`
    - pattern_ind (int): the index of the pattern

    output:
    - matches (list): OG list with reformatted matches appended
    """

    match = pattern.search(line)
    print(f"match is {match}")

    # Extract the groups from the match
    groups = list(match.groups())

    print(f"Current unmatched line number is {line_ind}.")
    print(f"Current unmatched line is {line}.")

    # Extract the groups from the match, check is matach is none
    groups = list(match.groups())

    # Replace empty values with '0'
    # since we know the 2nd incurred is missing,
    # add $0 in the position where the second total incurred value should be
    standardized_groups = groups.copy()

    # two ways to do this
    # (1) insert  without checking (faster)
    # check that the index 3 is 0
    # insert "$0" at index 3
    if standardized_groups[pattern_ind + 1] == "0":
        standardized_groups.insert(pattern_ind + 1, "$0")
    else:
        print("The 2nd number of claims is not 0!")

    # (2) check for 0 as claims value (we are not using this yet, wait til testing)
    # for index, g in enumerate(groups):
    #     if index == 3 and g.strip() == '0':  # Check if the position corresponds to the second incurred
    #         standardized_groups.append('$0')  # Insert '$0' for the missing second incurred value
    #     else:
    #         standardized_groups.append(g if g and g.strip() != '$0' else '0')  # Handle other values as usual

    # Insert the standardized tuple to the right position in matches
    # use the index, line[0]
    matches.insert(line_ind - 1, tuple(standardized_groups))

    return matches


def match_round2(matches, losses, data_pattern):
    """

    inputs:
    - matches: a list of matched lines after the first round
    - losses: loss run table
    outputs:
    - matches: a list of matched lines with newly appended unmatched lines
    """
    # 2nd Round: check if there are rows that might not be captured by analyzing the text more closely

    # remove first 4 rows of losses
    # Split the text into lines
    lines = losses.strip().split("\n")

    # Remove the first four lines
    lines = lines[4:]

    expected_rows = len(lines)

    if len(matches) != expected_rows:
        print(
            f"Expected to capture {expected_rows} rows, but only captured {len(matches)}."
        )
        missing_rows_count = expected_rows - len(matches)
        print(f"Missing rows count: {missing_rows_count}")

        # track lines that weren't captured
        unmatched = []

        # Analyze each line, add all unmatched lines in the 1st round
        for index, line in enumerate(lines):
            if not data_pattern.search(line):
                unmatched.append(
                    (index, line)
                )  # Add 1 to index because line numbers usually start at 1

        print(unmatched)

        # Try alternative patterns to capture these lines, ADD DIFFERENT PATTERNS IF NEEDED
        for line_number, line in unmatched:
            # Pattern with the first incurred loss possibly missing
            pattern1 = re.compile(
                r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)"
            )

            # Pattern with the second incurred loss possibly missing
            pattern2 = re.compile(
                r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\$\d|\S*) (\d+|0) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)"
            )

            # Pattern with the third incurred loss possibly missing
            pattern3 = re.compile(
                r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\$\d|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) (\d+|0)"
            )

            if pattern1.search(line):
                print(f"Line {line_number} matches pattern1.")

                # call reformat to reformat this line, updates matches
                matches = reformat(line, pattern1, matches, 1, line_number)

            elif pattern2.search(line):
                print(f"Line {line_number} matches pattern2.")

                matches = reformat(line, pattern2, matches, 2, line_number)

            elif pattern3.search(line):
                print(f"Line {line_number} matches pattern3.")

                matches = reformat(line, pattern3, matches, 3, line_number)
            else:
                print(f"Line {line_number} does not match any known pattern.")
        else:
            print("All lines are successfully captured after second check.")

    else:
        print("All rows are successfully captured after second check.")

    return matches


def ExportDf(text, matches):
    """
    Process the text string when there is more than one class.
    There are 4 classes in total: Gen'l Liab, Auto liab, Excess Auto Liab, and Professional Liab
    input: string that contains the text extracted from pdf
    output: standardized pandas dataframe
    """

    count, lst = multiclass_count(text)

    # define number of columns
    # the formula is 2 (start date and end date) + count * 2 (rach class has 2 columns, total incurred and total number)

    # Define the number of columns based on the formula
    num_columns = 2 * count + 2

    # Create a DataFrame with the required number of columns
    column_names = []
    for label in lst:
        column_names.extend([f"{label} Total Incurred", f"{label} Number"])
    column_names.extend(["Effective Date", "Expiration Date", "Evaluation Date"])

    # Initialize the DataFrame with zero rows, just column definitions
    df = pd.DataFrame(columns=column_names)

    print(f"intialized df is: {df}")

    # List to hold each row's data (as dictionaries)
    rows = []

    # # Process each match to create a dictionary for each row, this is the case where there are 3 categories: gl, al, and eal
    # for match in matches:
    #     date_range, gl_incurred, gl_number, al_incurred, al_number, eal_incurred, eal_number = match
    #     start_date, end_date = date_range.split('-')
    #     row = {
    #         'Gen\'l Liab Total Incurred': gl_incurred,
    #         'Gen\'l Liab Number': gl_number,
    #         'Auto Liab Total Incurred': al_incurred,
    #         'Auto Liab Number': al_number,
    #         'Excess Auto Liab Total Incurred': eal_incurred,
    #         'Excess Auto Liab Number': eal_number,
    #         'Effective Date': start_date,
    #         'Expiration Date': end_date,
    #         'Evaluation Date': '05/07/2024'
    #     }
    #     print(row)
    #     rows.append(row)

    # # Define the column names based on the labels found
    # column_names = [
    #     'Gen\'l Liab Total Incurred', 'Gen\'l Liab Number',
    #     'Auto Liab Total Incurred', 'Auto Liab Number',
    #     'Excess Auto Liab Total Incurred', 'Excess Auto Liab Number',
    #     'Effective Date', 'Expiration Date', 'Evaluation Date'
    # ]

    # Process each match to create a dictionary for each row
    for match in matches:
        row_dict = {}
        date_range = match[0]
        start_date, end_date = date_range.split("-")
        row_dict["Effective Date"] = start_date
        row_dict["Expiration Date"] = end_date
        row_dict["Evaluation Date"] = "05/07/2024"  # This should be taken from the text

        # Handle the data for each class
        match_index = 1  # Start after the date range
        for label in lst:
            row_dict[f"{label} Total Incurred"] = match[match_index]
            row_dict[f"{label} Number"] = match[match_index + 1]
            match_index += 2  # Move index to the next class

        rows.append(row_dict)

    # Initialize the DataFrame with the row data
    df = pd.DataFrame(rows, columns=column_names)
    return df


pdf = (
    "submission_pdfs/Fernlea Industries_ Inc__Submission_UMB_2024-06-04_012751_392.pdf"
)


"""
Takes a "multiclass" dateframe and a file name and outputs a list of dataframes and list of filenames
Purpose: Each category of liability (Excess Auto, Auto, Gen'l, Professional),
         must be in its own Excel Loss Rater sheet.
         So we split the table from the pdf into x amount of tables, where x is the number of categories present in the pdf 
         and transform them to follow the logic in import_to_excel in script.py
"""


def transform_df(df, file_name):
    df_list = []
    fn_list = []
    EXCESS_AUTO = pd.DataFrame(columns=["start date", "end date"])
    AUTO = pd.DataFrame([])
    GEN = pd.DataFrame([])
    PROF = pd.DataFrame([])
    EXCESS_AUTO["start date"]
    if "Excess Auto Liab Total Incurred" in df.columns:
        EXCESS_AUTO["start_date"] = df["Effective Date"]
        EXCESS_AUTO["end_date"] = df["Expiration Date"]
        EXCESS_AUTO["incurred"] = df["Excess Auto Liab Total Incurred"]
        EXCESS_AUTO["number"] = df["Excess Auto Liab Number"]
        df_list.append(EXCESS_AUTO)
        fn_list.append(file_name + " (Excess Auto Liab)")
    if "Auto Liab Total Incurred" in df.columns:
        AUTO["start_date"] = df["Effective Date"]
        AUTO["end_date"] = df["Expiration Date"]
        AUTO["incurred"] = df["Auto Liab Total Incurred"]
        AUTO["number"] = df["Auto Liab Number"]
        df_list.append(AUTO)
        fn_list.append(file_name + " (Auto Liab)")
    if "Gen'l Liab Total Incurred" in df.columns:
        GEN["start_date"] = df["Effective Date"]
        GEN["end_date"] = df["Expiration Date"]
        GEN["incurred"] = df["Gen'l Liab Total Incurred"]
        GEN["number"] = df["Gen'l Liab Number"]
        df_list.append(GEN)
        fn_list.append(file_name + " (Gen'l Liab)")
    if "Professional Liab Total Incurred" in df.columns:
        PROF["start date"] = df["Effective Date"]
        PROF["end date"] = df["Expiration Date"]
        PROF["incurred"] = df["Professional Liab Total Incurred"]
        PROF["number"] = df["Professional Liab Number"]
        df_list.append(PROF)
        fn_list.append(file_name + " (Professional Liab)")
    return df_list, fn_list


def convert_to_df_multiclass(pdf, file_name):
    losses = PDFtoText(pdf)
    matches = match_start(losses)
    df = ExportDf(losses, matches)
    print(df)
    df_list, fn_list = transform_df(df, file_name)
    return df_list, fn_list
