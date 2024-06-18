import pdfplumber
import re
import pandas as pd
import sys
import os

# Move to the folder of submissions, redefine path as you need
# Get the current working directory
current_directory = os.getcwd()

print(f'Current directory is: {current_directory}')

# # Define the target directory
# target_directory = "submissions"

# # Move the current file to the target directory
# os.rename(current_directory, target_directory)

# Print a success message
# print(f"Current directory moved to {target_directory}")

def PDFtoText(path_to_pdf: str):
    '''
    converts PDF to a string variable

    input: string
    output: string variable containing losses with labels from PDF
    '''
    # initiate text variable

    text = " "

    with pdfplumber.open(path_to_pdf) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
            # new = page.extract_text()
            # print(new)
            # text += new     

    # Find the index positions of 'LOSSES' and 'ADDITIONAL INFORMATION'
    losses_index = text.find('LOSSES')
    additional_info_index = text.find('ADDITIONAL INFORMATION')

    # Find the index position of 'LARGE LOSSES'
    large_losses_index = text.find('LARGE LOSSES')

    # Slice the string to get the portions after 'LOSSES' and 'ADDITIONAL INFORMATION'
    losses = text[losses_index + len('LOSSES'):large_losses_index] if losses_index != -1 else ''

    # Slice the string to get the parts after 'LARGE LOSSES'
    large_losses = text[large_losses_index + len('LARGE LOSSES'):additional_info_index] if large_losses_index != -1 else ''


    print("LOSSES:\n", losses)
    print("\nLARGE LOSSES:\n", large_losses)  

    return losses


    
def multiclass_count(text:str):
    '''
    Determines how many classes there are in the text.
    There are 4 classes in total: Gen'l Liab, Auto liab, Excess Auto Liab, and Professional Liab

    input: 
    string that contains the labels extracted from pdf

    outputs: 
    - count of how many unique claases there are (int)
    - names of the unique classes (list of strings)
    '''
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



def generate_patterns(num_classes: str):
    """
    Generate all possible regex patterns for missing data scenarios.
    Each class can have its 'incurred loss' or 'number of claims' missing, or both.

    Parameters:
    - num_classes (int): Number of categories of data.

    Returns:
    - List of compiled regex patterns (re.Pattern objects).
    """

    # base pattern is the date range
    base_pattern = r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4})"

    # money pattern is (total incurred, number)
    money_pattern = r"([$\d,]+|\$0|\S*) (\d+|0)"

    patterns = []


    # Create a template with placeholders for each class data
    template = [base_pattern] + ["{} {}"] * num_classes

    # Generate all combinations of data being present or set to '0'/'$0'
    for i in range(2 ** (num_classes * 2)):  # Each class has 2 fields, hence num_classes * 2 bits
        current_pattern = template[:]
        bits = f"{i:0{num_classes * 2}b}"  # binary representation of i with padding

        # Iterate over each class's two fields (incurred and number)
        for j in range(num_classes):
            incurred_index = 1 + 2 * j  # 1 for base_pattern offset, 2*j for previous fields
            number_index = incurred_index + 1
            while (1+2*j < num_classes):
                # Set incurred loss
                if bits[2 * j] == '0':  # Check bit for incurred loss
                    current_pattern[incurred_index] = "(0|\\$0)"
                else:
                    current_pattern[incurred_index] = "([\\$\\d,]+|\\$0|\\S*)"

                # Set number
                if bits[2 * j + 1] == '0':  # Check bit for number
                    current_pattern[number_index] = "0"
                else:
                    current_pattern[number_index] = "(\\d+|0)"

        # Join the pattern and compile it
        regex_pattern = " ".join(current_pattern)
        compiled_pattern = re.compile(regex_pattern)
        patterns.append(compiled_pattern)

    return patterns



def match_start(losses):
    '''
    Goes through all lines
    in the variables "lines" (losses without headers) and attemtps 
    to match each line to the default pattern. It then calls the function match_round2()

    inputs: 
    - losses: string
    '''
    # First round: Extracting data from the text

    num_classes, labels = multiclass_count(losses)

    matches = []

    if num_classes == 3:
        data_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)")
    elif num_classes == 4:
        data_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)")
    elif num_classes == 2:
        data_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)")

    # find matches
    try:
        # check if the var data_pattern is defined
        data_pattern

    except NameError: 
        # TODO: connect this to general cases script
        sys.exit("Round 1 data pattern not found. Could be due to \
                 (1) Table is single-column \
                 (2) There exist missing values (3) Unrecognized data type")
    
    else:
        # if data_pattern is defined, start matching
        matches = data_pattern.findall(losses)

        # check if any expected data is missing
        if not matches:
            print("No data captured. Please check the losses string format.")
        else:
            print("Captured Matches:")
            for match in matches:
                print(match)

            patterns = generate_patterns(num_classes)
                
            final_matches = match_round2(matches, losses, data_pattern, patterns)

    return final_matches


# TODO: Function to fill missing values
def fill_missing(default_match, missing_match):
    '''
    '''

    # default_match = default_pattern.search(text)
    # missing_match = missing_pattern.search(text)

    if not missing_match:
        return None  # No match found, cannot process

    group = missing_match.groups()

    filled_values = group.copy()

    for i, value in enumerate(missing_match.groups()):
        while (i+1 < len(group)) and (i-1 >= 0):
            # Number is 0, its incurred loss is missing
            if value == '0' and (not group[i-1].contains('$')):  
                filled_values.insert(i-1, '$0')  # Replace missing entries with '$0'

            # incurred loss is $0, number is missing
            # replace with '-'
            elif value =='$0' and (group[i+1] != 0) and (group[i+1].contains('$')):
                filled_values.insert(i+1,'-')
            else:
                continue

    return filled_values



