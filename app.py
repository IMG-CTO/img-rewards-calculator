from flask import Flask, request, render_template
import requests
import redis
import os

app = Flask(__name__)

# --- Redis setup: Use real Redis in Render, dummy locally ---
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
        return None  # Return None to trigger "Loading..."

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
        return 0  # fallback to avoid divide-by-zero

@app.route("/", methods=["GET", "POST"])
def calculator():
    volume = 100_000
    img_holdings = 1_000_000

    if request.method == "POST":
        volume = float(request.form.get("volume", "0").replace(",", "") or volume)
        img_holdings = float(request.form.get("img_holdings", "0").replace(",", "") or img_holdings)

    total_supply = get_img_total_supply()
    sol_price = get_sol_price()
    solana_per_usd = 1 / sol_price if sol_price else 0

    gross_pool = 0.05 * volume
    infra_wallet = 0.10 * gross_pool
    daily_rewards_pool = gross_pool - infra_wallet

    user_share = (img_holdings / total_supply) if total_supply else 0
    daily_earnings = user_share * daily_rewards_pool
    monthly_projection = daily_earnings * 30
    annual_projection = daily_earnings * 365

    return render_template("index.html",
        volume=f"{volume:,.0f}",
        img_holdings=f"{img_holdings:,.0f}",
        daily_pool=f"{daily_rewards_pool:,.2f}",
        infra_wallet=f"{infra_wallet:,.2f}",
        daily_earnings=f"{daily_earnings:,.2f}",
        daily_sol=f"{daily_earnings * solana_per_usd:,.6f}",
        monthly_projection=f"{monthly_projection:,.2f}",
        monthly_sol=f"{monthly_projection * solana_per_usd:,.6f}",
        annual_projection=f"{annual_projection:,.2f}",
        annual_sol=f"{annual_projection * solana_per_usd:,.6f}",
        sol_price=f"{sol_price:,.2f}" if sol_price else "Loading...",
        total_supply="Loading..." if total_supply is None else f"{total_supply:,.0f}"
    )

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
