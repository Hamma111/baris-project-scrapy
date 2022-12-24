import pandas as pd


def store_data(data, file_name):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)

