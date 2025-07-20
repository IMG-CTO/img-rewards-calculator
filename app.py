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
    # Default values (used both for GET and fallback)
    volume = 100_000
    img_holdings = 1_000_000

    # Override if POST values provided
    if request.method == "POST":
        volume = float(request.form.get("volume", volume))
        img_holdings = float(request.form.get("img_holdings", img_holdings))

    # Shared logic for GET or POST
    total_supply = get_img_total_supply()
    sol_price = get_sol_price()
    solana_per_usd = 1 / sol_price

    gross_pool = 0.05 * volume
    infra_wallet = 0.10 * gross_pool
    daily_rewards_pool = gross_pool - infra_wallet

    user_share = img_holdings / total_supply
    daily_earnings = user_share * daily_rewards_pool
    monthly_projection = daily_earnings * 30
    annual_projection = daily_earnings * 365

    return render_template("index.html",
                           volume=volume,
                           img_holdings=img_holdings,
                           daily_pool=f"{daily_rewards_pool:.2f}",
                           infra_wallet=f"{infra_wallet:.2f}",
                           daily_earnings=f"{daily_earnings:.2f}",
                           daily_sol=f"{daily_earnings * solana_per_usd:.6f}",
                           monthly_projection=f"{monthly_projection:.2f}",
                           monthly_sol=f"{monthly_projection * solana_per_usd:.6f}",
                           annual_projection=f"{annual_projection:.2f}",
                           annual_sol=f"{annual_projection * solana_per_usd:.6f}",
                           sol_price=f"{sol_price:.2f}",
                           total_supply="{:,.0f}".format(total_supply))

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")

