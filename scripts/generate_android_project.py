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
    with open("android_app/app/build.gradle", "w") as f:
        f.write("""
plugins {
    id 'com.android.application'
    id 'com.chaquo.python'
}

android {
    namespace 'com.myapp'
    compileSdk 34
    defaultConfig {
        applicationId "com.myapp"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
        ndk {
            abiFilters "armeabi-v7a", "arm64-v8a", "x86", "x86_64"
        }
    }
    buildTypes { release { minifyEnabled false } }
}

chaquopy {
    defaultConfig {
        pip {
            install "-r", "requirements.txt"
        }
    }
    sourceSets {
        main {
            srcDir "src/main/python"
        }
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
}
""")

    # 4. AndroidManifest.xml
    with open("android_app/app/src/main/AndroidManifest.xml", "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application android:allowBackup="true" android:label="My Python App" 
                 android:theme="@style/Theme.AppCompat.Light.DarkActionBar">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""")

    # 5. MainActivity.java
    with open("android_app/app/src/main/java/com/myapp/MainActivity.java", "w") as f:
        f.write("""package com.myapp;

import android.os.Bundle;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        TextView output = findViewById(R.id.output_text);
        Python py = Python.getInstance();
        py.getModule("main").callAttr("run_app", output);
    }
}
""")

    # 6. activity_main.xml
    with open("android_app/app/src/main/res/layout/activity_main.xml", "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent" android:padding="16dp">
    <TextView android:id="@+id/output_text" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:text="Starting Python..."
        android:textSize="18sp" android:textIsSelectable="true"/>
</ScrollView>
""")

    # 7. Auto-Wrap User's main.py
    if os.path.exists("main.py"):
        with open("main.py", "r") as f:
            user_code = f.read()
        
        with open("android_app/app/src/main/python/user_logic.py", "w") as f:
            f.write(user_code)
            
        with open("android_app/app/src/main/python/main.py", "w") as f:
            f.write("""import sys
import threading

def run_app(text_view):
    class TextViewWriter:
        def write(self, text):
            text_view.post(lambda: text_view.append(text))
        def flush(self): pass
    
    sys.stdout = TextViewWriter()
    sys.stderr = TextViewWriter()
    
    def run_logic():
        try:
            import user_logic
            if hasattr(user_logic, 'main'):
                user_logic.main(text_view)  # <-- CRITICAL FIX: Pass text_view to build UI
        except Exception as e:
            print(f"Error in user code: {e}")
            
    threading.Thread(target=run_logic, daemon=True).start()
""")
    else:
        with open("android_app/app/src/main/python/main.py", "w") as f:
            f.write("def run_app(tv):\n    tv.post(lambda: tv.setText('Hello from Python!'))\n")

    # 8. Copy requirements.txt
    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", "android_app/app/requirements.txt")
    else:
        with open("android_app/app/requirements.txt", "w") as f:
            f.write("# Add your pip dependencies here\n")

    # 9. Generate gradle.properties
    with open("android_app/gradle.properties", "w") as f:
        f.write("""
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
""")

    # 10. Generate Gradle Wrapper
    os.system("cd android_app && gradle wrapper --gradle-version 8.2")
    
    print("✅ Android project generated successfully! No Buildozer required.")

if __name__ == "__main__":
    create_project()
