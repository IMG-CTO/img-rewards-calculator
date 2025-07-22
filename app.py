from flask import Flask, request, render_template
import requests
import redis
import os

app = Flask(__name__)

# --- Determine environment: Use Redis on Render, DummyCache locally ---
USE_REDIS = "RENDER" in os.environ

if USE_REDIS:
    cache = redis.Redis.from_url("redis://red-d1vsou6r433s73814dqg:6379")
else:
    class DummyCache:
        def get(self, key): return None
        def setex(self, key, time, value): pass
    cache = DummyCache()

# --- CoinGecko contract address for $IMG ---
IMG_CONTRACT = "znv3Ft2FHFAvzYF5LxzVyyvh3mBXuLTRRng2SgEZAjh"

# --- Fallbacks for calculations only ---
FALLBACK_SUPPLY = 998_568_158
FALLBACK_SOL = 201.22

def get_img_total_supply():
    cached = cache.get("img_total_supply")
    if cached:
        return float(cached)

    url = f"https://api.coingecko.com/api/v3/coins/solana/contract/{IMG_CONTRACT}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        supply = float(data["market_data"]["circulating_supply"])
        cache.setex("img_total_supply", 300, supply)  # Cache for 5 min
        return supply
    except Exception:
        return 998_968_783  # Fallback value used in calculations and shown in UI


def get_sol_price():
    cached = cache.get("sol_price")
    if cached:
        return float(cached)

    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        price = float(data["solana"]["usd"])
        cache.setex("sol_price", 300, price)  # Cache for 5 min
        return price
    except Exception:
        return None

@app.route("/", methods=["GET", "POST"])
def calculator():
    # Default form values
    volume = 100_000
    img_holdings = 1_000_000

    if request.method == "POST":
        volume = float(request.form.get("volume", "0").replace(",", "") or volume)
        img_holdings = float(request.form.get("img_holdings", "0").replace(",", "") or img_holdings)

    # Live or fallback data
    total_supply = get_img_total_supply()
    sol_price = get_sol_price()

    # Fallback logic
    total_supply_for_math = total_supply if total_supply is not None else FALLBACK_SUPPLY
    sol_price_for_math = sol_price if sol_price is not None else FALLBACK_SOL
    solana_per_usd = 1 / sol_price_for_math

    # Calculations
    gross_pool = 0.05 * volume
    infra_wallet = 0.10 * gross_pool
    daily_rewards_pool = gross_pool - infra_wallet

    user_share = img_holdings / total_supply_for_math
    daily_earnings = user_share * daily_rewards_pool
    monthly_projection = daily_earnings * 30
    annual_projection = daily_earnings * 365

    return render_template("index.html",
        volume=f"{volume:,.0f}",
        img_holdings=f"{img_holdings:,.0f}",
        daily_pool=f"{daily_rewards_pool:,.2f}" if sol_price_for_math else "Loading...",
        infra_wallet=f"{infra_wallet:,.2f}" if sol_price_for_math else "Loading...",
        daily_earnings=f"{daily_earnings:,.2f}",
        daily_sol=f"{daily_earnings * solana_per_usd:,.6f}",
        monthly_projection=f"{monthly_projection:,.2f}" if sol_price_for_math else "Loading...",
        monthly_sol=f"{monthly_projection * solana_per_usd:,.6f}",
        annual_projection=f"{annual_projection:,.2f}" if sol_price_for_math else "Loading...",
        annual_sol=f"{annual_projection * solana_per_usd:,.6f}",
        sol_price=f"{sol_price:,.2f}" if sol_price else "Loading...",
        total_supply=f"{total_supply:,.0f}"
    )

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