def reformat(line, default_pattern, pattern:re.Pattern, matches:list, pattern_ind:int, line_ind:int):
    '''
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
    '''
    missing_pattern = pattern

    missing_match = missing_pattern.search(line)
    print(f"Reformatting... Current processing unmatched line: {missing_match}")
    
    # Extract the groups from the missed match
    groups = list(missing_match.groups())

    print(f"Current unmatched line number is {line_ind}.")
    print(f"Current unmatched line is {line}.")
    
    # Replace empty values with '0'
    # since we know the 2nd incurred is missing, 
    # add $0 in the position where the second total incurred value should be
    standardized_groups = groups.copy()

    # two ways to do this
    # (1) insert  without checking (faster)
    # check that the index 3 is 0 
    # insert "$0" at index 3

    if not missing_match:
        return None  # No match found, cannot process

    group = missing_match.groups()

    filled_values = group.copy()

    # TODO: test and add more cases
    for i, value in enumerate(missing_match.groups()):
        while (i+1 < len(group)) and (i-1 >= 0):
            # Number is 0, its incurred loss is missing
            if value == '0' and (not group[i-1].contains('$')):  
                filled_values.insert(i-1, '$0')  # Replace missing entries with '$0'
            # incurred loss is $0, number is missing
            # replace with '-'
            elif value =='$0' and (group[i+1] != 0) and (group[i+1].contains('$')):
                filled_values.insert(i+1,'-')
            else:
                continue

    if (len(filled_values) == len(default_pattern.groups())):
        matches.append(tuple(filled_values))

    return matches


def match_round2(matches, data_pattern, patterns):
    '''
    inputs:
    - matches: a list of matched lines after the first round
    - losses: loss run table
    - patterns: list of all possble data patterns (with missing values) based on num_classes

    outputs:
    - matches: a list of matched lines with newly appended unmatched lines
    '''
    # 2nd Round: check if there are rows that might not be captured by analyzing the text more closely

    # Generate all possible data patterns with missing values
    

    # remove first 4 rows of losses
    # Split the text into lines
    lines = losses.strip().split('\n')

    # Remove the first four lines
    lines = lines[4:]

    expected_rows = len(lines) 

    if len(matches) != expected_rows:
        print(f"Expected to capture {expected_rows} rows, but only captured {len(matches)}.")
        missing_rows_count = expected_rows - len(matches)
        print(f"Missing rows count: {missing_rows_count}")

        # track lines that weren't captured
        unmatched = []

        # Analyze each line, add all unmatched lines in the 1st round
        for index, line in enumerate(lines):
            if not data_pattern.search(line):
                unmatched.append((index, line))  

        print(unmatched)

        # Try alternative patterns to capture these lines, ADD DIFFERENT PATTERNS IF NEEDED
        for line_number, line in unmatched:
            for pattern in patterns:

            # # Pattern with the first incurred loss possibly missing
            # pattern1 = re.compile(r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)")

            # # Pattern with the second incurred loss possibly missing
            # pattern2 = re.compile(r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\$\d|\S*) (\d+|0) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0)")
                
            # # Pattern with the third incurred loss possibly missing
            # pattern3 = re.compile(r"(\d{2}/\d{2}/\d{4}-\d{2}/\d{2}/\d{4}) ([\$\d,]+|\$0|\$\d|\S*) (\d+|0) ([\$\d,]+|\$0|\$\d|0|\S*) (\d+|0) (\d+|0)")

            # if pattern1.search(line):
            #     print(f"Line {line_number} matches pattern1.")

            #     # call reformat to reformat this line, updates matches
            #     matches = reformat(line, pattern1, matches, 1, line_number)
                
            # elif pattern2.search(line):
            #     print(f"Line {line_number} matches pattern2.")

            #     matches = reformat(line, pattern2, matches, 2, line_number)

            # elif pattern3.search(line):
            #     print(f"Line {line_number} matches pattern3.")

            #     matches = reformat(line, pattern3, matches, 3, line_number)

                if pattern.search(line):
                    print(f'Line {line_number} macthed to a pattern.')

                    matches = reformat(line, losses, )
                else:
                    print(f"Line {line_number} does not match any known pattern.")
        else:
            print("All lines are successfully captured after second check.")

    else:
        print("All rows are successfully captured after second check.")
    
    return matches


def ExportDf(text, matches):
    '''
    Process the text string when there is more than one class.
    There are 4 classes in total: Gen'l Liab, Auto liab, Excess Auto Liab, and Professional Liab

    input: 
    - string that contains the text extracted from pdf

    output: 
    - standardized pandas dataframe (pd.dataframe)
    '''

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

    print(f'intialized df is: {df}')

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
        start_date, end_date = date_range.split('-')
        row_dict['Effective Date'] = start_date
        row_dict['Expiration Date'] = end_date
        row_dict['Evaluation Date'] = '05/07/2024'  # This should be taken from the text

        # Handle the data for each class
        match_index = 1  # Start after the date range
        for label in lst:
            row_dict[f"{label} Total Incurred"] = match[match_index]
            row_dict[f"{label} Number"] = match[match_index + 1]
            match_index += 2  # Move index to the next class

        rows.append(row_dict)

    # Initialize the DataFrame with the row data
    df = pd.DataFrame(rows, columns=column_names)

    print(f'Autopopulated df is {df}')

    return df
    


pdf = ".\multi\Evans.pdf"

losses = PDFtoText(pdf) 

matches = match_start(losses)

df = ExportDf(losses, matches)

