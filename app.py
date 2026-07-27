import pandas as pd

# قراءة البيانات
df = pd.read_csv("yarn_quality_data.csv")

# تجميع البيانات حسب نمرة الخيط
summary = df.groupby("Yarn_Count").agg(
    Avg_Defects=("Defects", "mean"),
    Max_Defects=("Defects", "max"),
    Avg_Strength=("Strength", "mean"),
    Min_Strength=("Strength", "min"),
    Samples=("Yarn_Count", "count")
).reset_index()

# حساب مؤشر جودة بسيط
summary["Quality_Index"] = (
    (summary["Avg_Strength"] * 10)
    - summary["Avg_Defects"]
)

# تصنيف الجودة
def classify(row):
    if row["Quality_Index"] >= 190:
        return "ممتاز"
    elif row["Quality_Index"] >= 170:
        return "جيد"
    elif row["Quality_Index"] >= 150:
        return "مقبول"
    else:
        return "يحتاج تحسين"

summary["Quality_Rating"] = summary.apply(classify, axis=1)

print("\nنتائج تحليل نمر الخيط:\n")
print(summary)

# استنتاجات تلقائية
print("\nالاستنتاجات:\n")

for _, row in summary.iterrows():
    conclusion = f"""
نمرة {row['Yarn_Count']}:
- متوسط العيوب = {row['Avg_Defects']:.2f}
- متوسط قوة الشد = {row['Avg_Strength']:.2f}
- تقييم الجودة = {row['Quality_Rating']}
"""

    if row["Avg_Defects"] > 10:
        conclusion += "- يوجد ارتفاع في العيوب ويحتاج مراجعة مراحل الإنتاج.\n"

    if row["Avg_Strength"] < 19:
        conclusion += "- قوة الشد منخفضة وقد تشير إلى مشاكل في الضبط أو الخامات.\n"

    if row["Quality_Rating"] == "ممتاز":
        conclusion += "- الأداء مستقر ويحقق متطلبات الجودة.\n"

    print(conclusion)
