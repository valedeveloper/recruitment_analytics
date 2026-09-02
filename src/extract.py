import pandas
def extract_file_to_csv(file):
    df=pandas.read_csv(file,sep=";")
    return df