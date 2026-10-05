import sys

with open('cybersecurity-event-frontend/app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Starter Message
content = content.replace(
    'The eleventh day begins. Drona has taken command, and every signal carries intent. The battlefield record is built from reports and dispatches sent from the field. Some reports describe events; others are used to amend what has already been recorded. Investigate the reports, dispatches, and amendments to understand how the record is maintained.',
    "The Archive of Drona Parva is open. State inconsistencies have been detected within the ledgers of Yudhishthira's host. Specifically, look into the Wheel Guardians and the status of Sudakshina. Retrieve the original unedited text, discover the conflicting edits, and trace the parser versions responsible."
)

# Header Changes
content = content.replace('Day XI A The Field of Kurukshetra', 'Archive Record: Drona Parva')
content = content.replace('Drona commands A battlefield intelligence', 'Archival Index // Integrity Check')
content = content.replace('Field log A XI / 18', 'Provenance Log')

# Center Body Changes
content = content.replace('Kurukshetra A Day XI', 'Panchala Archives')
content = content.replace('The field is listening.', 'The Ledger of Satyajit')
content = content.replace('Read the formations, signals, and hidden intelligence of the eleventh day.', 'Query the canonical archive to uncover the lost provenance of the Wheel Guardians.')

# Prompt Buttons
content = content.replace('Who commands today?', 'Examine the Wheel Guardians')
content = content.replace('Map the formations', 'Query Sudakshina')
content = content.replace('Decode a battle signal', 'Check parser provenance')
content = content.replace('Search the archive...', 'Search the ledger...')

# Color Swaps (Gold -> Emerald/Teal)
content = content.replace('#c6944d', '#0d9488') # Main Teal
content = content.replace('#d8b477', '#5eead4') # Lighter Teal
content = content.replace('#e1b66f', '#14b8a6') # Hover Teal
content = content.replace('#a87943', '#0f766e') # Darker Teal

with open('cybersecurity-event-frontend/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated page.tsx")
