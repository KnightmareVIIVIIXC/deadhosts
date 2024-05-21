import requests
import os
import time
from colorama import init, Fore, Style

# Explicitly initialize Colorama
init()

def is_domain_dead(domain, api_url):
    """Check if the given domain is dead using the specified API."""
    payload = {'domains': domain}
    try:
        response = requests.get(api_url, params=payload, timeout=10)
        if response.status_code == 200:
            # Assuming API returns JSON with a status for each domain
            data = response.json()
            # Check the status for 'dead' or 'alive'
            return data.get(domain, {}).get('status') == 'dead', data.get(domain, {}).get('status')
        else:
            return True, 'unknown'  # Treat non-200 responses as dead domains with unknown status
    except requests.RequestException:
        return True, 'error'  # Treat exceptions as dead domains with error status

def scan_file_for_dead_domains(file_path, api_url, delay=1):
    """Scan the specified file for dead domains and write results to 'dead_domains.txt'."""
    dead_domains = []
    with open(file_path, 'r') as file:
        for line in file:
            domain = line.strip()
            if domain and not domain.startswith('#'):  # Ignore empty lines and comments
                print(f"Checking domain: {domain}")
                dead, status = is_domain_dead(domain, api_url)
                if dead:
                    print(f"{Fore.BLUE}Dead domain found: {domain}{Style.RESET_ALL}")
                    dead_domains.append(domain)
                elif status == 'alive':
                    print(f"{Fore.GREEN}Domain {domain} is alive.{Style.RESET_ALL}")
                elif status == 'unknown':
                    print(f"{Fore.YELLOW}Status of domain {domain} is unknown.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Error occurred while checking domain {domain}.{Style.RESET_ALL}")
                time.sleep(delay)  # Add delay between requests to not overwhelm the server

    # Save the dead domains to a file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_file_path = os.path.join(script_dir, 'dead_domains.txt')
    with open(result_file_path, 'w') as result_file:
        for dead_domain in dead_domains:
            result_file.write(dead_domain + '\n')

    print(f"Scan complete. Dead domains have been written to '{result_file_path}'.")

# Define the API URL
api_url = 'https://urlfilter.adtidy.org/v2/checkDomains?filter=none'
# Define the path to the file to scan
file_path = './aiofirebog.txt'
# Define the delay between requests (in seconds)
delay_between_requests = 1

scan_file_for_dead_domains(file_path, api_url, delay_between_requests)

# Prompt the user to press any key to exit
input("Press any key to exit...")
