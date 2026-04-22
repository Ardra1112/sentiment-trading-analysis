# =========================
# 1. Import Libraries
# =========================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ML part
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# =========================
# 2. Load Data
# =========================
trades = pd.read_csv("historical_data.csv")
sentiment = pd.read_csv("fear_greed_index.csv")

print("Trades Shape:", trades.shape)
print("Sentiment Shape:", sentiment.shape)

# =========================
# 3. Clean Column Names
# =========================
trades.columns = trades.columns.str.lower().str.strip()
sentiment.columns = sentiment.columns.str.lower().str.strip()

# =========================
# 4. Handle Time Column
# =========================
time_col = None
for col in trades.columns:
    if "time" in col:
        time_col = col
        break

trades[time_col] = pd.to_datetime(trades[time_col], errors='coerce')
trades["date"] = trades[time_col].dt.date

# =========================
# 5. Handle Sentiment Data
# =========================
date_col = None
for col in sentiment.columns:
    if "date" in col:
        date_col = col
        break

sentiment[date_col] = pd.to_datetime(sentiment[date_col], errors='coerce')
sentiment["date"] = sentiment[date_col].dt.date

# rename column
if "classification" in sentiment.columns:
    sentiment.rename(columns={"classification": "sentiment"}, inplace=True)

# =========================
# 6. Merge Data
# =========================
df = pd.merge(trades, sentiment[["date", "sentiment"]], on="date", how="left")
df = df.dropna(subset=["sentiment"])

print("Merged Data Shape:", df.shape)

# =========================
# 7. Find Important Columns
# =========================
pnl_col = None
for col in df.columns:
    if "pnl" in col:
        pnl_col = col
        break

df.rename(columns={pnl_col: "pnl"}, inplace=True)

# leverage (optional)
lev_col = None
for col in df.columns:
    if "leverage" in col:
        lev_col = col
        break

# =========================
# 8. Feature Engineering
# =========================
df["win"] = df["pnl"] > 0

# =========================
# 9. Basic Analysis
# =========================
avg_pnl = df.groupby("sentiment")["pnl"].mean()
win_rate = df.groupby("sentiment")["win"].mean()

print("\n=== ANALYSIS ===")
print("Average PnL:\n", avg_pnl)
print("\nWin Rate:\n", win_rate)

# =========================
# 10. Visualization
# =========================
plt.figure()
sns.barplot(x=avg_pnl.index, y=avg_pnl.values)
plt.title("Average PnL by Sentiment")
plt.show()

plt.figure()
sns.barplot(x=win_rate.index, y=win_rate.values)
plt.title("Win Rate by Sentiment")
plt.show()

# =========================
# 11. PnL Distribution
# =========================
plt.figure()
sns.boxplot(x="sentiment", y="pnl", data=df)
plt.title("PnL Distribution")
plt.show()

# =========================
# 12. Buy/Sell Behavior
# =========================
if "side" in df.columns:
    buy_sell = df.groupby(["sentiment", "side"]).size().unstack(fill_value=0)
    buy_sell.plot(kind="bar")
    plt.title("Buy vs Sell Behavior")
    plt.show()

# =========================
# 13. INSIGHTS
# =========================
print("\n=== INSIGHTS ===")

fear_pnl = avg_pnl.get("Fear", 0)
greed_pnl = avg_pnl.get("Greed", 0)

if fear_pnl > greed_pnl:
    print("Traders perform better during FEAR")
else:
    print("Traders perform better during GREED")

if win_rate.get("Fear", 0) > win_rate.get("Greed", 0):
    print("Higher win rate during FEAR")
else:
    print("Lower win rate during GREED")

# =========================
# 14. SIMPLE ML MODEL (AI PART)
# =========================

# Convert sentiment to number
df["sentiment_num"] = df["sentiment"].map({"Fear": 0, "Greed": 1})

features = ["sentiment_num"]

if lev_col:
    features.append(lev_col)

X = df[features]
y = df["win"]

# remove missing
X = X.dropna()
y = y.loc[X.index]

# split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# model
model = LogisticRegression()
model.fit(X_train, y_train)

# predict
pred = model.predict(X_test)

# accuracy
acc = accuracy_score(y_test, pred)

print("\n=== ML MODEL ===")
print("Prediction Accuracy:", round(acc * 100, 2), "%")

# =========================
# 15. STRATEGY
# =========================
print("\n=== STRATEGY ===")

if fear_pnl > greed_pnl:
    print("Consider trading during FEAR periods")
else:
    print("Consider trading during GREED")

print("Avoid high leverage and manage risk properly")