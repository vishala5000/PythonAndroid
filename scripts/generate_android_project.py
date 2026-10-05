import os
import shutil

def create_project():
    if os.path.exists("android_app"):
        shutil.rmtree("android_app")
        
    os.makedirs("android_app/app/src/main/java/com/myapp")
    os.makedirs("android_app/app/src/main/res/layout")
    os.makedirs("android_app/app/src/main/python")

    with open("android_app/settings.gradle", "w") as f:
        f.write("""pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "PiperTTS"
include ':app'
""")

    with open("android_app/build.gradle", "w") as f:
        f.write("""plugins {
    id 'com.android.application' version '8.2.0' apply false
    id 'com.chaquo.python' version '15.0.1' apply false
}
""")

    with open("android_app/app/build.gradle", "w") as f:
        f.write("""plugins {
    id 'com.android.application'
    id 'com.chaquo.python'
}
android {
    namespace 'com.myapp'
    compileSdk 34
    defaultConfig {
        applicationId "com.myapp.pipertts"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
        ndk { abiFilters "armeabi-v7a", "arm64-v8a", "x86", "x86_64" }
    }
    buildTypes { release { minifyEnabled false } }
}
chaquopy {
    defaultConfig { pip { install "-r", "requirements.txt" } }
    sourceSets { main { srcDir "src/main/python" } }
}
dependencies { implementation 'androidx.appcompat:appcompat:1.6.1' }
""")

    with open("android_app/app/src/main/AndroidManifest.xml", "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Permissions for older Android versions (API < 29). Modern Android uses MediaStore without broad permissions -->
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
    
    <application android:allowBackup="true" android:label="Piper TTS" 
                 android:theme="@style/Theme.AppCompat.NoActionBar"
                 android:requestLegacyExternalStorage="true">
        <activity android:name=".MainActivity" android:exported="true" android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""")

    with open("android_app/app/src/main/java/com/myapp/MainActivity.java", "w") as f:
        f.write("""package com.myapp;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (!Python.isStarted()) Python.start(new AndroidPlatform(this));
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Python py = Python.getInstance();
        py.getModule("main").callAttr("run_app", this);
    }
}
""")

    with open("android_app/app/src/main/res/layout/activity_main.xml", "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:fillViewport="true" android:background="#121212">
    
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="24dp">
        
        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
            android:text="🎙️ Piper TTS (Unlimited)" android:textColor="#BB86FC"
            android:textSize="26sp" android:textStyle="bold" android:gravity="center" android:layout_marginBottom="16dp" />
            
        <EditText android:id="@+id/text_input" android:layout_width="match_parent"
            android:layout_height="200dp" android:hint="Enter unlimited text to speak..."
            android:textColor="#FFFFFF" android:textColorHint="#888888" android:background="#1E1E1E"
            android:padding="16dp" android:textSize="18sp" android:gravity="top"
            android:inputType="textMultiLine" android:scrollbars="vertical" />
            
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="horizontal" android:layout_marginTop="24dp">
            
            <Button android:id="@+id/speak_btn" android:layout_width="0dp" android:layout_height="wrap_content"
                android:layout_weight="1" android:layout_marginEnd="8dp"
                android:text="🔊 Generate &amp; Play" android:textColor="#000000"
                android:background="#03DAC6" android:textSize="16sp" android:padding="16dp" />
                
            <Button android:id="@+id/download_btn" android:layout_width="0dp" android:layout_height="wrap_content"
                android:layout_weight="1" android:layout_marginStart="8dp"
                android:text="💾 Download" android:textColor="#000000"
                android:background="#CF6679" android:textSize="16sp" android:padding="16dp"
                android:enabled="false" />
        </LinearLayout>
        
        <ProgressBar android:id="@+id/progress_bar" android:layout_width="wrap_content"
            android:layout_height="wrap_content" android:layout_gravity="center"
            android:layout_marginTop="24dp" android:visibility="gone"
            android:indeterminateTint="#BB86FC" />
            
        <TextView android:id="@+id/status_text" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:text="Initializing engine..."
            android:textColor="#888888" android:textSize="16sp" android:gravity="center"
            android:layout_marginTop="16dp" />
            
    </LinearLayout>
</ScrollView>
""")

    if os.path.exists("main.py"):
        with open("main.py", "r") as f:
            user_code = f.read()
        with open("android_app/app/src/main/python/user_logic.py", "w") as f:
            f.write(user_code)
        with open("android_app/app/src/main/python/main.py", "w") as f:
            f.write("""def run_app(activity):
    try:
        import user_logic
        if hasattr(user_logic, 'main'):
            user_logic.main(activity)
    except Exception as e:
        import traceback
        try:
            res_id = activity.getResources().getIdentifier("status_text", "id", activity.getPackageName())
            display = activity.findViewById(res_id)
            if display: display.setText(f"Python Error:\\n{str(e)}")
        except: pass
""")
    else:
        with open("android_app/app/src/main/python/main.py", "w") as f:
            f.write("def run_app(activity): pass\n")

    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", "android_app/app/requirements.txt")
    else:
        with open("android_app/app/requirements.txt", "w") as f:
            f.write("sherpa-onnx\n")

    with open("android_app/gradle.properties", "w") as f:
        f.write("org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\nandroid.useAndroidX=true\nandroid.nonTransitiveRClass=true\n")

    os.system("cd android_app && gradle wrapper --gradle-version 8.2")
    print("✅ Android TTS project generated successfully!")

if __name__ == "__main__":
    create_project()
