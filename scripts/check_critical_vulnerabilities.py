import json
import sys
from pathlib import Path


def parse_score(vulnerability: dict) -> float:
    cvss = (
        vulnerability.get("cvss_score")
        or vulnerability.get("cvssv3")
        or vulnerability.get("severity")
        or 0
    )
    try:
        return float(cvss)
    except (TypeError, ValueError):
        return 0.0


def main() -> int:
    report_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("safety-report.json")

    if not report_file.exists():
        print(f"{report_file} not found")
        return 1

    data = json.loads(report_file.read_text())
    vulnerabilities = data if isinstance(data, list) else data.get("vulnerabilities", [])

    critical = [v for v in vulnerabilities if parse_score(v) >= 9.0]

    if critical:
        print(f"Critical vulnerabilities found: {len(critical)}")
        for vulnerability in critical:
            package_name = vulnerability.get("package_name", "unknown")
            vulnerability_id = vulnerability.get("vulnerability_id", "n/a")
            score = vulnerability.get("cvss_score", vulnerability.get("cvssv3", "n/a"))
            print(f"- {package_name} | {vulnerability_id} | CVSS: {score}")
        return 1

    print("No critical vulnerabilities found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
