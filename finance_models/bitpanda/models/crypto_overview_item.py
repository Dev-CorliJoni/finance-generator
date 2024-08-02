import datetime
from dataclasses import dataclass, field
from finance_models.bitpanda.models import Transaction


class LogMessages:

    @staticmethod
    def entry(out_item_name, in_item_name, out_item, in_item):
        return """
---- {out_item_name}(id={id1}, time={time1}) - Attempt to {o_name_s} crypto of this {in_item_name}(id={id2}, time={time2}) ----
""".format(o_name_s=out_item_name.lower(), id1=out_item.item.id, time1=out_item.item.time, out_item_name=out_item_name,
           id2=in_item.item.id, time2=in_item.item.time, in_item_name=in_item_name)

    @staticmethod
    def transfer_entry(transfer_item, buy_item):
        return LogMessages.entry("Transfer", "Buy", transfer_item, buy_item)

    @staticmethod
    def sell_entry(sell_item, buy_item):
        return LogMessages.entry("Sell", "Buy", sell_item, buy_item)

    @staticmethod
    def transfer_start(buy_item, transfer_item, **kwargs):
        return """
            Before Transaction:
            Buy Item: Available({calc_asset1}{asset1}, {calc_fiat1}{fiat1}) Staked({staked_asset1}{asset1}, {staked_fiat1}{fiat1})
            Transfer Item: TransferAmount({calc_asset2}{asset2}, In/Out: {inout}
            Percentage (Buy Available Amount / Transfer Amount): {p_in_n}

            Calculated Transfer Amount:
            Amount Asset: {amount_asset}{asset1}
            Amount Fiat: {amount_fiat}{fiat1}
            """.format(calc_asset1=buy_item.calculation_asset, asset1=buy_item.item.asset,
                       calc_fiat1=buy_item.calculation_fiat, fiat1=buy_item.item.fiat_currency,
                       staked_asset1=buy_item.staked_asset, staked_fiat1=buy_item.staked_fiat,
                       calc_asset2=transfer_item.calculation_asset, asset2=transfer_item.item.asset,
                       inout=transfer_item.item.in_out, **kwargs)

    @staticmethod
    def sell_start(buy_item, sell_item, **kwargs):
        return """
            Before Transaction:
            Buy Item: Available({calc_asset1}{asset1}, {calc_fiat1}{fiat1}) Staked({staked_asset1}{asset1}, {staked_fiat1}{fiat1})
            Sell Item: SellAmount({calc_asset2}{asset2}, {calc_fiat2}{fiat2})
            Percentage (Buy Available Amount / Sell Amount): {p_in}            
            Percentage (Sell Amount / Buy Available Amount): {p_out}
            """.format(calc_asset1=buy_item.calculation_asset, asset1=buy_item.item.asset,
                       calc_fiat1=buy_item.calculation_fiat,
                       staked_asset1=buy_item.staked_asset, staked_fiat1=buy_item.staked_fiat,
                       fiat1=buy_item.item.fiat_currency,
                       calc_asset2=sell_item.calculation_asset, asset2=sell_item.item.asset,
                       calc_fiat2=sell_item.calculation_fiat, fiat2=sell_item.item.fiat_currency, **kwargs)

    @staticmethod
    def transfer_end(buy_item, transfer_item, **kwargs):
        return """
            After Transaction:
            Buy Item: Available({calc_asset1}{asset1}, {calc_fiat1}{fiat1}) Staked({staked_asset1}{asset1}, {staked_fiat1}{fiat1})
            Transfer Item: TransferAmount({calc_asset2}{asset2})
            """.format(calc_asset1=buy_item.calculation_asset, asset1=buy_item.item.asset,
                       calc_fiat1=buy_item.calculation_fiat, fiat1=buy_item.item.fiat_currency,
                       staked_asset1=buy_item.staked_asset, staked_fiat1=buy_item.staked_fiat,
                       calc_asset2=transfer_item.calculation_asset, asset2=transfer_item.item.asset, **kwargs)

    @staticmethod
    def sell_end(buy_item, sell_item, **kwargs):
        return """
            Calculated:
            Buy Value: {buy_price}{fiat1}
            Sell Value: {sell_price}{fiat2}
            Taxes (payed): {payed_taxes}{fiat2} | Sell Taxable: {is_taxable}
            Profit: {profit}{fiat1}
            
            After Transaction:
            Buy Item: Available({calc_asset1}{asset1}, {calc_fiat1}{fiat1}) Staked({staked_asset1}{asset1}, {staked_fiat1}{fiat1})
            Sell Item: SellAmount({calc_asset2}{asset2}, {calc_fiat2}{fiat2})
            """.format(calc_asset1=buy_item.calculation_asset, asset1=buy_item.item.asset,
                       staked_asset1=buy_item.staked_asset, staked_fiat1=buy_item.staked_fiat,
                       calc_fiat1=buy_item.calculation_fiat,
                       calc_asset2=sell_item.calculation_asset, asset2=sell_item.item.asset,
                       calc_fiat2=sell_item.calculation_fiat,
                       fiat1=buy_item.item.fiat_currency, fiat2=sell_item.item.fiat_currency, **kwargs)


def _get_percentage_of(base_item, percentage_item):
    return min(1 / (base_item / percentage_item), 1)


