import datetime
from dataclasses import dataclass, field
from finance_models.bitpanda.models import Transaction


class LogMessages:

    @staticmethod
    def entry(out_item, in_item, out_item_name, out_item_verb=""):
        out_item_verb = out_item_verb if out_item_verb != "" else out_item_name.lower()
        return """
---- {out_item_name}(id={id1}, time={time1}) - Attempt to {o_name_s} this Crypto(id={id2}, time={time2}) ----
""".format(o_name_s=out_item_verb, id1=out_item.item.id, time1=out_item.item.time, out_item_name=out_item_name,
           id2=in_item.item.id, time2=in_item.item.time)

    @staticmethod
    def transfer_entry(transfer_item, crypto_item):
        return LogMessages.entry(transfer_item, crypto_item, "Transfer")

    @staticmethod
    def sell_entry(sell_item, crypto_item):
        return LogMessages.entry(sell_item, crypto_item, "Sell")

    @staticmethod
    def withdrawal_entry(withdrawal_item, crypto_item):
        return LogMessages.entry(withdrawal_item, crypto_item, "Withdrawal", "withdraw")

    @staticmethod
    def get_item_information(crypto_item, processing_item, processing_name):
        return ("""
            Crypto Item: Available({calc_asset1}{asset1}, {calc_fiat1}{fiat1}) Staked({staked_asset1}{asset1}, {staked_fiat1}{fiat1}) Withdrew({withdrew_asset1}{asset1}, {withdrew_fiat1}{fiat1})
            {processing_name} Item: Amount({calc_asset2}{asset2}, In/Out={inout})"""
                .format(calc_asset1=crypto_item.calculation_asset, calc_fiat1=crypto_item.calculation_fiat,
                        staked_asset1=crypto_item.staked_asset, staked_fiat1=crypto_item.staked_fiat,
                        withdrew_asset1=crypto_item.withdrew_asset, withdrew_fiat1=crypto_item.withdrew_fiat,
                        asset1=crypto_item.item.asset, fiat1=crypto_item.item.fiat_currency,
                        calc_asset2=processing_item.calculation_asset, asset2=processing_item.item.asset,
                        inout=processing_item.item.in_out, processing_name=processing_name))

    @staticmethod
    def send_start(crypto_item, processing_item, processing_name, **kwargs):
        return """
            Before Transaction:{item_information}
            Percentage (Crypto Available Amount / {processing_name} Amount): {p_in_n}

            Calculated affected Amount:
            Amount Asset:\t{amount_asset}{asset1}
            Amount Fiat:\t{amount_fiat}{fiat1}
            """.format(item_information=LogMessages.get_item_information(crypto_item, processing_item, processing_name),
                       fiat1=crypto_item.item.fiat_currency, asset1=crypto_item.item.asset,
                       processing_name=processing_name, **kwargs)

    @staticmethod
    def transfer_start(crypto_item, transfer_item, **kwargs):
        return LogMessages.send_start(crypto_item, transfer_item, "Transfer", **kwargs)

    @staticmethod
    def withdrawal_start(crypto_item, withdrawal_item, **kwargs):
        return """{start_info}Fee:\t\t\t{fee_asset}{asset1}
            Fee Fiat:\t\t{fee_fiat}{fiat1}
        """.format(**kwargs, fiat1=crypto_item.item.fiat_currency, asset1=crypto_item.item.asset,
                   start_info=LogMessages.send_start(crypto_item, withdrawal_item, "Withdrawal", **kwargs))

    @staticmethod
    def sell_start(crypto_item, sell_item, **kwargs):
        return """
            Before Transaction:{item_information}
            Percentage (Buy Available Amount / Sell Amount): {p_in}            
            Percentage (Sell Amount / Buy Available Amount): {p_out}
            """.format(item_information=LogMessages.get_item_information(crypto_item, sell_item, "Sell"), **kwargs)

    @staticmethod
    def end_item_update(crypto_item, processing_item, processing_name):
        return """
            After Transaction:{item_information}
                """.format(item_information=LogMessages.get_item_information(crypto_item, processing_item, processing_name))

    @staticmethod
    def transfer_end(crypto_item, transfer_item, **kwargs):
        return LogMessages.end_item_update(crypto_item, transfer_item, "Transfer")

    @staticmethod
    def withdrawal_end(crypto_item, withdrawal_item, **kwargs):
        return LogMessages.end_item_update(crypto_item, withdrawal_item, "Withdrawal")

    @staticmethod
    def sell_end(crypto_item, sell_item, **kwargs):
        return """
            Calculated:
            Buy Value:\t\t{buy_price}{fiat1}
            Sell Value:\t\t{sell_price}{fiat2}
            Taxes (payed):\t{payed_taxes}{fiat2} | Sell Taxable: {is_taxable}
            Profit:\t\t\t{profit}{fiat1}
            {end_item_update}
            """.format(end_item_update=LogMessages.end_item_update(crypto_item, sell_item, "Sell"),
                       fiat1=crypto_item.item.fiat_currency, fiat2=sell_item.item.fiat_currency, **kwargs)


def _get_percentage_of(base_item, percentage_item):
    return min(1 / (base_item / percentage_item), 1)


