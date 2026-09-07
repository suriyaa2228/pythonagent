import subprocess
import re
from collections import defaultdict

test_file = "tests/test_tc004_verify_info_and_resource.py"
iterations = 3
results = defaultdict(list)

for i in range(1, iterations + 1):
    print(f"--- Running iteration {i}/{iterations} ---")
    result = subprocess.run(
        ["pytest", test_file, "-v", "--tb=short"], 
        capture_output=True, text=True
    )
    
    # Parse output to find test outcomes
    for line in result.stdout.split('\n'):
        # Matches lines like: tests/test_tc004_verify_info_and_resource.py::TestTC007VerifyInfoAndResource::test_01_click_info_and_resource_link PASSED
        if "::test_" in line and ("PASSED" in line or "FAILED" in line or "SKIPPED" in line):
            parts = line.split("::")
            if len(parts) >= 3:
                test_name = parts[-1].split(" ")[0].strip()
                outcome = "PASSED" if "PASSED" in line else "FAILED" if "FAILED" in line else "SKIPPED"
                results[test_name].append(outcome)
    
    if result.returncode != 0:
        print(f"Iteration {i} had failures.")
    else:
        print(f"Iteration {i} passed completely.")

print("\n--- Summary of Discrepancies ---")
has_discrepancies = False
for test_name, outcomes in results.items():
    unique_outcomes = set(outcomes)
    if len(unique_outcomes) > 1:
        has_discrepancies = True
        print(f"FLAKY TEST: {test_name} - Outcomes: {outcomes}")

if not has_discrepancies:
    print("All tests were perfectly consistent across all runs!")
