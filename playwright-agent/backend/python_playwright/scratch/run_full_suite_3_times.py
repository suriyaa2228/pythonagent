import subprocess
import re
import json
import time
from collections import defaultdict
import datetime

test_dir = "tests/"
iterations = 3
results = defaultdict(list)
start_time = time.time()

for i in range(1, iterations + 1):
    print(f"[{datetime.datetime.now()}] --- Running iteration {i}/{iterations} ---")
    # Run all tests in the tests directory
    result = subprocess.run(
        ["pytest", test_dir, "-v", "--tb=short"], 
        capture_output=True, text=True
    )
    
    # Parse output to find test outcomes
    for line in result.stdout.split('\n'):
        if "::test_" in line and ("PASSED" in line or "FAILED" in line or "SKIPPED" in line):
            parts = line.split("::")
            if len(parts) >= 3:
                # E.g. tests/test_tc001...py::TestClass::test_method PASSED
                test_name = f"{parts[0]}::{parts[-1].split(' ')[0].strip()}"
                outcome = "PASSED" if "PASSED" in line else "FAILED" if "FAILED" in line else "SKIPPED"
                results[test_name].append(outcome)
    
    if result.returncode != 0:
        print(f"[{datetime.datetime.now()}] Iteration {i} had failures.")
    else:
        print(f"[{datetime.datetime.now()}] Iteration {i} passed completely.")

print(f"\n--- Summary of Discrepancies (Total time: {(time.time() - start_time)/60:.2f} mins) ---")
has_discrepancies = False
for test_name, outcomes in results.items():
    # If the test didn't run all 3 times, pad with "MISSING"
    while len(outcomes) < iterations:
        outcomes.append("MISSING")
        
    unique_outcomes = set(outcomes)
    if len(unique_outcomes) > 1:
        has_discrepancies = True
        print(f"FLAKY TEST: {test_name} - Outcomes: {outcomes}")

if not has_discrepancies:
    print("All tests were perfectly consistent across all runs!")

# Save results to a file for easy analysis later
with open("scratch/full_suite_results.json", "w") as f:
    json.dump(results, f, indent=4)
print("Results saved to scratch/full_suite_results.json")