class CalcAssetItem:

    def __init__(self, incoming_item):
        self.item = incoming_item

        self.staked_asset = self.item.amount_asset if self.is_rewards_type() else 0
        self.staked_fiat = self.item.amount_fiat if self.is_rewards_type() else 0

        self.calculation_asset = self.item.amount_asset
        self.calculation_fiat = self.item.amount_fiat

        self.calculation_asset -= self.staked_asset
        self.calculation_fiat -= self.staked_fiat

    @property
    def asset_value(self):
        return self.item.amount_asset

    @property
    def fiat_value(self):
        return self.item.amount_fiat

    def is_other_item_older(self, other_item):
        return self.item.time < other_item.item.time

    def is_buy_type(self):
        return self.item.type == "buy"

    def is_sell_type(self):
        return self.item.type == "sell"

    def is_withdraw_type(self):
        return self.item.type == "withdrawal"

    def is_rewards_type(self):
        return self.item.type == "reward"

    def is_transfer_type(self):
        return self.item.type == "transfer"

    def is_incoming(self):
        return self.item.in_out == "incoming"

    def is_outgoing(self):
        return self.item.in_out == "outgoing"

    def is_processed(self):
        return self.calculation_asset == 0

    def transfer(self, transfer_item):
        if (self.calculation_asset <= 0 and transfer_item.is_outgoing() or
                self.staked_asset <= 0 and transfer_item.is_incoming()):
            return ""

        log = LogMessages.transfer_entry(transfer_item, self)

        if transfer_item.is_outgoing():
            log = self.transfer_outgoing(transfer_item, log)
        elif transfer_item.is_incoming():
            log = self.transfer_incoming(transfer_item, log)

        return log

    def transfer_outgoing(self, transfer_item, log):
        percentage_buy_item = _get_percentage_of(self.calculation_asset, transfer_item.calculation_asset)
        amount = self.calculation_asset * percentage_buy_item
        amount_fiat = self.calculation_fiat * percentage_buy_item

        log += LogMessages.transfer_start(self, transfer_item, p_in_n=percentage_buy_item, amount_asset=amount,
                                          amount_fiat=amount_fiat)

        self.staked_asset += amount
        self.staked_fiat += amount_fiat
        self.calculation_asset -= amount
        self.calculation_fiat -= amount_fiat
        transfer_item.calculation_asset -= amount

        return log + LogMessages.transfer_end(self, transfer_item, p_in_n=percentage_buy_item, amount_asset=amount,
                                              amount_fiat=amount_fiat)

    def transfer_incoming(self, transfer_item, log):
        percentage_buy_item = _get_percentage_of(self.staked_asset, transfer_item.calculation_asset)
        amount = self.staked_asset * percentage_buy_item
        amount_fiat = self.staked_fiat * percentage_buy_item

        log += LogMessages.transfer_start(self, transfer_item, p_in_n=percentage_buy_item, amount_asset=amount,
                                          amount_fiat=amount_fiat)

        self.staked_asset -= amount
        self.staked_fiat -= amount_fiat
        self.calculation_asset += amount
        self.calculation_fiat += amount_fiat
        transfer_item.calculation_asset -= amount

        return log + LogMessages.transfer_end(self, transfer_item, p_in_n=percentage_buy_item, amount_asset=amount,
                                              amount_fiat=amount_fiat)

    def sell(self, sell_item):
        if self.calculation_asset <= 0:
            return "", 0, 0, False

        log = LogMessages.sell_entry(sell_item, self)

        sell_percentage_outgoing_item = _get_percentage_of(sell_item.calculation_asset, self.calculation_asset)
        sell_percentage_income_item = _get_percentage_of(self.calculation_asset, sell_item.calculation_asset)

        log += LogMessages.sell_start(self, sell_item, p_in=sell_percentage_income_item,
                                      p_out=sell_percentage_outgoing_item)

        buy_price = self.calculation_fiat * sell_percentage_income_item
        sell_price = sell_item.calculation_fiat * sell_percentage_outgoing_item
        payed_taxes = sell_item.item.tax_fiat * sell_percentage_outgoing_item
        profit = sell_price - buy_price

        is_taxable = False
        if self.item.time + datetime.timedelta(days=360) >= sell_item.item.time:  # Include the 10 years rule
            is_taxable = True

        sell_item.calculation_fiat -= sell_price
        sell_item.calculation_asset -= sell_item.calculation_asset * sell_percentage_outgoing_item

        self.calculation_fiat -= buy_price
        self.calculation_asset -= self.calculation_asset * sell_percentage_income_item

        log += LogMessages.sell_end(self, sell_item, buy_price=buy_price, sell_price=sell_price,
                                    payed_taxes=payed_taxes, is_taxable=is_taxable, profit=profit)
        return log, profit, payed_taxes, is_taxable

    def __hash__(self):
        return hash(self.item)

    def __eq__(self, other):
        if isinstance(other, CalcAssetItem):
            return self.item == other.item
        return False


@dataclass
class CryptoOverviewItem:
    @dataclass
    class Inventory:
        inventory_course_image_path: str = field(default="")

    @dataclass
    class Profits:
        pass

    @dataclass
    class Costs:
        pass

    inventory: Inventory = field(default_factory=Inventory)
    profits: Profits = field(default_factory=Profits)
    costs: Costs = field(default_factory=Costs)

    asset_items: dict[str: list[Transaction]] = field(default_factory=dict)
