import sys
import re

with open('cybersecurity-event-frontend/app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'Day XI.*?The Field of Kurukshetra', 'Archive Record: Drona Parva', content)
content = re.sub(r'Drona commands.*?battlefield intelligence', 'Archival Index / Integrity Check', content)
content = re.sub(r'Field log.*?XI / 18', 'Provenance Log', content)
content = re.sub(r'Kurukshetra.*?Day XI', 'Panchala Archives', content)

with open('cybersecurity-event-frontend/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
