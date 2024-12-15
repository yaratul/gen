import requests
import concurrent.futures
from colorama import Fore, init

init(autoreset=True)

def check_proxy(proxy):
    """
    Checks if the proxy is live or dead.
    Proxy format: ip:port or ip:port:username:password
    """
    try:
        parts = proxy.strip().split(':')
        if len(parts) == 2:  # No authentication
            ip, port = parts
            proxy_dict = {
                'http': f'http://{ip}:{port}',
                'https': f'http://{ip}:{port}'
            }
        elif len(parts) == 4:  # With authentication
            ip, port, username, password = parts
            proxy_dict = {
                'http': f'http://{username}:{password}@{ip}:{port}',
                'https': f'http://{username}:{password}@{ip}:{port}'
            }
        else:
            raise ValueError("Invalid proxy format")

        # Test URLs
        test_urls = [
            'http://www.google.com',
            'http://www.example.com'
        ]

        for url in test_urls:
            response = requests.get(url, proxies=proxy_dict, timeout=10)
            if response.status_code == 200:
                return f"[LIVE] {proxy}"
    except Exception:
        return f"[DEAD] {proxy}"
    return None

def validate_proxies(proxies):
    """
    Validates a list of proxies using threading.
    """
    live_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_proxy, proxies))
    for result in results:
        if result and "[LIVE]" in result:
            live_proxies.append(result)
    return live_proxies
