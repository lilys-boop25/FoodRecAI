from pathlib import Path
import pandas as pd

def load_split_data(data_dir=None, train_file="train.jsonl", val_file="valid.jsonl", test_file="test.jsonl"):
    # If data_dir is not provided, use the current directory of this script as the default
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent
    else:
        data_dir = Path(data_dir)
    
    # Define paths for train, validation, and test files
    train_path = data_dir / train_file
    val_path = data_dir / val_file
    test_path = data_dir / test_file
    
    # Check if all three files exist
    for path in [train_path, val_path, test_path]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path.resolve()}")
            
    # Load the data from JSONL files into pandas DataFrames
    df_train = pd.read_json(train_path, lines=True)
    df_val = pd.read_json(val_path, lines=True)
    df_test = pd.read_json(test_path, lines=True)
    
    # Check the structure of each file
    for name, df in [("Train", df_train), ("Validation", df_val), ("Test", df_test)]:
        if 'content' not in df.columns or 'rating_label' not in df.columns:
            raise ValueError(f"File {name} must contain both 'content' and 'rating_label' columns")
            
    # Extract the features (X) and labels (y) for each split
    X_train = df_train['content'].astype(str)
    y_train = df_train['rating_label']
    
    X_val = df_val['content'].astype(str)
    y_val = df_val['rating_label']
    
    X_test = df_test['content'].astype(str)
    y_test = df_test['rating_label']
    
    return X_train, y_train, X_val, y_val, X_test, y_test
