import requests
import re

# Local server base URL
BASE_URL = "http://192.168.1.102:5000"
MOVE_URL = f"{BASE_URL}/move"
GAME_URL = f"{BASE_URL}/game"

# The move sequence you found
moves = "ddddddddddddddssaassddssddddddssaassddssddddwwaawwddddwwwwddddssssddddddssssdddddssssssss"

SESSION_COOKIE = "PASTE_YOUR_LOCAL_SESSION_COOKIE_HERE"

def main():
    s = requests.Session()

    # Make it look browser-like
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/game",
    })

    s.cookies.set("session", SESSION_COOKIE)

    # Send moves
    for i, direction in enumerate(moves, start=1):
        resp = s.post(MOVE_URL, data={"direction": direction})
        print(f"[{i}] Sent move: {direction} | Status: {resp.status_code}")

        # Check if flag appears mid-way
        if "RCSC{" in resp.text:
            print("Flag found in /move response!")
            m = re.search(r"RCSC\{.*?\}", resp.text)
            if m:
                print("Flag:", m.group(0))
            else:
                print(resp.text)
            return

    # After all moves, check /game
    final_resp = s.get(GAME_URL)
    print("\nFinal /game response:")
    print(final_resp.text)

    m = re.search(r"RCSC\{.*?\}", final_resp.text)
    if m:
        print("\nFlag:", m.group(0))
    else:
        print("\nFlag pattern not found. Check the HTML above manually.")

if __name__ == "__main__":
    main()
