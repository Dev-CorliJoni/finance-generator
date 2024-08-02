import requests


def get(crypto_id, fiat_currencies=("usd", "eur", "gbp")):
    crypto_id = {
        "MATIC": "matic-network",
        "ETH": "ethereum",
        "BTC": "bitcoin",
        "DODGE": "dogecoin",
        "BEST": "bitpanda-ecosystem-token",
        #  other coins - tether,binancecoin,cardano,xrp,dogecoin,polkadot,solana,chainlink
    }.get(crypto_id, crypto_id)

    currencies = ','.join(fiat_currencies)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currencies}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if crypto_id in data:
            return data[crypto_id]
    return {}
