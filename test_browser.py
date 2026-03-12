import subprocess
import sys

# Run browser search
result = subprocess.run(
    [sys.executable, r"C:\Users\yezhihong\.openclaw\skills\browser-search\scripts\browser.py", 
     "search", "A股行情", "--limit", "3"],
    capture_output=True,
    text=True,
    timeout=60
)

print("STDOUT:")
print(result.stdout[:2000] if result.stdout else "No output")
print("\nSTDERR:")
print(result.stderr[:500] if result.stderr else "No errors")
