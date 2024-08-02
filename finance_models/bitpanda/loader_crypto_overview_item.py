from math import isnan
from finance_models.bitpanda.crypto_price import get as get_crypto_price
from finance_models.bitpanda.models import CryptoOverviewItem, Transaction, CalcAssetItem


def load_crypto_overview_item(df):
    inventory = CryptoOverviewItem.Inventory()
    profits = CryptoOverviewItem.Profits()
    costs = CryptoOverviewItem.Costs()

    crypto_overview_item = CryptoOverviewItem(inventory, profits, costs)

    load_asset_items(df, crypto_overview_item)
    print(list(get_inventory(crypto_overview_item)))
    list(get_profits(crypto_overview_item))


def load_asset_items(df, crypto_overview_item):
    filtered_df = df[
        (
                (df["Transaction Type"] == "withdrawal") |
                (df["Transaction Type"] == "buy") |
                (df["Transaction Type"] == "sell") |
                (df["Transaction Type"] == "reward") |
                (df["Transaction Type"] == "transfer")
        )
        &
        (df["Asset class"] == "Cryptocurrency")
        ]

    for asset in filtered_df["Asset"].unique():
        crypto_overview_item.asset_items[asset] = []

        for index, item in filtered_df[filtered_df["Asset"] == asset].iterrows():
            crypto_overview_item.asset_items[asset].append(Transaction.create(item))


def asset_items_iterator(func):
    def wrapper(crypto_overview_item):
        for asset in crypto_overview_item.asset_items.keys():
            yield func(asset, crypto_overview_item.asset_items[asset])

    return wrapper


@asset_items_iterator
def get_inventory(asset, asset_items):
    asset_inventory = 0

    for asset_item in asset_items:
        if asset_item.type not in ("transfer", ):
            if asset_item.type == "buy" or asset_item.type == "reward":
                asset_inventory += asset_item.amount_asset
            elif asset_item.type == "sell" or asset_item.type == "withdrawal":
                asset_inventory -= asset_item.amount_asset if not isnan(asset_item.amount_asset) else 0

            if asset_item.fee_asset == asset:
                asset_inventory -= asset_item.fee if not isnan(asset_item.fee) else 0

    return asset, asset_inventory, get_crypto_price(asset)


def _get_asset_items_by_type_groups(asset_items, type_groups):
    for type_group in type_groups:
        yield sorted([CalcAssetItem(i) for i in asset_items if i.type in type_group], key=lambda i: i.item.time)


@asset_items_iterator
def get_profits(asset, asset_items):
    type_groups = [("buy", "reward"), ("sell", "withdrawal", "transfer")]
    incoming, processing_items = tuple(_get_asset_items_by_type_groups(asset_items, type_groups))

    asset_log = f"\n{asset}\n\n"

    for processing_item in processing_items:
        incoming_filtered = [i for i in incoming if i.is_other_item_older(processing_item)]

        for incoming_item in incoming_filtered:
            log = ""

            if processing_item.is_sell_type():
                log, profit, payed_tax, is_taxable = incoming_item.sell(processing_item)

            elif processing_item.is_withdraw_type():
                log = ""

            elif processing_item.is_transfer_type() and incoming_item.is_buy_type():
                log = incoming_item.transfer(processing_item)

            asset_log += log

            if processing_item.is_processed():
                break

    print(asset_log)
