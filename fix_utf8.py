import sys

def fix_file(filename):
    try:
        # Read with utf-8, replace errors
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Replace the corrupted 'A' sequences with a clean dash or space
        content = content.replace('A', '—').replace('', '')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filename}")
    except Exception as e:
        print(f"Error on {filename}: {e}")

fix_file('cybersecurity-event-frontend/app/page.tsx')
fix_file('cybersecurity-event-frontend/app/eleventh-day/page.tsx')
