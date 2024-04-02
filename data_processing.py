import pandas as pd

def get_index_of_totals(df):
    # Locate the row with 'TOTAL' in the 'F' column, which indicates the total values
    return df.index[df.iloc[:, 5].str.contains('TOTAL', case=False, na=False)].tolist()

def consolidate_excel_sheets_to_csv(excel_path, output_csv_path):
    xls = pd.ExcelFile(excel_path)
    start_date = pd.to_datetime("2023-01-01")
    consolidated_data = []

    for sheet in xls.sheet_names:
        try:
            # Parse the sheet name into a date, if not possible, it will raise an error and continue
            sheet_date = pd.to_datetime(sheet, errors='raise', format='%B %Y')
            if sheet_date < start_date:
                continue  # Skip the sheets before January 2023
        except ValueError:
            continue  # Skip sheet names that do not represent a month and year
        
        df = pd.read_excel(excel_path, sheet_name=sheet)

        total_indices = get_index_of_totals(df)
        if len(total_indices) < 2:
            print(f"Not enough 'TOTAL' entries found in sheet: {sheet} - Found: {len(total_indices)}")
            continue

        # The index of the 'SALES' column should be 2 places after the 'F' column, which is index 5
        sales_index = 7
        purse_index = 8
        days_index = 6  # This assumes 'DAYS' is the column immediately after 'F' for simulcast

        # Create a dictionary for the row, ensuring to round values to 2 decimal places
        row = {
            'date': sheet_date.strftime('%B %Y'),
            'live_races_total': int(df.iloc[total_indices[0], days_index]),
            'live_race_sales': round(float(df.iloc[total_indices[0], sales_index]), 2),
            'live_race_purses': round(float(df.iloc[total_indices[0], purse_index]), 2),
            'simulcast_days_total': int(df.iloc[total_indices[1], days_index]),
            'simulcast_sales': round(float(df.iloc[total_indices[1], sales_index]), 2),
            'simulcast_average': round(float(df.iloc[total_indices[1], sales_index]) / int(df.iloc[total_indices[1], days_index]), 2),
        }
        consolidated_data.append(row)

    # Convert the list of dictionaries into a DataFrame
    consolidated_df = pd.DataFrame(consolidated_data)

    # Save the DataFrame to a CSV file
    consolidated_df.to_csv(output_csv_path, index=False)

def excel_to_csv_targets(excel_path, csv_path):
    # Read the target Excel file
    df_targets = pd.read_excel(excel_path)
    
    # Save to CSV
    df_targets.to_csv(csv_path, index=False)
    
# If you want to run this script as a standalone script for testing
if __name__ == "__main__":
    sales_excel_path = 'data/spreadsheets/sales.xlsx'
    sales_output_csv_path = 'data/csvs/sales.csv'
    targets_excel_path = 'data/spreadsheets/targets.xlsx'
    targets_output_csv_path = 'data/csvs/targets.csv'
    consolidate_excel_sheets_to_csv(sales_excel_path, sales_output_csv_path)
    excel_to_csv_targets(targets_excel_path, targets_output_csv_path)
