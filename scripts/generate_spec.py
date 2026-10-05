import re
import os

SPEC_FILE = "buildozer.spec"

def configure_spec():
    if not os.path.exists(SPEC_FILE):
        print("⚠️ buildozer.spec not found. Running 'buildozer init'...")
        os.system("buildozer init")

    with open(SPEC_FILE, "r") as f:
        content = f.read()

    # 1. Parse requirements.txt safely
    reqs = ["python3", "kivy"] # Base requirements for Android
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            for line in f:
                # Clean up package names (remove version specifiers like ==, >=, <=)
                pkg = line.strip().split('==')[0].split('>=')[0].split('<=')[0]
                if pkg and pkg not in reqs:
                    reqs.append(pkg)
    
    # Remove known problematic packages that often fail to compile on Android CI
    reqs = [r for r in reqs if r.lower() not in ['pandas', 'numpy', 'scipy', 'setuptools', 'wheel']] 
    req_str = ",".join(reqs)

    # 2. Apply "Guaranteed" Settings using robust regex
    replacements = {
        r'^\s*#?\s*title\s*=.*': 'title = My Python App',
        r'^\s*#?\s*package\.name\s*=.*': 'package.name = myapp',
        r'^\s*#?\s*package\.domain\s*=.*': 'package.domain = com.master.build',
        r'^\s*#?\s*requirements\s*=.*': f'requirements = {req_str}',
        r'^\s*#?\s*android\.archs\s*=.*': 'android.archs = arm64-v8a',
        r'^\s*#?\s*android\.permissions\s*=.*': 'android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE',
        r'^\s*#?\s*android\.accept_sdk_license\s*=.*': 'android.accept_sdk_license = True',
        r'^\s*#?\s*p4a\.python_version\s*=.*': 'p4a.python_version = 3.10',
        
        # CRITICAL: Pin API and Build Tools to stable versions
        r'^\s*#?\s*android\.api\s*=.*': 'android.api = 33',
        r'^\s*#?\s*android\.build_tools_version\s*=.*': 'android.build_tools_version = 33.0.2',
        
        r'^\s*#?\s*orientation\s*=.*': 'orientation = portrait',
    }

    for pattern, repl in replacements.items():
        content = re.sub(pattern, repl, content, flags=re.MULTILINE)

    # 3. Double-check fallback: If the line didn't exist, inject it under [app]
    for key, value in [
        ('android.api', '33'),
        ('android.build_tools_version', '33.0.2')
    ]:
        if f"{key} = {value}" not in content:
            if "[app]" in content:
                content = content.replace("[app]", f"[app]\n{key} = {value}", 1)
            else:
                content += f"\n[app]\n{key} = {value}\n"

    with open(SPEC_FILE, "w") as f:
        f.write(content)
    
    print(f"✅ Configured buildozer.spec with guaranteed settings and requirements: {req_str}")

if __name__ == "__main__":
    configure_spec()
