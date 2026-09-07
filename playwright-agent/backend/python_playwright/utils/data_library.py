import os
import openpyxl

def read_excel_data(excel_file_name):
    """
    Reads excel data from the 'data' directory.
    Skips the header row (row 1) and returns a list of lists representing row data.
    """
    if not excel_file_name:
        return []
    
    # Locate data folder relative to project workspace
    # Since this file is in python_playwright/utils/data_library.py, 
    # the workspace root is 3 levels up.
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(os.path.dirname(utils_dir))
    file_path = os.path.join(workspace_dir, "data", f"{excel_file_name}.xlsx")
    
    if not os.path.exists(file_path):
        # Fallback to current working directory 'data' folder
        file_path = os.path.join(os.getcwd(), "data", f"{excel_file_name}.xlsx")
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file '{excel_file_name}.xlsx' not found at: {file_path}")
        
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
    data = []
    
    # Iterate rows and skip the header (row 1)
    for row in list(sheet.iter_rows(values_only=True))[1:]:
        # Filter out empty rows
        if any(cell is not None for cell in row):
            # Format all cells as string to mimic Java's DataFormatter
            formatted_row = [str(cell).strip() if cell is not None else "" for cell in row]
            data.append(formatted_row)
            
    return data
