name: 🚀 Ultra-Fast Android Builder (No Buildozer)

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: ☕ Set up JDK 17
        uses: actions/setup-java@v5
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: 🤖 Use Native Pre-installed Android SDK
        run: |
          echo "ANDROID_HOME=/usr/local/lib/android/sdk" >> $GITHUB_ENV
          echo "ANDROID_SDK_ROOT=/usr/local/lib/android/sdk" >> $GITHUB_ENV
          
          mkdir -p $ANDROID_HOME/licenses
          echo -e "\n24333f8a63b6825ea9c5514f83c2829b004d1fee" > $ANDROID_HOME/licenses/android-sdk-license
          echo -e "\n84831b9409646a918e30573bab4c9c91346d8abd" > $ANDROID_HOME/licenses/android-sdk-preview-license
          echo "✅ Native Android SDK configured and licenses accepted."

      - name: 🏗️ Generate Android Project & Wrap Python
        run: python scripts/generate_android_project.py

      - name: 🚀 Build APK with Gradle (Ultra Fast)
        uses: gradle/actions/setup-gradle@v3
        with:
          gradle-version: '8.2'
          arguments: assembleDebug
          build-root-directory: ./android_app

      - name: 🔑 Auto-Sign APK using apksigner (No Secrets)
        run: |
          KEYSTORE="$HOME/.android/debug.keystore"
          UNSIGNED="android_app/app/build/outputs/apk/debug/app-debug.apk"
          SIGNED="android_app/app/build/outputs/apk/debug/app-signed.apk"
          
          mkdir -p "$HOME/.android"
          if [ ! -f "$KEYSTORE" ]; then
            echo "Generating default public debug keystore..."
            keytool -genkey -v \
              -keystore "$KEYSTORE" \
              -storepass android \
              -alias androiddebugkey \
              -keypass android \
              -keyalg RSA -keysize 2048 -validity 10000 \
              -dname "CN=Android Debug,O=Android,C=US"
          fi
          
          APKSIGNER=$(find /usr/local/lib/android/sdk/build-tools -name "apksigner" | head -n 1)
          echo "Using apksigner at: $APKSIGNER"
          
          "$APKSIGNER" sign \
            --ks "$KEYSTORE" \
            --ks-pass pass:android \
            --ks-key-alias androiddebugkey \
            --key-pass pass:android \
            --out "$SIGNED" \
            "$UNSIGNED"
            
          echo "✅ APK signed successfully using default debug credentials!"

      - name: 📤 Upload Signed APK
        uses: actions/upload-artifact@v4
        with:
          name: my-signed-android-app
          path: android_app/app/build/outputs/apk/debug/app-signed.apk
          if-no-files-found: error
