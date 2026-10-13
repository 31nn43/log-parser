DDP Logs Script Usage Guide
Authored by: Minna Gaafar

Script: ddp_script.py

1.1. Purpose
A Python script used to search through log files (including gzipped .gz files) for specific patterns or search terms within a specified time range. It supports both AND and OR search modes to filter log entries effectively, case-sensitive searching, exclude filters, regex-based searches, and automatically handles time zone offsets in log timestamps.

1.2. Prerequisites
Python installed on your system.

Log files located in the same directory as the script or provide the path.

Log files must have timestamps in the format:
YYYY-MM-DDTHH:MM:SS.sss[+HH:MM or -HH:MM]

(e.g., 2025-08-05T12:15:00.000+02:00 or without offset 2025-08-05T12:45:00.000)

1.3. How To Use
Place the script (ddp_script.py) in the directory where your log files are located or provide the full path to the log files when running the script, and make sure you change directories in command prompt/terminal to the same one.

1.3.1. Command Line Usage
Bash
python ddp_script.py [--and] [--case-sensitive] [--regex] <inputfile> <outputfile> <start_time> <end_time> <search1> <search2> ... [--exclude term1 term2 ...]
FLAGS AND ARGUMENTS:

--and (optional): Use AND logic to only match lines containing all search terms.

--case-sensitive (optional): Match terms exactly as written (default is case-insensitive).

--regex (optional): Treat search terms as regular expressions.

<inputfile>: Name or path of the input log file (supports .gz files).

<outputfile>: Name or path of the output file where results will be saved.

<start_time>: Start timestamp in ISO format (YYYY-MM-DDTHH:MM:SS.sss+00:00).

<end_time>: End timestamp in ISO format (YYYY-MM-DDTHH:MM:SS.sss+00:00).

<search1> <search2> ...: One or more search terms (variable number of search terms).

--exclude term1 term2 ... (optional): Exclude lines containing these terms.

1.3.2. Examples
1.3.2.1. OR Mode (Default)
Search for lines containing any of the terms "error" or "fail" between two timestamps:

Bash
python ddp_script.py file.log output.txt 2024-01-01T00:00:00.000+00:00 2024-01-02T00:00:00.000+00:00 error fail
1.3.2.2. AND Mode
Search for lines containing only both "error" and "database" between two timestamps:

Bash
python ddp_script.py --and file.log output.txt 2024-01-01T00:00:00.000+00:00 2024-01-02T00:00:00.000+00:00 error database
To use this mode you must include the --and flag after calling the script.

1.3.2.3. CASE-SENSITIVE Search
Match the exact case for "ERROR":

Bash
python ddp_script.py --case-sensitive file.log output.txt 2024-01-01T00:00:00.000+00:00 2024-01-02T00:00:00.000+00:00 ERROR
1.3.2.4. EXCLUDE Terms
Find "error" but skip lines with "User" or "Debug":

Bash
python ddp_script.py file.log output.txt 2024-01-01T00:00:00.000+00:00 2024-01-02T00:00:00.000+00:00 error --exclude User Debug
1.3.2.5. CASE-SENSITIVE and EXCLUDE Terms Joint Search
Match "ERROR" exactly, skipping lines containing "User":

Bash
python ddp_script.py --case-sensitive file.log output.txt 2024-01-01T00:00:00.000+00:00 2024-01-02T00:00:00.000+00:00 ERROR --exclude User
1.3.2.6. REGEX Mode
Use regex patterns to match more complex searches. Search for lines that contain either a date in August 2025 or any WARN/ERROR message, using regex:

Bash
python ddp_script.py --regex file.log output.txt 2025-08-01T00:00:00.000+00:00 2025-08-31T23:59:59.999+00:00 "2025-08-\d{2}" "WARN|ERROR"
In PowerShell, enclose regex in quotes. In Command Prompt, quotes are optional unless your regex contains spaces or special characters.

1.4. Script BehaviorThe script appends the search results to the output file with a timestamp header indicating when the search was performed.It processes each line in the log file, extracts the timestamp, converts time zone offsets to UTC for accurate comparison, and assumes UTC if no offset is provided.Lines matching the search are written to the output file with their line number.Supports both case-insensitive search (default) and case-sensitive search.Excludes lines containing terms listed after --exclude.Can handle both plain text and gzipped log files.1.5. Error HandlingThe script will exit if:No search terms are provided.The input file does not exist.The timestamp format is incorrect.Not enough arguments are provided.1.6. NotesEnsure the timestamps in your log files match the expected ISO format at the start of each line in the log files.Timestamps without a time zone offset are assumed to be UTC (00:00).Timestamps with offsets are automatically converted to UTC for comparison.The output file will accumulate results from multiple runs if using the same output file unless cleared manually.The script assumes the log file is UTF-8 encoded.Ensure that search terms with spaces included are placed between quotations, e.g., "critical error".Regex Mode: When using --regex, search terms are treated as full regular expressions. In PowerShell, enclose search terms in quotes to prevent misinterpretation (e.g., --regex "ERROR.*Database"). In CMD, quotes are optional unless the regex contains spaces or special characters.1.6.1. Note on Regex (Regular Expressions)Regex is a text-matching tool that allows searching for patterns instead of exact words. You can match letters, digits, symbols, or complex patterns. For example:\d{2} → matches any two digitsERROR|WARN → matches ERROR or WARN2025-08-\d{2} → matches any date in August 2025Always put regex patterns in quotes when using PowerShell to avoid the shell interpreting special characters.Regex works in combination with the script's AND/OR logic, case sensitivity, and exclude filters for flexible searches.1.6.2. Regex Reference GuideSymbol / PatternMeaningExample.Any single character except newlinea.b → matches acb, a1b\dDigit (0-9)\d{4} → matches 2025\DNon-digit\D+ → matches Error\wWord character (letter, digit, _)\w+ → matches User_123\WNon-word character\W → matches !, .\sWhitespace (space, tab)\s+ → matches\SNon-whitespace\S+ → matches ERROR:^Start of line^2025 → matches lines starting with 2025$End of lineerror$ → matches lines ending with error*0 or more of previousa* → matches "", a, aa+1 or more of previousa+ → matches a, aa?0 or 1 of previous (optional)colou?r → matches color or colour{n}Exactly n repetitions\d{2} → matches 12{n,m}Between n and m repetitions\d{2,4} → matches 12, 123, 1234[]Any character in set[aeiou] → matches a, e, i[^]Any character NOT in set[^0-9] → matches letters|OR operator()Grouping(ERROR)(?=.*TERM)Lookahead (AND logic)(?=.*error)(?=.*database) → lines with both words\Escape special character\. → matches literal .