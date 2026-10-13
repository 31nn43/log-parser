#DDP LOGS SCRIPT
#Author: by Minna Gaafar

#Purpose: searches log files for specific patterns/search terms within a given time range
#Supports:
#       - Regular & gzipped log files
#       - AND / OR search modes
#       - Case-sensitive or case-insensitive search
#       - Excluding specific terms
#       - Regex search
#       - Handling timezone offsets in timestamps

# QUCIK COMMAND FLAGS
# Flag              | Description
# ------------------|-------------------------------------------------------------
# --and             | Require ALL search terms to appear (AND mode)
# --case-sensitive  | Match text exactly as typed (case-sensitive search)
# --exclude         | Terms to exclude from matches
# --regex           | Treat search terms as raw regex instead of literal strings
# --------------------------------------------------------------------------------
#


#====================================================================================================================================

import gzip
import re
import sys
import os
from datetime import datetime, timezone

# ---------------------------------------------------
# Convert timestamp string to UTC datetime object
# Supports:
#  - with timezone offset (e.g., +02:00)
#  - without timezone (assumes UTC)
# --------------------------------------------------

def get_timestamps(ts_str):
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S"
    ]
    for fmt in formats:
        try:
            ts = datetime.strptime(ts_str, fmt)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            else:
                ts = ts.astimezone(timezone.utc)
            return ts
        except ValueError:
            continue
    return None

#Define the function to find log errors with the input file and output file as args

# -----------------------------
# Main log search function
# -----------------------------


def find_log_searches(file, output, search_terms, start_time, end_time, and_mode = False, case_sensitive = False, exclude_terms = None, regex_mode = False):


    #Search log files for specific patterns within a given time range,using AND or OR logic.

    #Args:
    #file : Path to/ name of input log file (supports .gz compression)
    #output : Path to/ name ofoutput results file
    #search : List of search terms (variable number)
    #start_time : ISO format start timestamp
    #end_time : ISO format end timestamp
    #and_mode: bool for AND vs OR search
    #case_sensitive (bool): True for exact match case
    #regex_mode (bool): interpret search terms as regex expressions if True
    #exclude_terms (list): Words/phrases to exclude


    #File must be in the same directory the script is in
    print("Searching file in current working directory:", os.getcwd())

    if not search_terms:
        print("At least 1 search term is required.")
        sys.exit(1)


    exclude_terms = exclude_terms or []

    flags = 0 if case_sensitive else re.IGNORECASE

    try:
        #Compile include pattern
        if regex_mode:
            if and_mode:
                #Build a regex with multiple lookaheads (?=.*TERM) so all terms must appear
                include_pattern = re.compile(''.join(f'(?=.*{term})' for term in search_terms), flags)
            else:
                #Join terms with "|" (OR operator) so any of them can match
                include_pattern = re.compile('|'.join(search_terms), flags)
        else:
            #Same as above, but escape() used so terms are treated literally (not regex)
            if and_mode:
                include_pattern = re.compile(''.join(f'(?=.*{re.escape(term)})' for term in search_terms), flags)
            else:
                #OR mode, literal terms
                include_pattern = re.compile('|'.join(map(re.escape, search_terms)), flags)
    except re.error as e:
        print(f"Error compiling regex")
        sys.exit(1)


    #Build exclude pattern if provided
    exclude_pattern = re.compile('|'.join(re.escape(term) for term in exclude_terms), flags) if exclude_terms else None


    #Parse and validate input timestamps
    start_date = get_timestamps(start_time)
    if not start_date:
        print(f"Invalid start timestamp: {start_time}")
        sys.exit(1)

    end_date = get_timestamps(end_time)
    if not end_date:
        print(f"Invalid end timestamp: {end_time}")
        sys.exit(1)

    if not start_date or not end_date:
        print("Format must be YYYY-MM-DDTHH:MM:SS.sss or with +00:00 timestamp") #####################################
        sys.exit(1)

    if start_date > end_date:
        print("Error: Start time must be before end time")
        sys.exit(1)


    #File opening function that determines how to open the file based on the extension
    opening_files = gzip.open if file.endswith('.gz') else open


    #Process the files
    with opening_files(file,'rt', encoding='utf-8', errors='ignore') as infile, \
            open(output, 'a', encoding='utf-8') as outfile:

        count = 0  #track number of matches found
        current_entry = "" #accumulate mulit-line log entry
        current_line_number = 0

        #Process each line with line numbers starting from 1
        for line_num, line in enumerate(infile, 1):
            if re.match(r'^\s*\d{4}-\d{2}-\d{2}T', line):
                if current_entry:
                    #Extract the timestamp from the line
                    ts_match = re.match(r'^\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:[+-]\d{2}:\d{2})?)', current_entry)

                    if ts_match:
                        ts_str = ts_match.group(1)
                        ts = get_timestamps(ts_str) #Convert timestamp to datetime object
                        #Check if the timestamp falls within the user inputted range
                        if ts and start_date <= ts <= end_date:
                            include_match = include_pattern.search(current_entry) is not None
                            exclude_match = exclude_pattern and exclude_pattern.search(current_entry) is not None
                            #If pattern.search(line): #check if the line matches the search pattern

                            if include_match and not exclude_match:
                                if count == 0:
                                    outfile.write(f"\n--- New log search at {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n")
                                outfile.write(f"Line {current_line_number}: {current_entry}\n") #If so, write the matching line to output file
                                count +=1

                current_entry = line.rstrip('\n')
                current_line_number = line_num
            else:
                current_entry += '\n' + line.rstrip('\n')

        # Process the last entry
        if current_entry:
            ts_match = re.match(r'^\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:[+-]\d{2}:\d{2})?)', current_entry)
            if ts_match:
                ts_str = ts_match.group(1)
                ts = get_timestamps(ts_str)
                if ts and start_date <= ts <= end_date:
                    include_match = include_pattern.search(current_entry) is not None
                    exclude_match = exclude_pattern and exclude_pattern.search(current_entry) is not None
                    if include_match and not exclude_match:
                        if count == 0:
                            outfile.write(f"\n--- New log search at {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n")
                        outfile.write(f"Line {current_line_number}: {current_entry}\n")
                        count += 1


    print(f"\nSaved {count} matching lines to output file")



