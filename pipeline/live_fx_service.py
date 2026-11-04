"""
RetailPulse - Real-Time Macro FX (Foreign Exchange) Service
Integrates with the public Frankfurter API to fetch live currency conversion rates.
Normalizes multi-currency e-commerce sales into standard USD reporting currency.
"""

import json
import urllib.request
from datetime import datetime

# Backup / Baseline rates if offline or rate-limited
FALLBACK_RATES_FROM_USD = {
    "USD": 1.0,
    "BRL": 5.42,    # Brazilian Real
    "INR": 83.50,   # Indian Rupee
    "EUR": 0.92,    # Euro
    "GBP": 0.79     # British Pound
}

class LiveFXService:
    def __init__(self, base_currency="USD"):
        self.base_currency = base_currency
        self.rates = FALLBACK_RATES_FROM_USD.copy()
        self.last_updated = None
        self.is_live = False

    def fetch_live_rates(self):
        """Fetches latest real-time rates from Frankfurter API."""
        url = f"https://api.frankfurter.app/latest?from={self.base_currency}&to=INR,EUR,GBP"
        headers = {"User-Agent": "RetailPulse-Intelligence/1.0"}

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    live_rates = data.get("rates", {})
                    # Update cache
                    self.rates.update(live_rates)
                    self.rates[self.base_currency] = 1.0
                    self.last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                    self.is_live = True
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [LIVE FX] Successfully updated rates: {self.rates}")
                    return True
        except Exception as e:
            self.last_updated = f"Offline Fallback (Active: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')})"
            self.is_live = False
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [LIVE FX] API unavailable ({e}). Using cached rates.")
            return False

    def convert_to_usd(self, amount: float, from_currency: str) -> float:
        """Converts an order amount from local currency to USD."""
        curr = from_currency.upper()
        if curr == "USD":
            return round(amount, 2)
        
        rate = self.rates.get(curr, FALLBACK_RATES_FROM_USD.get(curr, 1.0))
        # Rate represents 1 USD = rate * CURR, so USD = amount / rate
        usd_value = amount / rate if rate > 0 else amount
        return round(usd_value, 2)

    def get_rate(self, currency: str) -> float:
        """Returns the conversion rate from USD to target currency."""
        return self.rates.get(currency.upper(), 1.0)


if __name__ == "__main__":
    fx = LiveFXService()
    print("Testing FX Service...")
    fx.fetch_live_rates()
    print("USD to INR:", fx.get_rate("INR"))
    sample_order_brl = 250.0  # 250 Brazilian Real
    sample_order_inr = 5000.0 # 5000 Indian Rupee
    print(f"R$ {sample_order_brl} BRL = ${fx.convert_to_usd(sample_order_brl, 'BRL')} USD")
    print(f"INR {sample_order_inr} = ${fx.convert_to_usd(sample_order_inr, 'INR')} USD")
