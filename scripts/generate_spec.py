import re
import os

SPEC_FILE = "buildozer.spec"

def configure_spec():
    if not os.path.exists(SPEC_FILE):
        os.system("buildozer init")

    with open(SPEC_FILE, "r") as f:
        content = f.read()

    # 1. Parse requirements.txt
    reqs = ["python3", "kivy"] # Base requirements
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            for line in f:
                pkg = line.strip().split('==')[0].split('>=')[0]
                if pkg and pkg not in reqs:
                    reqs.append(pkg)
    
    # Remove known problematic packages for a "Guaranteed" build
    reqs = [r for r in reqs if r not in ['pandas', 'numpy', 'scipy']] 

    req_str = ",".join(reqs)

    # 2. Apply "Guaranteed" Settings
    replacements = {
        r'^title\s*=.*': f'title = My Python App',
        r'^package.name\s*=.*': f'package.name = myapp',
        r'^package.domain\s*=.*': f'package.domain = com.master.build',
        r'^requirements\s*=.*': f'requirements = {req_str}',
        r'^android.archs\s*=.*': f'android.archs = arm64-v8a', # Modern only
        r'^android.permissions\s*=.*': f'android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE',
        r'^android.accept_sdk_license\s*=.*': f'android.accept_sdk_license = True',
        r'^p4a.python_version\s*=.*': f'p4a.python_version = 3.10', # Match CI
        
        # CRITICAL FIX: Pin API and Build Tools to stable versions to prevent 
        # Buildozer from downloading bleeding-edge tools that break CI licenses
        r'^android.api\s*=.*': f'android.api = 33',
        r'^android.build_tools_version\s*=.*': f'android.build_tools_version = 33.0.2',
        
        r'^orientation\s*=.*': f'orientation = portrait',
    }

    for pattern, repl in replacements.items():
        content = re.sub(pattern, repl, content, flags=re.MULTILINE)

    with open(SPEC_FILE, "w") as f:
        f.write(content)
    
    print(f"✅ Configured buildozer.spec with: {req_str}")

if __name__ == "__main__":
    configure_spec()
