import json
import re
import sys
import os

# Load internal project-level license mapping
with open(".github/mapping.json", "r") as f:
    project_mapping = json.load(f)
    allowed_licenses = set(project_mapping.get("allowed_licenses", []))

# Read the patch file
with open("pr_diff.patch", "r") as f:
    patch_content = f.read()

# Extract changed file names
changed_files = set(re.findall(r"diff --git a/(.+) b/\1", patch_content))

# Regex patterns to detect copyright and license in added lines
copyright_pattern = re.compile(r'Copyright\s+\(c\)\s+\d{4}\s+(.+)\.\s+All\s+rights\s+reserved\.', re.IGNORECASE)
license_pattern = re.compile(r'SPDX-License-Identifier:\s*(\S+)', re.IGNORECASE)

detected_licenses = set()
detected_copyrights = set()

for file in changed_files:
    file_path = os.path.join(os.getenv('GITHUB_WORKSPACE', ''), file)
    print(f"Checking file: {file_path}")
    try:
        with open(file_path, "r") as f:
            content = f.readlines()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        continue

    for line in content:
        print(f"Processing line: {line.strip()}")
        copyright_match = copyright_pattern.search(line)
        if copyright_match:
            copyright_holder = copyright_match.group(1).strip()
            detected_copyrights.add(copyright_holder)
            print(f"Copyright found in file: {file}, Holder: {copyright_holder}")
        
        license_match = license_pattern.search(line)
        print(f"License match: {license_match}")
        print('--------------')
        if license_match:
            detected_license = license_match.group(1).strip()
            detected_licenses.add(detected_license)

# Validate detected licenses against project mapping
if detected_licenses:
    invalid_licenses = detected_licenses - allowed_licenses

    if invalid_licenses:
        print(f"❌ License Mismatch. Allowed: {allowed_licenses}, Found: {detected_licenses}")
        sys.exit(1)
    else:
        print(f"✅ License Check Passed. Detected Licenses: {detected_licenses}")
else:
    print("⚠️ No licenses detected in changed files.")

# Print detected copyrights
if detected_copyrights:
    print(f"Detected Copyright Holders: {detected_copyrights}")

sys.exit(0)