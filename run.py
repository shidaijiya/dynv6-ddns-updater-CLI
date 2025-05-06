import os
import sys
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
import argparse
import tempfile
import time
from pathlib import Path
import dns.resolver
import dns.resolver
import requests
from lib.log_utils import log_print
from lib.network_info import get_network_info, format_info
from lib.process_locker import process_does_not_exist
from lib.security import encrypt_token, decrypt_token



secrets_file_path = "ddns-secrets.bin"
LOCK_FILE = "dynv6-update.lock"
LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), LOCK_FILE)



def post_update_request(domain, token,ipv4_address = None, ipv6_address = None):
    if ipv4_address and ipv6_address:
        url = f'https://dynv6.com/api/update?hostname={domain}&ipv4={ipv4_address}&ipv6={ipv6_address}&token={token}'
    elif ipv4_address:
        url = f'https://dynv6.com/api/update?hostname={domain}&ipv4={ipv4_address}&token={token}'
    elif ipv6_address:
        url = f'https://dynv6.com/api/update?hostname={domain}&ipv6={ipv6_address}&token={token}'
    else:
        log_print("Missing IP address parameter", "WARNING")
        return False

    try:
        response = requests.get(url, proxies=None)
        if response.status_code == 200 and response.text == "addresses updated":
            log_print(f"IPv4:{ipv4_address}, IPv6:{ipv6_address} IP address updated!", "INFO")
            return True
        else:
            log_print(response.text, "WARNING")
            return False


    except Exception as e:
        log_print(f"Network request failed{e}","ERROR")
        return False



def dns_query(domain,rdtype):
    try:
        records = dns.resolver.resolve(domain, rdtype)
        record = records[0].to_text()
        log_print(f"DNS records for {domain} is {record}", "INFO")
        return records[0].to_text()
    except Exception as e:
        log_print(f"DNS query failed. Error:{e}", "ERROR")
        return False



def check_and_update(address_key, domain, token, address):
    config = {
        "ipv4": {"ip_type": "IPv4", "rdtype": "A"},
        "ipv6": {"ip_type": "IPv6", "rdtype": "AAAA"}
    }

    if not address:
        log_print(f"{config[address_key]['ip_type']}address doesn't exist，Skipping update", "WARNING")
        return

    log_print(f"Local IP:{address}", "INFO")

    dns_record = dns_query(domain, config[address_key]['rdtype'])
    if dns_record == address:
        log_print(f"{domain} {config[address_key]['ip_type']} DNS record matches local IP, No update needed.", "INFO")
        return
    elif not dns_record:
        log_print(f"{config[address_key]['ip_type']} DNS Query failed, forcing update", "INFO")

    elif dns_record != address:
        log_print(f"{domain} {config[address_key]['ip_type']} NS record does not match local IP. Updating...", "INFO")
    else:
        log_print(f"{config[address_key]['ip_type']} Unknown error occurred. Forcing update.", "INFO")

    max_retries = 3
    retry_count = 0
    update_resp = post_update_request(domain, token, **{f"{address_key}_address": address})

    if not update_resp:
        log_print(f"Retrying (Max retry{max_retries}rd)...", "WARNING")

        while retry_count < max_retries:
            time.sleep(10)
            retry_count += 1
            update_resp = post_update_request(domain, token, **{f"{address_key}_address": address})
            if update_resp:
                break
            log_print(f"Retry failed at {retry_count}rd", "WARNING")

        if not update_resp:
            log_print("Finally update failed", "ERROR")



# update_type 可选值ipv4, ipv6 ,both
def update_ddns_record(token,domain,update_type = "ipv6"):
    network_info = get_network_info()
    interface_name, ipv4, ipv6 = format_info(network_info)

    ipv4_address = ipv4[0] if ipv4 else None
    ipv6_address = ipv6[0] if ipv6 else None


    if update_type == "ipv4":
        check_and_update("ipv4", domain, token, ipv4_address)

    elif update_type == "ipv6":
        check_and_update("ipv6", domain, token, ipv6_address)

    elif update_type == "both":
        check_and_update("ipv4", domain, token, ipv4_address)
        check_and_update("ipv6", domain, token, ipv6_address)

    else:
        log_print(f"Unknown options", "ERROR")



def has_args(args):
    return any([
        args.conf_name, args.domain, args.token, args.update_type, args.update_interval
    ])



def main():
    parser = argparse.ArgumentParser(description="DDNS update script parameter")
    parser.add_argument('--conf_name', type=str, help="config name")
    parser.add_argument('--domain', type=str, help="Domain")
    parser.add_argument('--token', type=str, help="access token")
    parser.add_argument('--update_type', type=str, help="update type (Available options: ipv4, ipv6, both)")
    parser.add_argument('--update_interval', type=int, help="update interval，(seconds)")
    parser.add_argument('--once', action='store_true', help="Single running model")

    args = parser.parse_args()
    if has_args(args):

        if args.once:
            if args.domain and args.token and args.update_type:
                update_ddns_record(args.token,
                                   args.domain,
                                   args.update_type)
                log_print("Single update completed. Exiting...", "INFO")
                exit(0)
            else:
                log_print("Missing required parameters for single update，Exiting...", "ERROR")
                exit(1)


        process_exist, exit_code = process_does_not_exist()
        if not process_exist:
            if exit_code != 2 and Path(LOCK_FILE_PATH).exists():
                os.remove(LOCK_FILE_PATH)
                log_print("Lock file cleaned", "INFO")

            exit(exit_code)

        if not (args.domain and args.token and args.update_type):
            log_print("Missing required parameters，Exiting...", "ERROR")
            exit(1)


        conf = {
            "conf_name": args.conf_name or "default",
            "domain": args.domain,
            "token": args.token,
            "update_type": args.update_type,
            "update_interval": args.update_interval or 3600
        }

        encrypt_token(conf,secrets_file_path)



    if not Path(secrets_file_path).exists():
        log_print("Fatal Error!config doesn't exist!", "ERROR")
        exit(1)


    decrypt_conf = decrypt_token(secrets_file_path)
    token = decrypt_conf["token"]

    log_print(
        f"{'-'*100}", "INFO"
    )


    log_print(
        f"Currently running config {decrypt_conf['conf_name']} | "
        f"Domain {decrypt_conf['domain']} | "
        f"Token {token[:5]}{'*'*15}{token[-5:]}", "INFO"
    )

    log_print(
        f"{'-'*100}", "INFO"
    )

    while True:
        update_ddns_record(
            decrypt_conf["token"],
            decrypt_conf["domain"],
            decrypt_conf["update_type"]
        )
        log_print(f"{'-' * 30}This round of task has ended, Waiting for next round...{'-' * 30}", "INFO")
        time.sleep(int(decrypt_conf["update_interval"]))



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_print(f"Program exception: {e}", "ERROR")

    finally:
        try:
            if Path(LOCK_FILE_PATH).exists():
                with open(LOCK_FILE_PATH, "r") as f:
                    lock_file_pid = int(f.read().strip())
                if lock_file_pid == os.getpid():
                    os.remove(LOCK_FILE_PATH)
                    log_print("Lock file cleaned (fallback in finally)", "INFO")
        except Exception as e:
            log_print(f"Finally cleanup failed: {e}", "WARNING")











