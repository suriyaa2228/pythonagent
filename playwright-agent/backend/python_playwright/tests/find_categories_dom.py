import re

with open("C:\\Users\\SuriyaaP\\momentecautomation\\Momentec_Automation\\python_playwright\\tests\\page_source_logged_in.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the exact occurrence of CATEGORIES that is not in a URL
import bs4
soup = bs4.BeautifulSoup(text, "html.parser")
elements = soup.find_all(string=re.compile(r"^\s*CATEGORIES\s*$", re.IGNORECASE))
for e in elements:
    parent = e.parent
    print(f"Parent tag: {parent.name}")
    print(f"Parent class: {parent.get('class')}")
    print(f"Parent id: {parent.get('id')}")
    print(f"Parent HTML: {str(parent)[:200]}")
    print("---------------------------------")
