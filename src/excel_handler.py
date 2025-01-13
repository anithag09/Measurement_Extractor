import pandas as pd

def read_questions(excel_path):
    """Read questions from the Excel file."""
    try:
        df = pd.read_excel(excel_path)
        questions = []
        for index, row in df.iterrows():
            question = row.get('B', None)  # Column B contains questions
            if pd.notna(question):
                questions.append({"row": index, "question": question})
        return questions
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")

def write_answer(excel_path, row, answer):
    """Write the answer to the Excel file."""
    try:
        df = pd.read_excel(excel_path)
        df.at[row, 'C'] = answer  # Column C is for answers
        df.to_excel(excel_path, index=False)
    except Exception as e:
        raise ValueError(f"Error writing to Excel file: {e}")
