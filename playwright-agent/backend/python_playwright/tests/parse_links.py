from bs4 import BeautifulSoup

with open("homepage_dump.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")
    
print("--- ALL VISIBLE LINKS ---")
for a in soup.find_all("a"):
    text = a.get_text(strip=True)
    if text:
        print(f"[{text}] -> {a.get('href')}")

