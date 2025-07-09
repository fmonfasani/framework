import asyncio
import json
from tests.test_genesis_framework import GenesisFrameworkTester


async def main():
    tester = GenesisFrameworkTester()
    report = await tester.run_all_tests()
    tester.print_final_report(report)
    with open("genesis_test_report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())

