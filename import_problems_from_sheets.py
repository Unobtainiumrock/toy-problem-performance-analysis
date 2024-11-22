import gspread
import psycopg2
from psycopg2.extras import execute_values
import numpy as np
import os
import logging
from dotenv import load_dotenv

from helpers import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def connect_to_google_sheets(credentials_file, sheet_name):
    try:
        # Connect to Google Sheets
        gc = gspread.service_account(filename=credentials_file)
        ss = gc.open(sheet_name)
        logging.info("Successfully connected to the spreadsheet")
        return ss
    except Exception as e:
        logging.error(f"Failed to connect to Google Sheets: {e}")

def get_changed_rows(sheet):
    try:
        logging.info("Fetching changed row indices from the tracker sheet...")
        tracker_data = sheet.col_values(1)[1:] # Skip header
        
        if not tracker_data:
            logging.info("No changes detected. Exiting the script")
            exit(0)
        
        changed_rows = [int(row) for row in tracker_data]
        logging.info(f"Changed rows detected: {changed_rows}")
        changed_rows = np.unique(changed_rows)
        logging.info(f"Unique sorted changed rows: {changed_rows}") # np.unique sorts by default
        
        return changed_rows
    
    except ValueError as e:
        logging.error("Error parsing row indices from change tracker.")
        
        raise ValueError("Change tracker contains non-integer row indices.") from e

def connect_to_postgres(host, dbname, user, password):
    try:
        logging.info("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
        host="localhost",
        database="problem_tracker",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
        )
        logging.info("Successfully connected to PostgreSQL")
        return conn
    except Exception as e:
        logging.error("Failed to connect to PostgreSQL")
        
def fetch_data_ranges(sheet, grouped_ranges, column_start="A", column_end="K"):
    """
    Fetches data ranges from the Google Sheet based on grouped ranges.

    Args:
        sheet (gspread.Worksheet): The worksheet object to fetch data from.
        grouped_ranges (list of tuples): List of (start, end) row tuples representing the ranges.
        column_start (str): Starting column (default: "A").
        column_end (str): Ending column (default: "K").

    Returns:
        list: Data fetched from the specified ranges.
    """
    range_strings = []
    for start, end in grouped_ranges:
        if start == end:
            range_str = f"{column_start}{start}:{column_end}{start}"
        else:
            range_str = f"{column_start}{start}:{column_end}{end}"
        range_strings.append(range_str)

    logging.info(f"Batch ranges to fetch: {range_strings}")
    
    try:
        # Fetch all ranges in a single API call
        data_ranges = sheet.batch_get(range_strings)
        logging.info("Fetched data ranges from 'problems' sheet successfully.")
        return data_ranges
    except Exception as e:
        logging.error(f"Error fetching data ranges: {e}")
        raise
        
