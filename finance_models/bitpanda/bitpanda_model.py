import pandas as pd
from datetime import datetime

from finance_models.bitpanda.loader_staking_items import load_staking_items, generate_staking_files
from finance_models.finance_html_exporter import FinanceHTMLExporter


class BitpandaModel:

    def __init__(self, csv_path, start_date, end_date):
        self._path = csv_path

        self.start_date = pd.to_datetime(start_date, utc=True) if start_date is not None and start_date != "" else None
        self.end_date = pd.to_datetime(end_date, utc=True) if end_date is not None and end_date != "" else None

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

        self._df = self._df.sort_values(by='Timestamp')

        self._staking_items = list(load_staking_items(self._df, self.start_date, self.end_date))

        html_path = ".\\finance_models\\bitpanda\\html\\"

        self._bitpanda_exporter = FinanceHTMLExporter(f"{html_path}bitpanda_export.html")
        self._staking_item_exporter = FinanceHTMLExporter(f"{html_path}staking_item.html")
        self._staking_reward_item_exporter = FinanceHTMLExporter(f"{html_path}staking_reward_item.html")
        self._staking_image_exporter = FinanceHTMLExporter(f"{html_path}staking_image.html")
        self._staking_yearly_reward_exporter = FinanceHTMLExporter(f"{html_path}yearly_reward.html")

    def generate_files(self, export_folder):
        generate_staking_files(export_folder, self._df, self._staking_items, self.start_date, self.end_date)

    def to_html(self):
        staking_items_html = ""
        data = {key: value for key, value in self.__dict__.items() if not key.startswith("_")}

        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.strftime("%d %b %Y")

        for staking_item in self._staking_items:
            staking_item_args = {
                "asset_name": staking_item.asset,
                "yearly_rewards": "",
                "reward_items": "",
                "staking_images_noncumulative": "",
                "staking_images_cumulative": ""
            }

            for year, rewards, fiat_currency in staking_item.get_rewards_by_year_and_fiat_currency():
                staking_item_args["yearly_rewards"] += self._staking_yearly_reward_exporter.export_html(
                    amount_fiat=sum([r.amount_fiat for r in rewards]), fiat_currency=fiat_currency,
                    amount_asset=sum([r.amount_asset for r in rewards]), asset_currency=staking_item.asset, year=year
                )

            for reward in staking_item.rewards:
                staking_item_args["reward_items"] += self._staking_reward_item_exporter.export_html(
                    day=reward.time.strftime("%d %b %Y"), amount_fiat=reward.amount_fiat,
                    fiat_currency=reward.fiat_currency, amount_asset=reward.amount_asset,
                    asset_currency=staking_item.asset, asset_market_price=reward.asset_market_price,
                    asset_market_price_currency=reward.asset_market_price_currency, tax_fiat=reward.tax_fiat,
                    fee=reward.fee, fee_currency=reward.fee_currency, spread=reward.spread,
                    spread_currency=reward.spread_currency
                )

            for noncumulative_images, cumulative_images in staking_item.image_paths:
                for image in noncumulative_images:
                    html_part = self._staking_image_exporter.export_html(path=image)
                    staking_item_args["staking_images_noncumulative"] += html_part

                for image in cumulative_images:
                    html_part = self._staking_image_exporter.export_html(path=image)
                    staking_item_args["staking_images_cumulative"] += html_part

            staking_items_html = staking_items_html + self._staking_item_exporter.export_html(**staking_item_args)

        data["staking_items"] = staking_items_html
        return self._bitpanda_exporter.export_html(**data)