# -----------------------------
# Main script execution
# -----------------------------

if __name__ == "__main__":

    #Parse flags
    and_mode = "--and" in sys.argv
    if and_mode:
        sys.argv.remove("--and") #Remove the flag after to avoid messing up the arguments

    case_sensitive = "--case-sensitive" in sys.argv
    if case_sensitive:
        sys.argv.remove("--case-sensitive")


    if "--exclude" in sys.argv:
        idx = sys.argv.index("--exclude")
        if idx + 1 >= len(sys.argv):  # no terms provided
            print("Error: '--exclude' flag provided but no terms specified.")
            sys.exit(1)
        exclude_terms = sys.argv[idx + 1:] #Take everything after the "--exclude" as the search terms to exclude
        sys.argv = sys.argv[:idx]#Arguements to validate are all before the index
    else:
        exclude_terms = []



    regex_mode = "--regex" in sys.argv
    if regex_mode:
        sys.argv.remove("--regex")




    #Argument validation
    if len(sys.argv) < 6:
        print("Correct usage:")
        print("python ddp_script.py [--and] [--case-sensitive] [--regex] <inputfile> <outputfile> <start_time> <end_time> <searchterm1>...[--exclude term1 term2 ...]")
        sys.exit(1)



    file = sys.argv[1]
    output = sys.argv[2]
    start_time = sys.argv[3]
    end_time = sys.argv[4]
    search_terms = sys.argv[5:]

    #make sure the input file exists
    if not os.path.exists(file):
        print(f"File '{file}' not found!")
        sys.exit(1)


    #Call the log search function
    find_log_searches(file, output, search_terms, start_time, end_time, and_mode, case_sensitive, exclude_terms, regex_mode)