class CalcAssetItem:

    def __init__(self, incoming_item):
        self.item = incoming_item

        self.staked_asset = self.item.amount_asset if self.is_rewards_type() else 0
        self.staked_fiat = self.item.amount_fiat if self.is_rewards_type() else 0

        self.withdrew_asset = 0
        self.withdrew_fiat = 0

        self.payed_fee = 0

        self.calculation_asset = self.item.amount_asset
        self.calculation_asset = self.calculation_asset + self.item.fee if self.is_withdraw_type() else self.calculation_asset
        self.calculation_fiat = self.item.amount_fiat

        self.calculation_asset -= self.staked_asset
        self.calculation_fiat -= self.staked_fiat

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

    def is_other_item_older(self, other_item):
        return self.item.time < other_item.item.time

    @property
    def unpaid_fee(self):
        return self.item.fee - self.payed_fee

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
        percentage_crypto_item = _get_percentage_of(self.calculation_asset, transfer_item.calculation_asset)
        amount = self.calculation_asset * percentage_crypto_item
        amount_fiat = self.calculation_fiat * percentage_crypto_item

        log += LogMessages.transfer_start(self, transfer_item, p_in_n=percentage_crypto_item, amount_asset=amount,
                                          amount_fiat=amount_fiat)

        self.staked_asset += amount
        self.staked_fiat += amount_fiat
        self.calculation_asset -= amount
        self.calculation_fiat -= amount_fiat
        transfer_item.calculation_asset -= amount

        return log + LogMessages.transfer_end(self, transfer_item)

    def transfer_incoming(self, transfer_item, log):
        percentage_crypto_item = _get_percentage_of(self.staked_asset, transfer_item.calculation_asset)
        amount = self.staked_asset * percentage_crypto_item
        amount_fiat = self.staked_fiat * percentage_crypto_item

        log += LogMessages.transfer_start(self, transfer_item, p_in_n=percentage_crypto_item, amount_asset=amount,
                                          amount_fiat=amount_fiat)

        self.staked_asset -= amount
        self.staked_fiat -= amount_fiat
        self.calculation_asset += amount
        self.calculation_fiat += amount_fiat
        transfer_item.calculation_asset -= amount

        return log + LogMessages.transfer_end(self, transfer_item)

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

    def withdrawal(self, withdrawal_item):
        if (self.calculation_asset <= 0 and withdrawal_item.is_outgoing() or
                self.withdrew_asset <= 0 and withdrawal_item.is_incoming()):
            return ""

        log = LogMessages.withdrawal_entry(withdrawal_item, self)

        if withdrawal_item.is_outgoing():
            log = self.withdrawal_outgoing(withdrawal_item, log)
        elif withdrawal_item.is_incoming():
            log = self.withdrawal_incoming(withdrawal_item, log)

        return log

    def _withdrawal_base(self, crypto_amount, fiat_amount, withdrawal_item, log):
        percentage_crypto_item = _get_percentage_of(crypto_amount, withdrawal_item.calculation_asset)
        withdrew_asset = crypto_amount * percentage_crypto_item
        withdrew_fiat = fiat_amount * percentage_crypto_item

        percentage_without_fee = 1
        if withdrawal_item.calculation_asset - withdrew_asset < withdrawal_item.unpaid_fee:
            withdrawal_asset_without_fee = withdrawal_item.calculation_asset - withdrawal_item.unpaid_fee
            if withdrawal_asset_without_fee == 0:
                percentage_without_fee = 0
            else:
                percentage_without_fee = _get_percentage_of(withdrew_asset, withdrawal_asset_without_fee)

        withdrew_asset_without_fee = (withdrew_asset * percentage_without_fee)
        withdrew_fiat_without_fee = (withdrew_fiat * percentage_without_fee)

        fee_asset = withdrew_asset - withdrew_asset_without_fee
        fee_fiat = withdrew_fiat - withdrew_fiat_without_fee

        withdrawal_item.payed_fee += fee_asset
        withdrawal_item.calculation_asset -= withdrew_asset

        log += LogMessages.withdrawal_start(self, withdrawal_item, fee_asset=fee_asset, fee_fiat=fee_fiat,
                                            p_in_n=percentage_crypto_item, amount_asset=withdrew_asset, amount_fiat=withdrew_fiat)
        return withdrew_asset, withdrew_fiat, withdrew_asset_without_fee, withdrew_fiat_without_fee, fee_asset, log

    def withdrawal_outgoing(self, withdrawal_item, log):
        withdrawal_data = self._withdrawal_base(self.calculation_asset, self.calculation_fiat, withdrawal_item, log)
        amount, amount_fiat, withdrew_asset, withdrew_fiat, fee_asset, log = withdrawal_data

        self.withdrew_asset += withdrew_asset
        self.withdrew_fiat += withdrew_fiat
        self.calculation_asset -= amount
        self.calculation_fiat -= amount_fiat

        return log + LogMessages.withdrawal_end(self, withdrawal_item)

    def withdrawal_incoming(self, withdrawal_item, log):
        withdrawal_data = self._withdrawal_base(self.withdrew_asset, self.withdrew_fiat, withdrawal_item, log)
        amount, amount_fiat, withdrew_asset, withdrew_fiat, fee_asset, log = withdrawal_data

        self.withdrew_asset -= amount
        self.withdrew_fiat -= amount_fiat
        self.calculation_asset += withdrew_asset
        self.calculation_fiat += withdrew_fiat

        return log + LogMessages.transfer_end(self, withdrawal_item)

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
