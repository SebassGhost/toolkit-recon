#!/usr/bin/env python3
import sys
import time

# =========================
# COLORS (UX)
# =========================
class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


# =========================
# BANNER
# =========================
def banner():
    print(C.BLUE + r"""
████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗████████╗
╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝╚══██╔══╝
   ██║   ██║   ██║██║   ██║██║     █████╔╝    ██║
   ██║   ██║   ██║██║   ██║██║     ██╔═██╗    ██║
   ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗   ██║
   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝
    """ + C.RESET)
    print("By SebassGhost\n")


# =========================
# MENU
# =========================
def menu():
    print("[1] Subdomain Enumeration")
    print("[2] Endpoint Discovery")
    print("[3] Tech Fingerprinting")
    print("[4] Recon All")
    print("[0] Exit")


# =========================
# HELPERS
# =========================
def ask_target():
    target = input("\nTarget domain: ").strip()
    if not target:
        print(C.RED + "[-] Target cannot be empty" + C.RESET)
        return None
    return target


def pause():
    input(C.YELLOW + "\nPress Enter to continue..." + C.RESET)


# =========================
# OUTPUT FORMATTERS
# =========================
def show_subdomains(data):
    results = data.get("results", [])
    print(C.GREEN + f"\n[✔] {len(results)} subdomains found\n" + C.RESET)

    for r in results:
        print(
            f" - {r.get('subdomain'):30} "
            f"{r.get('ip', 'N/A'):15} "
            f"({r.get('source', 'unknown')})"
        )


# =========================
# MODULE RUNNERS
# =========================
def run_subdomain_enum():
    from toolkit_recon.recon.subdomain_enum.sub_enum import run as sub_run
    from toolkit_recon.utils.output import save_output

    target = ask_target()
    if not target:
        return

    data = sub_run(target)
    show_subdomains(data)
    save_output(target, "subdomains", data)


def run_endpoint_discovery():
    from toolkit_recon.recon.endpoint_discovery.endpoints import run as endpoint_run
    from toolkit_recon.utils.output import save_output

    target = ask_target()
    if not target:
        return

    print(C.BLUE + "\n--- Endpoint Discovery ---" + C.RESET)

    endpoints = endpoint_run(target)

    if not endpoints or not isinstance(endpoints, list):
        print(C.YELLOW + "[!] No endpoints found" + C.RESET)
        return

    interesting = [e for e in endpoints if isinstance(e, dict) and e.get("interesting")]

    print(C.GREEN + f"\n[✔] {len(interesting)} interesting endpoints found\n" + C.RESET)

    for e in interesting:
        print(
            f" - {e.get('path'):25} "
            f"[{e.get('status')}] "
            f"{','.join(e.get('methods', []))}"
        )

    save_output(target, "endpoints", endpoints)


def run_recon_all():
    from toolkit_recon.recon.subdomain_enum.sub_enum import run as sub_run
    from toolkit_recon.recon.endpoint_discovery.endpoints import run as endpoint_run
    from toolkit_recon.utils.output import save_output, save_recon
    from toolkit_recon.recon.tech_fingerprint.fingerprint import run as fp_run

    target = ask_target()
    if not target:
        return

    # =========================
    # SUBDOMAIN ENUMERATION
    # =========================
    print(C.BLUE + "\n--- Subdomain Enumeration ---" + C.RESET)

    sub_data = sub_run(target)
    results = sub_data.get("results", [])

    show_subdomains(sub_data)
    save_output(target, "subdomains", sub_data)
    save_recon(target, "subdomain_enum", sub_data)

    # =========================
    # ENDPOINT DISCOVERY
    # =========================
    print(C.BLUE + "\n--- Endpoint Discovery (per subdomain) ---" + C.RESET)

    all_endpoints = {}

    for entry in results:
        subdomain = entry.get("subdomain")
        if not subdomain:
            continue

        print(C.BLUE + f"\n[*] Scanning {subdomain}" + C.RESET)

        endpoints = endpoint_run(subdomain)

        if not endpoints or not isinstance(endpoints, list):
            print(C.YELLOW + "    [!] No endpoints found" + C.RESET)
            continue

        clean = [e for e in endpoints if isinstance(e, dict)]
        interesting = [e for e in clean if e.get("interesting")]

        print(
            C.GREEN
            + f"    [✓] {len(interesting)} interesting endpoints found"
            + C.RESET
        )

        all_endpoints[subdomain] = clean

    save_output(target, "endpoints", all_endpoints)
    save_recon(target, "endpoint_discovery", all_endpoints)

    # =========================
    # TECH FINGERPRINT (placeholder)
    # =========================
       # =========================
    # TECH FINGERPRINTING
    # =========================
    print(C.BLUE + "\n--- Tech Fingerprinting ---" + C.RESET)

    fingerprints = {}

    for entry in results:
        subdomain = entry.get("subdomain")
        if not subdomain:
            continue

        print(C.BLUE + f"[*] Fingerprinting {subdomain}" + C.RESET)

        fp = fp_run(subdomain)

        if fp:
            fingerprints[subdomain] = fp

    save_recon(target, "tech_fingerprint", fingerprints)



# =========================
# MAIN LOOP
# =========================
def main():
    while True:
        banner()
        menu()

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            run_subdomain_enum()
            pause()
        elif choice == "2":
            run_endpoint_discovery()
            pause()
        elif choice == "3":
            print(C.YELLOW + "\n[!] Tech Fingerprinting not implemented yet" + C.RESET)
            pause()
        elif choice == "4":
            run_recon_all()
            pause()
        elif choice == "0":
            sys.exit(0)
        else:
            print(C.RED + "\nInvalid option" + C.RESET)
            time.sleep(1)


if __name__ == "__main__":
    main()
