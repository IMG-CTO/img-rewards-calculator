# 💰 IMG Rewards Calculator

A web-based calculator that estimates $IMG token holder rewards based on live market data and user holdings. Built with Flask and deployed on Render, it uses real-time data from CoinGecko and supports fallback logic for reliability.

---

## 🔧 System Overview

- **Framework:** Flask (Python)
- **Hosting:** Render
- **Template Engine:** Jinja2 (`index.html`)
- **Cache Layer:** Redis
- **Live Price Feeds:** CoinGecko API  
  - Retrieves $IMG circulating supply  
  - Retrieves current SOL/USD price

---

## 🧠 Calculator Logic (`app.py`)

### Caching Setup:
- Checks if hosted on Render (`"RENDER"` in environment).
- Uses Redis (`redis.Redis.from_url(...)`) on Render.
- Uses in-memory dummy cache for local development.

### Default Values:
- `volume`: 100,000 USD  
- `img_holdings`: 1,000,000 IMG

### Data Fetching Functions:
- **`get_img_total_supply()`**
  - Attempts to retrieve $IMG circulating supply from CoinGecko.
  - Caches response for 5 minutes.
  - If request fails, uses fallback value: `998,968,783`.
  
- **`get_sol_price()`**
  - Fetches current SOL/USD price.
  - Caches response for 5 minutes.
  - If request fails, defaults to: `201.22`.

### Math Logic:
- **Rewards Pool Calculation:**
  - Gross pool = `5%` of daily volume.
  - `10%` of the pool goes to the Infra Wallet.
  - Remaining `90%` is distributed to IMG holders based on their holdings.

- **Earnings Projection:**
  - Based on user’s proportional share of the total supply.
  - Daily, Monthly, and Annual earnings calculated.
  - All USD values are converted to SOL using the current or fallback SOL price.

### Display Logic:
- Values formatted with commas and precision:
  - `{:,.2f}` for USD
  - `{:,.6f}` for SOL
- Fallback values are used in math but never shown in the frontend.
- If the SOL price is unavailable, the UI displays “Loading…” for USD-dependent fields.

---

## 💻 User Interface Behavior (`index.html`)

### User Inputs:
- **24H Volume in USD**
- **IMG Token Holdings**

### Behavior:
- Form auto-formats numbers with commas.
- Submitting the form POSTs data to `/`.
- On calculation, results display:
  - Rewards Pool (90%)
  - InfraWallet (10%)
  - Daily, Monthly, Annual earnings (USD + SOL)
  - Total IMG Supply
  - Live CoinGecko footnote with SOL price and IMG supply




