import matplotlib.pyplot as plt
from src.etl.Loading_modelData import load_model_data
import matplotlib.dates as mdates
df = load_model_data()

# matplotlib can't plot Period directly; convert to datetime for x-axis
if str(df["month"].dtype).startswith("period"):
    x = df["month"].dt.to_timestamp()
else:
    x = df["month"]

plt.figure()
plt.plot(x, df["avg_hourly_earnings"])

plt.title("Average Hourly Earnings (Total Private)")
plt.xlabel("Year")
plt.ylabel("Dollars/hour")

# Force yearly ticks (every year)
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

ax.xaxis.set_minor_locator(mdates.MonthLocator())

plt.tight_layout()
plt.show()