def main():
    logging.info("Starting the Google Sheets to PostgreSQL sync script.")

    # Load env variables
    load_dotenv()
    
    # Connect to Google Sheets
    ss = connect_to_google_sheets("credentials.json", "Toy Problem Performance")
    
    # Get changed rows
    problems_sheet = ss.worksheet("problems")
    tracker_sheet = ss.worksheet("change_tracker")
    
    logging.info("Accessed 'problems' and 'change_tracker' sheets.")
    
    
    changed_rows = get_changed_rows(tracker_sheet)
    
    if changed_rows.size == 0:
        return
    
    # Process fetched data
    grouped_ranges = group_consecutive_numbers(changed_rows)
    logging.info(f"Grouped changed rows into ranges: {grouped_ranges}")
    
    data_ranges = fetch_data_ranges(problems_sheet, grouped_ranges)
    logging.info("Successfully fetched data ranges from 'problems' sheet.")

    # Process fetched data
    rows_to_insert = []
    for (start_row, _), data_range in zip(grouped_ranges, data_ranges):
        for i, row_data in enumerate(data_range):
            row_index = start_row + i
            # Skip empty or invalid rows
            if row_index == 1 or not row_data or not any(cell.strip() for cell in row_data):
                logging.debug(f"Skipping invalid or empty row at index {row_index}.")
                continue
            # Ensure row_data has exactly 10 elements (excluding spreadsheet_row_id)
            row_data.extend([''] * (10 - len(row_data)))
            # Prepare the row for insertion (as a tuple)
            row_tuple = (
                row_index,                                                  # spreadsheet_row_id (this should always be valid)
                row_data[0] if row_data[0] else 'Unknown Problem',          # problem_name
                row_data[1] if row_data[1] else 'General',                  # problem_type
                row_data[2] if row_data[2] else 'medium',                   # difficulty_level
                row_data[3] if row_data[3] else 'https://www.google.com',   # problem_link
                row_data[4] if row_data[4] else 'https://www.google.com',   # problem_html_link
                int(row_data[5]) if row_data[5].isdigit() else 0,           # completion_time_minutes
                row_data[6] if row_data[6] else 'https://www.google.com',   # solution_link
                row_data[7] if row_data[7] else 'Unknown',                  # solution_runtime_complexity
                row_data[8] if row_data[8] else 'Unknown',                  # solution_space_complexity
                row_data[9] if row_data[9] else 'No explanation provided',  # complexity_explanation
                row_data[10] if row_data[10] else 0                         # found_optimal_solution
            )
            rows_to_insert.append(row_tuple)

    logging.info(f"Prepared {len(rows_to_insert)} rows for database insertion.")

    # Remove duplicates in rows_to_insert based on spreadsheet_row_id
    rows_to_insert = {row[0]: row for row in rows_to_insert}.values()

    # This next part defeats the purpose of leveraging fast computations via NumPy to some extent, but
    # we have to convert the rows_to_insert back to Python-native types,since psycopg2 doesn't support them.
    # I'm considering making a PR to psycopg2 to add this capability.

    rows_to_insert_native = [
        tuple(convert_to_native(value) for value in row) 
        for row in rows_to_insert
    ]

    logging.info(f"Final number of rows to insert: {len(rows_to_insert_native)}")

    try:
        # Create PostgreSQL connection
        logging.info("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            database="problem_tracker",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        logging.info("Successfully connected to PostgreSQL.")

        # Perform batch UPSERT
        if rows_to_insert:  # Only execute if there are rows to insert
            logging.info("Inserting/updating rows into the 'problems' table...")
            with conn.cursor() as cursor:
                execute_values(
                    cursor,
                    """
                    INSERT INTO problems (
                        spreadsheet_row_id, problem_name, problem_type, difficulty_level, 
                        problem_link, problem_html_link, completion_time_minutes, solution_link, 
                        solution_runtime_complexity, solution_space_complexity, complexity_explanation,
                        found_optimal_solution
                    ) VALUES %s
                    ON CONFLICT (spreadsheet_row_id) 
                    DO UPDATE SET 
                        problem_name = EXCLUDED.problem_name,
                        problem_type = EXCLUDED.problem_type,
                        difficulty_level = EXCLUDED.difficulty_level,
                        problem_link = EXCLUDED.problem_link,
                        problem_html_link = EXCLUDED.problem_html_link,
                        completion_time_minutes = EXCLUDED.completion_time_minutes,
                        solution_link = EXCLUDED.solution_link,
                        solution_runtime_complexity = EXCLUDED.solution_runtime_complexity,
                        solution_space_complexity = EXCLUDED.solution_space_complexity,
                        complexity_explanation = EXCLUDED.complexity_explanation,
                        found_optimal_solution = EXCLUDED.found_optimal_solution;
                    """,
                    rows_to_insert_native
                )
            conn.commit()
            logging.info("Rows successfully inserted/updated.")
        else:
            logging.info("No rows to insert. Skipping database update.")
            
    except Exception as e:
        print(f"Error occurred during database operation: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("PostgreSQL connection closed.")

    # Clear the change tracker sheet
    tracker_sheet.batch_clear(["A2:A"])  # Clear all data starting from row 2
    logging.info("Cleared change tracker sheet. Sync complete!")

main()
