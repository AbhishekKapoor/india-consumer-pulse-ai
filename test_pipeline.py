"""Quick pipeline smoke test — run with: python test_pipeline.py"""
from scrapers.apify_scraper import scrape_data
from processing.cleaner import clean_dataframe
from processing.classifier import classify_dataframe
from insights.generator import generate_insights, generate_report_markdown

keywords = ["AI laptops", "premium laptops"]
brands = ["Apple", "Lenovo", "HP", "Dell", "ASUS", "Acer"]

print("1. Scrape (sample data)...")
df_raw = scrape_data(["Sample Data"], keywords, brands, "2026-04-01", "2026-05-10", "consumer_tech")
print(f"   Got {len(df_raw)} records. Columns: {list(df_raw.columns)}")

print("2. Clean...")
df_clean = clean_dataframe(df_raw)
print(f"   After cleaning: {len(df_clean)} records")

print("3. Classify (keyword fallback — no OpenRouter key)...")
df_proc = classify_dataframe(df_clean, "Consumer Tech India", brands)
print(f"   Classified {len(df_proc)} records")
print(f"   Sentiment breakdown: {df_proc['sentiment'].value_counts().to_dict()}")
print(f"   Top 3 themes: {df_proc['theme'].value_counts().head(3).to_dict()}")
pain_points = df_proc['pain_point'].dropna().tolist()
print(f"   Pain points detected: {len(pain_points)}")

print("4. Generate insights (template fallback — no OpenRouter key)...")
config = {"category": "Consumer Tech India", "keywords": keywords,
          "brands": brands, "source": "Sample Data", "timestamp": "2026-05-10 12:00"}
insights = generate_insights(df_proc, "Consumer Tech India", brands, keywords)
print(f"   Executive summary: {len(insights['executive_summary'])} chars")
print(f"   Narratives: {len(insights['dominant_narratives'])}")
print(f"   Recommendations: {len(insights['strategic_recommendations'])}")

print("5. Generate markdown report...")
report = generate_report_markdown(df_raw, df_proc, insights, config)
print(f"   Report: {len(report)} chars, {report.count(chr(10))} lines")

print()
print("Pipeline end-to-end: PASSED")
print("Run the dashboard with:  C:\\icpai_venv\\Scripts\\streamlit run app.py")
