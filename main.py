from recon.subdomain_enum.sub_enum import run as subdomain_enum
from recon.endpoint_discovery.endpoints import run as endpoint_discovery
from recon.tech_fingerprint.tech import run as tech_fingerprint


def banner():
    print(r"""
████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗
╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝
   ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║   
   ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║   
   ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║   
   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   

             By SebassGhost
    """)


def menu():
    print("[1] Subdomain Enumeration")
    print("[2] Endpoint Discovery")
    print("[3] Tech Fingerprinting")
    print("[4] Recon All")
    print("[0] Exit")


def get_choice():
    return input("\nSelect an option: ").strip()


def main():
    banner()
    menu()
    choice = get_choice()

    if choice == "1":
        target = input("Target domain: ")
        print(subdomain_enum(target))

    elif choice == "2":
        target = input("Target domain: ")
        print(endpoint_discovery(target))

    elif choice == "3":
        target = input("Target domain: ")
        print(tech_fingerprint(target))

    elif choice == "4":
        target = input("Target domain: ")
        print("[*] Running full recon...")
        print(subdomain_enum(target))
        print(endpoint_discovery(target))
        print(tech_fingerprint(target))

    elif choice == "0":
        print("Bye")

    else:
        print("Invalid option")


if __name__ == "__main__":
    main()
