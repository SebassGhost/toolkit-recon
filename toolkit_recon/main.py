#!/usr/bin/env python3
import argparse
import sys


class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def banner():
    print(C.BLUE + "Toolkit-Recon" + C.RESET)
    print("Modular reconnaissance toolkit\n")


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

    sub = subparsers.add_parser("subdomain", help="Subdomain enumeration")
    sub.add_argument("target", help="Target domain")

    ep = subparsers.add_parser("endpoints", help="Endpoint discovery")
    ep.add_argument("target", help="Target domain or subdomain")

    tech = subparsers.add_parser("tech", help="Technology fingerprinting")
    tech.add_argument("target", help="Target domain or subdomain")

    osint_user = subparsers.add_parser("osint-user", help="OSINT username lookup")
    osint_user.add_argument("target", help="Username")

    recon = subparsers.add_parser("recon-all", help="Full reconnaissance")
    recon.add_argument("target", help="Target domain")
    recon.add_argument(
        "--osint-user",
        dest="osint_user",
        default=None,
        help="Username para enriquecer recon con OSINT (Sherlock)",
    )

    return parser.parse_args()


def cmd_subdomain(args):
    from toolkit_recon.recon.subdomain_enum.sub_enum import run
    from toolkit_recon.utils.output import save_output, save_recon

    print(C.BLUE + "\n--- Subdomain Enumeration ---" + C.RESET)

    data = run(args.target, profile=args.profile)

    results = data.get("results", [])
    print(C.GREEN + f"[+] {len(results)} subdomains found\n" + C.RESET)

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

    data = run(args.target, profile=args.profile)
    endpoints = data.get("results", [])

    if not endpoints:
        print(C.YELLOW + "[!] No endpoints found" + C.RESET)
    else:
        interesting = [e for e in endpoints if e.get("interesting")]
        print(C.GREEN + f"[+] {len(interesting)} interesting endpoints found\n" + C.RESET)

        for e in interesting:
            methods = ",".join(e.get("methods", []))
            print(f" - {e.get('path'):25} [{e.get('status')}] {methods}")

    metrics = data.get("metrics", {})
    if metrics:
        print(
            f"[i] scanned={metrics.get('total_paths', 0)} "
            f"ok={metrics.get('completed', 0)} "
            f"errors={metrics.get('errors', 0)} "
            f"retries={metrics.get('retried_requests', 0)} "
            f"time={metrics.get('duration_seconds', 0)}s"
        )

    save_output(args.target, "endpoints", data)
    save_recon(args.target, "endpoint_discovery", data)


def cmd_tech(args):
    from toolkit_recon.recon.tech_fingerprint.fingerprint import run
    from toolkit_recon.utils.output import save_output, save_recon

    print(C.BLUE + "\n--- Tech Fingerprinting ---" + C.RESET)

    data = run(args.target, profile=args.profile)

    techs = data.get("technologies", {})
    print(C.GREEN + "[+] Technologies detected:\n" + C.RESET)

    for k, v in techs.items():
        print(f" - {k}: {v}")

    save_output(args.target, "tech_fingerprint", data)
    save_recon(args.target, "tech_fingerprint", data)


def cmd_osint_user(args):
    from toolkit_recon.recon.osint_username.username import run
    from toolkit_recon.utils.output import save_output, save_recon

    print(C.BLUE + "\n--- OSINT Username ---" + C.RESET)

    data = run(args.target, profile=args.profile)
    found = data.get("metrics", {}).get("found", 0)
    errors = data.get("metrics", {}).get("errors", 0)

    print(C.GREEN + f"[+] Perfiles encontrados: {found}" + C.RESET)
    if errors:
        print(C.YELLOW + f"[!] Errores: {errors}" + C.RESET)
        if data.get("error"):
            print(f"    {data['error']}")

    for item in data.get("results", []):
        print(f" - {item.get('site')}: {item.get('url')}")

    save_output(args.target, "osint_username", data)
    save_recon(args.target, "osint_username", data)


def cmd_recon_all(args):
    from toolkit_recon.recon.recon_all import run

    print(C.BLUE + "\n--- Recon All ---" + C.RESET)
    data = run(
        args.target,
        profile=args.profile,
        osint_user=args.osint_user,
    )

    sub_count = (
        data.get("modules", {})
        .get("subdomain_enum", {})
        .get("count", 0)
    )
    endpoint_targets = len(
        data.get("modules", {})
        .get("endpoint_discovery", {})
    )
    tech_targets = len(
        data.get("modules", {})
        .get("tech_fingerprint", {})
    )
    osint_found = (
        data.get("modules", {})
        .get("osint_username", {})
        .get("metrics", {})
        .get("found")
    )

    print(C.GREEN + "\n[+] Recon All completed" + C.RESET)
    print(f"    subdomains: {sub_count}")
    print(f"    endpoint scans: {endpoint_targets}")
    print(f"    tech fingerprints: {tech_targets}")
    if osint_found is not None:
        print(f"    osint perfiles encontrados: {osint_found}")


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
    elif args.command == "osint-user":
        cmd_osint_user(args)
    elif args.command == "recon-all":
        cmd_recon_all(args)
    else:
        print(C.RED + "[-] Unknown command" + C.RESET)


if __name__ == "__main__":
    main()
