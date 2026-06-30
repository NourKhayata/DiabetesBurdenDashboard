import pandas as pd
# https://www.kaggle.com/datasets/malaiarasugraj/global-health-statistics/data
df = pd.read_csv("Global Health Statistics.csv")

diabetes_df = df[df["Disease Name"] == "Diabetes"].copy()

diabetes_df.to_csv("diabetes_data.csv", index=False)

print("Saved diabetes_data.csv")
print(diabetes_df.shape)