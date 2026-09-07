import re

with open("C:\\Users\\SuriyaaP\\momentecautomation\\Momentec_Automation\\python_playwright\\tests\\page_source_logged_in.html", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.finditer(re.compile(r".{0,150}CATEGORIES.{0,150}", re.IGNORECASE), text)
for i, m in enumerate(matches):
    print(f"Match {i+1}:")
    print(m.group(0))
    print("-" * 50)
