# UET Economic Health Index

## Traditional vs UET Ranking

### Traditional GDP Ranking
```
Rank by: Total GDP or GDP per capita
Problem: Ignores debt, inequality, sustainability
```

### UET Health Index (k)
```
k = sqrt(Productivity / Debt_Ratio) × Employment_Factor

Where:
- Productivity = GDP_per_capita / Cost_of_Living
- Debt_Ratio = (Private_Debt + Gov_Debt) / GDP
- Employment_Factor = 1 - Unemployment_Rate

Interpretation:
- k > 1.5: Very Healthy (sustainable growth)
- k = 1.0: Balanced (equilibrium)  
- k < 0.7: Stressed (unsustainable)
- k < 0.3: Crisis (collapse risk)
```

## Example Calculation
```python
# Thailand 2023 (estimated)
gdp_per_capita = 7000  # USD
cost_of_living = 800   # USD/month
productivity = 7000 / (800*12)  # = 0.73

private_debt_gdp = 0.90  # 90%
gov_debt_gdp = 0.62      # 62%
debt_ratio = 0.90 + 0.62  # = 1.52

unemployment = 0.01  # 1%
employment_factor = 0.99

k = sqrt(0.73 / 1.52) * 0.99
k = 0.69  # Stressed but stable
```
