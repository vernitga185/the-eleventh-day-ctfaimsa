import time, subprocess
while True:
    res = subprocess.run(['python', r'C:\Users\verni\.gemini\antigravity\brain\0b87cdb0-6b13-4661-8f47-27ece9285cdc\scratch\get_all_services.py'], capture_output=True, text=True)
    out = res.stdout
    status = ""
    for line in out.splitlines():
        if line.startswith("Satyajit-of-panchala |"):
            status = line.split(" | ")[2]
            break
    print(status)
    if status == "live":
        break
    time.sleep(10)
