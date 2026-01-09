#!/usr/bin/env python3
import sys
import time
print(">>> MAIN CORRECTO EJECUTÁNDOSE <<<")

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
            f"{r.get('ip'):15} "
            f"({r.get('source')})"
        )


# =========================
# MODULE RUNNERS
# =========================
def run_subdomain_enum():
    from toolkit_recon.recon.subdomain_enum.sub_enum import run
    from toolkit_recon.utils.output import save_output

    target = ask_target()
    if not target:
        return

    data = run(target)
    show_subdomains(data)
    save_output(target, "subdomains", data)


def run_recon_all():
    from toolkit_recon.recon.subdomain_enum.sub_enum import run as sub_run
    from toolkit_recon.utils.output import save_output

    target = ask_target()
    if not target:
        return

    print(C.BLUE + "\n--- Subdomain Enumeration ---" + C.RESET)

    sub_data = sub_run(target)
    show_subdomains(sub_data)
    save_output(target, "subdomains", sub_data)

    print(C.GREEN + "\n[✓] Recon All completed" + C.RESET)

def run_endpoint_discovery():
    print(C.YELLOW + "\n[!] Endpoint Discovery not implemented yet" + C.RESET)


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
            run_tech_fingerprint()
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
