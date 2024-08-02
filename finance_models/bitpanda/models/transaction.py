from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Transaction:
    id: str = field()
    time: datetime = field()

    type: str = field()
    in_out: str = field()
    asset_class: str = field()

    amount_fiat: float = field()
    fiat_currency: str = field()

    amount_asset: float = field()
    asset: str = field()

    asset_market_price: float = field()
    asset_market_price_currency: str = field()

    fee: float = field()
    fee_asset: str = field()

    spread: float = field()
    spread_currency: str = field()

    tax_fiat: float = field()

    @staticmethod
    def create(item):
        _args = {
            "id": item["Transaction ID"],
            "time": item["Timestamp"],
            "type": item["Transaction Type"],
            "in_out": item["In/Out"],
            "asset_class": item["Asset class"],
            "amount_fiat": item["Amount Fiat"],
            "fiat_currency": item["Fiat"],
            "amount_asset": item["Amount Asset"],
            "asset": item["Asset"],
            "fee": item["Fee"],
            "fee_asset": item["Fee asset"],
            "tax_fiat": item["Tax Fiat"],
            "spread": item["Spread"],
            "spread_currency": item["Spread Currency"],
            "asset_market_price": item["Asset market price"],
            "asset_market_price_currency": item["Asset market price currency"]
        }

        return Transaction(**_args)
