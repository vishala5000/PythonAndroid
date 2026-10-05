import re
import os

SPEC_FILE = "buildozer.spec"

def configure_spec():
    if not os.path.exists(SPEC_FILE):
        os.system("buildozer init")

    with open(SPEC_FILE, "r") as f:
        content = f.read()

    # 1. Parse requirements.txt safely
    reqs = ["python3", "kivy"]
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            for line in f:
                pkg = line.strip().split('==')[0].split('>=')[0].split('<=')[0]
                if pkg and pkg.lower() not in ['pandas', 'numpy', 'scipy', 'setuptools', 'wheel', '']:
                    if pkg not in reqs:
                        reqs.append(pkg)
    req_str = ",".join(reqs)

    # 2. Apply Guaranteed Settings (Regex matches commented or uncommented lines)
    replacements = {
        r'^\s*#?\s*title\s*=.*': 'title = My Python App',
        r'^\s*#?\s*package\.name\s*=.*': 'package.name = myapp',
        r'^\s*#?\s*package\.domain\s*=.*': 'package.domain = com.master.build',
        r'^\s*#?\s*requirements\s*=.*': f'requirements = {req_str}',
        r'^\s*#?\s*android\.archs\s*=.*': 'android.archs = arm64-v8a',
        r'^\s*#?\s*android\.permissions\s*=.*': 'android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE',
        r'^\s*#?\s*android\.accept_sdk_license\s*=.*': 'android.accept_sdk_license = True',
        r'^\s*#?\s*p4a\.python_version\s*=.*': 'p4a.python_version = 3.10',
        
        # CRITICAL: Pin to 33 to avoid the build-tools 37.0.0 license trap
        r'^\s*#?\s*android\.api\s*=.*': 'android.api = 33',
        r'^\s*#?\s*android\.build_tools_version\s*=.*': 'android.build_tools_version = 33.0.2',
        
        r'^\s*#?\s*orientation\s*=.*': 'orientation = portrait',
    }

    for pattern, repl in replacements.items():
        content = re.sub(pattern, repl, content, flags=re.MULTILINE)

    # 3. Fallback injection if lines were completely missing
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
    
    print(f"✅ Configured buildozer.spec with pinned API 33 and Build Tools 33.0.2")

if __name__ == "__main__":
    configure_spec()
