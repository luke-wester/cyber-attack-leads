import pandas as pd

def write_to_csv(data, filename="lead_list.csv"):
    df = pd.DataFrame(data)
    df.drop_duplicates(subset=["company", "name", "linkedin"], inplace=True)
    df.sort_values(by=["severity_score"], ascending=False, inplace=True)
    df.to_csv(filename, index=False)