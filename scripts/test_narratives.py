import sys
sys.path.insert(0, ".")
import pandas as pd
from processing.cleaner import clean_dataframe
from processing.classifier import classify_dataframe
from insights.generator import generate_insights

df = pd.read_csv("data/samples/sample_consumer_tech.csv")
print(f"Raw records: {len(df)}")

df_clean = clean_dataframe(df)
print(f"After cleaning: {len(df_clean)}")

brands = ["Apple", "Lenovo", "HP", "Dell", "ASUS"]
df_proc = classify_dataframe(df_clean, "Consumer Tech India", brands)
print(f"After classify: {len(df_proc)}")

insights = generate_insights(df_proc, "Consumer Tech India", brands, ["laptop", "smartphone"])
narratives = insights.get("dominant_narratives", [])
print(f"\nNarratives generated: {len(narratives)}")

for i, n in enumerate(narratives):
    print(f"\n--- Narrative {i+1} ---")
    print(f"Keys: {list(n.keys())}")
    print(f"TREND: {n.get('trend', '')[:100]}")
    print(f"CONSUMER DRIVER: {n.get('consumer_driver', '')[:100]}")
    print(f"BUSINESS IMPLICATION: {n.get('business_implication', '')[:100]}")
    print(f"STRATEGIC ACTION (generic): {n.get('strategic_action', '')[:100]}")
    brand_actions = n.get("brand_actions", {})
    print(f"Brand actions available for: {list(brand_actions.keys())}")
    for brand in brands:
        action = brand_actions.get(brand, "MISSING")
        print(f"  [{brand}]: {action[:90]}")

print("\nPASS: narrative structure is correct" if all(
    "brand_actions" in n and isinstance(n["brand_actions"], dict)
    for n in narratives
) else "FAIL: brand_actions missing or wrong type")
