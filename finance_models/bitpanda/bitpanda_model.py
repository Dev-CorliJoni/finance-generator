import pandas as pd
from datetime import datetime
import pytz


class BitpandaModel:

    def __init__(self, csv_path):
        self._path = csv_path

        with open(self._path, "r") as f:
            lines = f.readlines()

        self.name, self.birthdate = [d.replace("\n", "").replace("\"", "") for d in lines[1].split(', ')]
        self.email = lines[2].replace("\n", "")
        self.account_opened_at = lines[3].split(': ')[1].replace("\n", "")
        self.crypto_market = lines[4].split(': ')[1].replace(" ", "").replace("\n", "").replace("\"", "")

        # convert to datetime
        self.birthdate = datetime.strptime(self.birthdate, "%Y-%m-%d")
        self.account_opened_at = datetime.strptime(self.account_opened_at, '%Y-%m-%dT%H:%M:%S%z\"')

        # load dataframe
        self._df = pd.read_csv(csv_path, delimiter=',', skiprows=6)

        # remove '-'
        for c in self._df.columns:
            self._df[c] = self._df[c].apply(lambda x: None if x == '-' else x)

        # Change db types
        self._df['Timestamp'] = pd.to_datetime(self._df['Timestamp'], utc=True)

        self._df['Fee'] = pd.to_numeric(self._df['Fee'])
        self._df['Spread'] = pd.to_numeric(self._df['Spread'])
        self._df['Tax Fiat'] = pd.to_numeric(self._df['Tax Fiat'])
        self._df['Product ID'] = pd.to_numeric(self._df['Product ID'])
        self._df['Amount Asset'] = pd.to_numeric(self._df['Amount Asset'])
        self._df['Asset market price'] = pd.to_numeric(self._df['Asset market price'])

    def to_html(self):
        return ""
