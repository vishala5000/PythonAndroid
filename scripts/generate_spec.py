import os
import re

SPEC_FILE = "buildozer.spec"

def configure_spec():
    # 1. ALWAYS delete the old spec to prevent duplicate entries from previous failed runs
    if os.path.exists(SPEC_FILE):
        os.remove(SPEC_FILE)
    
    # 2. Generate a fresh, clean buildozer.spec
    os.system("buildozer init")

    with open(SPEC_FILE, "r") as f:
        lines = f.readlines()

    # 3. Parse requirements.txt safely
    reqs = ["python3", "kivy"]
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            for line in f:
                pkg = line.strip().split('==')[0].split('>=')[0].split('<=')[0]
                if pkg and pkg.lower() not in ['pandas', 'numpy', 'scipy', 'setuptools', 'wheel', '']:
                    if pkg not in reqs:
                        reqs.append(pkg)
    req_str = ",".join(reqs)

    # 4. Define the exact values we want to enforce
    target_values = {
        'title': 'My Python App',
        'package.name': 'myapp',
        'package.domain': 'com.master.build',
        'requirements': req_str,
        'android.archs': 'arm64-v8a',
        'android.permissions': 'INTERNET,WRITE_EXTERNAL_STORAGE',
        'android.accept_sdk_license': 'True',
        'p4a.python_version': '3.10',
        'android.api': '33',
        'android.build_tools_version': '33.0.2',
        'orientation': 'portrait',
    }

    # 5. Process the file line by line to guarantee NO duplicates
    new_lines = []
    found_keys = set()
    
    for line in lines:
        matched_key = None
        # Check if this line is an UNCOMMENTED definition of one of our target keys
        for key in target_values:
            if re.match(rf'^\s*{re.escape(key)}\s*=', line):
                matched_key = key
                break
        
        if matched_key:
            found_keys.add(matched_key)
            # Replace the line with our guaranteed value
            new_lines.append(f"{matched_key} = {target_values[matched_key]}\n")
        else:
            new_lines.append(line)

    # 6. Append any missing keys at the very end of the [app] section
    # Find the end of the [app] section (where the next section starts, or EOF)
    insert_index = len(new_lines)
    for i, line in enumerate(new_lines):
        if line.strip().startswith('[') and line.strip() != '[app]':
            insert_index = i
            break
            
    missing_keys = []
    for key, value in target_values.items():
        if key not in found_keys:
            missing_keys.append(f"{key} = {value}\n")
            
    if missing_keys:
        for idx, mk in enumerate(missing_keys):
            new_lines.insert(insert_index + idx, mk)

    with open(SPEC_FILE, "w") as f:
        f.writelines(new_lines)
    
    print(f"✅ Configured buildozer.spec with guaranteed settings and requirements: {req_str}")

if __name__ == "__main__":
    configure_spec()
