import os
import shutil

def create_project():
    if os.path.exists("android_app"):
        shutil.rmtree("android_app")
        
    os.makedirs("android_app/app/src/main/java/com/myapp")
    os.makedirs("android_app/app/src/main/res/layout")
    os.makedirs("android_app/app/src/main/python")

    # 1. settings.gradle
    with open("android_app/settings.gradle", "w") as f:
        f.write("""
pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "MyPythonApp"
include ':app'
""")

    # 2. build.gradle (root)
    with open("android_app/build.gradle", "w") as f:
        f.write("""
plugins {
    id 'com.android.application' version '8.2.0' apply false
    id 'com.chaquo.python' version '15.0.1' apply false
}
""")

    # 3. app/build.gradle
    with open("android_app/app/build
