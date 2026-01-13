#!/usr/bin/env python3
import argparse
import sys

# =========================
# COLORS
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
    print("toolkit-recon | by SebassGhost\n")


# =========================
# ARGPARSE
# =========================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Recon framework for bug bounty and pentesting"
    )

    parser.add_argument(
        "--profile",
        choices=["passive", "balanced", "aggressive"],
        default="balanced",
        help="Scan aggressiveness profile",
    )

    subparsers = parser.add_subparsers(dest="command")

    # subdomain
    sub = subparsers.add_parser("subdomain", help="Subdomain enumeration")
    sub.add_argument("target", help="Target domain")

    # endpoints
    ep = subparsers.add_parser("endpoints", help="Endpoint discovery")
    ep.add_argument("target", help="Target domain or subdomain")

    # tech fingerprint
    tech = subparsers.add_parser("tech", help="Technology fingerprinting")
    tech.add_argument("target", help="Target domain or subdomain")

    # recon all
    recon = subparsers.add_parser("recon-all", help="Full reconnaissance")
    recon.add_argument("target", help="Target domain")

    return parser.parse_args()


# =========================
# COMMAND HANDLERS
# =========================
def cmd_subdomain(args):
    from toolkit_recon.recon.subdomain_enum.sub_enum import run
    from toolkit_recon.utils.output import save_output, save_recon

    print(C.BLUE + "\n--- Subdomain Enumeration ---" + C.RESET)

    data = run(args.target, profile=args.profile)

    results = data.get("results", [])
    print(C.GREEN + f"[✔] {len(results)} subdomains found\n" + C.RESET)

    for r in results:
        print(
            f" - {r.get('subdomain'):30} "
            f"{r.get('ip', 'N/A'):15} "
            f"({r.get('source', 'unknown')})"
        )

    save_output(args.target, "subdomains", data)
    save_recon(args.target, "subdomain_enum", data)


def cmd_endpoints(args):
    from toolkit_recon.recon.endpoint_discovery.endpoints import run
    from toolkit_recon.utils.output import save_output, save_recon

    print(C.BLUE + "\n--- Endpoint Discovery ---" + C.RESET)

    endpoints = run(args.target, profile=args.profile)

    if not endpoints:
        print(C.YELLOW + "[!] No endpoints found" + C.RESET)
        return

    interesting = [e for e in endpoints if e.get("interesting")]

    print(C.GREEN + f"[✔] {len(interesting)} interesting endpoints found\n" + C.RESET)

    for e in interesting:
        print(
            f" - {e.get('path'):25} "
            f"[{e.get('status')}] "
            f"{','.join(e.get('methods', []))}"
        )

    save_output(args.target, "endpoints", endpoints)
    save_recon(args.target, "endpoint_discovery", endpoints)


def cmd_tech(args):
    from toolkit_recon.recon.tech_fingerprint.fingerprint import run
    from toolkit_recon.utils.output import save_output, save_recon

    print(C.BLUE + "\n--- Tech Fingerprinting ---" + C.RESET)

    data = run(args.target)

    techs = data.get("technologies", {})
    print(C.GREEN + "[✔] Technologies detected:\n" + C.RESET)

    for k, v in techs.items():
        print(f" - {k}: {v}")

    save_output(args.target, "tech_fingerprint", data)
    save_recon(args.target, "tech_fingerprint", data)


def cmd_recon_all(args):
    from toolkit_recon.recon.subdomain_enum.sub_enum import run as sub_run
    from toolkit_recon.recon.endpoint_discovery.endpoints import run as ep_run
    from toolkit_recon.recon.tech_fingerprint.fingerprint import run as tech_run
    from toolkit_recon.utils.output import save_recon

    print(C.BLUE + "\n--- Recon All ---" + C.RESET)

    # Subdomains
    sub_data = sub_run(args.target, profile=args.profile)
    save_recon(args.target, "subdomain_enum", sub_data)

    results = sub_data.get("results", [])

    # Endpoints
    all_endpoints = {}
    for r in results:
        sub = r.get("subdomain")
        if not sub:
            continue

        print(C.BLUE + f"[*] Scanning {sub}" + C.RESET)
        eps = ep_run(sub, profile=args.profile)
        all_endpoints[sub] = eps or []

    save_recon(args.target, "endpoint_discovery", all_endpoints)

    # Tech fingerprint
    tech_data = tech_run(args.target)
    save_recon(args.target, "tech_fingerprint", tech_data)

    print(C.GREEN + "\n[✓] Recon All completed" + C.RESET)


# =========================
# MAIN
# =========================
def main():
    banner()
    args = parse_args()

    if not args.command:
        print(C.RED + "[-] No command specified\n" + C.RESET)
        sys.exit(1)

    if args.command == "subdomain":
        cmd_subdomain(args)
    elif args.command == "endpoints":
        cmd_endpoints(args)
    elif args.command == "tech":
        cmd_tech(args)
    elif args.command == "recon-all":
        cmd_recon_all(args)
    else:
        print(C.RED + "[-] Unknown command" + C.RESET)


if __name__ == "__main__":
    main()
