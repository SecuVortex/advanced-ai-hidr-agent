"""Create Test Suspicious File"""
import os

downloads = os.path.expanduser("~\\Downloads")
test_file = os.path.join(downloads, "suspicious.exe")

with open(test_file, "w") as f:
    f.write("This is a test file")

print(f"Created: {test_file}")
print("\nNow run this file to trigger multi-agent analysis:")
print(f"  {test_file}")
