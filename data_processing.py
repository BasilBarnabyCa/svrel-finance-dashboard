import pandas as pd

def consolidate_excel_sheets_to_csv(excel_path, sheet_names, output_csv_path):
    consolidated_data = []

    for sheet in sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet, skiprows=2)  # Adjust skiprows as needed
        df = df[['Date', 'SALES']]  # Select only the columns you need, adjust column names as necessary
        df['Month'] = sheet  # Optional: Add a column for the month
        consolidated_data.append(df)

    # Combine all dataframes into a single dataframe
    consolidated_df = pd.concat(consolidated_data, ignore_index=True)

    # Data cleaning and organization
    consolidated_df['Date'] = pd.to_datetime(consolidated_df['Date'])
    consolidated_df['SALES'] = pd.to_numeric(consolidated_df['SALES'], errors='coerce')
    consolidated_df.dropna(subset=['SALES'], inplace=True)
    consolidated_df.sort_values(by='Date', inplace=True)

    # Save to CSV
    consolidated_df.to_csv(output_csv_path, index=False)

# If you want to run this script directly for testing or standalone use
if __name__ == "__main__":
    excel_path = 'data/spreadsheets/sales.xlsx'  # Update with the path to your Excel file
    sheet_names = ['July 2020', 'August 2020', 'Sept 2020']  # Add all relevant sheet names
    output_csv_path = 'data/csvs/sales_data.csv'
    consolidate_excel_sheets_to_csv(excel_path, sheet_names, output_csv_path)
