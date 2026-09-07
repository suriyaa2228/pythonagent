import sys
from bs4 import BeautifulSoup

def parse_report(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    fails = soup.find_all('div', class_='test-detail')
    for f in fails:
        badge = f.find('span', class_='status-badge')
        if badge and 'status-fail' in badge.get('class', []):
            title = f.find('h2', class_='test-title').text
            print(f'\\n--- {title} ---')
            for row in f.find_all('tr'):
                status_td = row.find('td')
                if status_td and status_td.find('span', class_='status-fail'):
                    tds = row.find_all('td')
                    if len(tds) > 2:
                        print(tds[2].text.strip())

if __name__ == '__main__':
    parse_report('../reports/extent_report_20260810_232013.html')
