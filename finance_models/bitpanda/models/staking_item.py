from dataclasses import dataclass, field
from finance_models.bitpanda.models import Transaction


@dataclass
class StakingItem(object):
    asset: str = field()
    rewards: list[Transaction] = field(default_factory=lambda: [])
    image_paths: list[tuple[list[str], list[str]]] = field(default_factory=lambda: [])

    def get_rewards_by_year_and_fiat_currency(self):
        for year in sorted(set([reward.time.year for reward in self.rewards])):
            rewards_by_year = [reward for reward in self.rewards if reward.time.year == year]
            for fiat_currency in sorted(set([reward.fiat_currency for reward in rewards_by_year])):
                rewards = [reward for reward in rewards_by_year if reward.fiat_currency == fiat_currency]
                yield year, rewards, fiat_currency
