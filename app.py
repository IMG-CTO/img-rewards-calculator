from flask import Flask, request, render_template
import requests

app = Flask(__name__)

# --- CoinGecko contract address for $IMG ---
IMG_CONTRACT = "znv3FZt2HFAvzYf5LxzVyryh3mBXWuTRRng25gEZAjh"

def get_img_total_supply():
    url = f"https://api.coingecko.com/api/v3/coins/solana/contract/{IMG_CONTRACT}"
    try:
        response = requests.get(url)
        data = response.json()
        supply = float(data["market_data"]["circulating_supply"])
        return supply
    except Exception:
        return 1_000_000_000  # fallback

def get_sol_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return float(data["solana"]["usd"])
    except Exception:
        return 141.13  # fallback

@app.route("/", methods=["GET", "POST"])
def calculator():
    daily_earnings = monthly_projection = daily_pool = solana_per_usd = 0
    img_holdings = volume = total_supply = 0

    if request.method == "POST":
        volume = float(request.form["volume"])
        img_holdings = float(request.form["img_holdings"])

        total_supply = get_img_total_supply()
        sol_price = get_sol_price()

        daily_pool = 0.05 * volume
        user_share = img_holdings / total_supply
        daily_earnings = user_share * daily_pool
        monthly_projection = daily_earnings * 30
        solana_per_usd = 1 / sol_price

        return render_template("index.html",
                               volume=volume,
                               img_holdings=img_holdings,
                               daily_pool=round(daily_pool, 2),
                               daily_earnings=round(daily_earnings, 2),
                               sol_earned=round(daily_earnings * solana_per_usd, 6),
                               monthly_projection=round(monthly_projection, 2),
                               monthly_sol=round(monthly_projection * solana_per_usd, 6),
                               sol_price=round(sol_price, 2),
                               total_supply="{:,.0f}".format(total_supply))

    return render_template("index.html", total_supply="Fetching...", sol_price="Fetching...")
