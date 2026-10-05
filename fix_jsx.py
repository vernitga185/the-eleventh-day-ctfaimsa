with open('cybersecurity-event-frontend/app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "'The Archive of Drona Parva is open. State inconsistencies have been detected within the ledgers of Yudhishthira's host. Specifically, look into the Wheel Guardians and the status of Sudakshina. Retrieve the original unedited text, discover the conflicting edits, and trace the parser versions responsible.'",
    '"The Archive of Drona Parva is open. State inconsistencies have been detected within the ledgers of Yudhishthira\\'s host. Specifically, look into the Wheel Guardians and the status of Sudakshina. Retrieve the original unedited text, discover the conflicting edits, and trace the parser versions responsible."'
)

with open('cybersecurity-event-frontend/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
