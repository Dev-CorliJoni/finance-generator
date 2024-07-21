from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class YearlyReward(object):
    year: int = field()
    cumulative_amount: float = field()


@dataclass
class Reward(object):
    time: datetime = field()

    amount_fiat: float = field()
    tax_fiat: float = field()
    fiat_currency: str = field()

    amount_asset: float = field()

    asset_market_price: float = field()
    asset_market_price_currency: str = field()

    fee: float = field()
    fee_currency: str = field()

    spread: float = field()
    spread_currency: str = field()


@dataclass
class StakingItem(object):
    asset: str = field()
    # yearly_rewards: list[YearlyReward] = field(default_factory=lambda: []) remove if calculate with rewards
    rewards: list[Reward] = field(default_factory=lambda: [])
    image_paths: list[tuple[list[str], list[str]]] = field(default_factory=lambda: [])
