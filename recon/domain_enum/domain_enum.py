import socket

def run(target: str) -> dict:
    results = []

    try:
        ip = socket.gethostbyname(target)
        results.append({
            "domain": target,
            "ip": ip
        })
    except Exception as error:
        results.append({
            "domain": target,
            "error": str(error)
        })

    return {
        "module": "domain_enum",
        "target": target,
        "results": results
    }
