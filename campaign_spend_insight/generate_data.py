import pandas as pd
import random

# Channel Distributions: (channel1, channel2, channel3)
channel_distributions = {
    "ads1": [0.10, 0.10, 0.80],
    "ads2": [0.20, 0.15, 0.65],
    "ads3": [0.05, 0.60, 0.35]
}

months = range(1, 13)
channels = ["channel1", "channel2", "channel3"]
rows = []

for ads, c_dist in channel_distributions.items():
    # Total annual spend for this campaign
    total_annual_spend = random.randint(120000, 600000)
    
    # Yearly weights for each month
    monthly_weights = []
    for month in months:
        if ads == "ads1": # Summer focused
            weight = 10 if month in [6, 7, 8] else 1
        elif ads == "ads2": # Holiday focused
            weight = 15 if month in [11, 12] else 1
        else: # ads3: Always on (Evenly distributed)
            weight = 1
        monthly_weights.append(weight)
    
    total_weight = sum(monthly_weights)
    
    for i, month in enumerate(months):
        monthly_spend = total_annual_spend * (monthly_weights[i] / total_weight)
        for j, channel in enumerate(channels):
            spend = monthly_spend * c_dist[j]
            rows.append({
                "campaign": ads,
                "month": month,
                "year": 2025,
                "channel": channel,
                "spend": round(spend, 2)
            })

df = pd.DataFrame(rows)
df.to_csv("campaign_spend.csv", index=False)
print("Updated campaign_spend.csv with monthly and seasonal data.")
