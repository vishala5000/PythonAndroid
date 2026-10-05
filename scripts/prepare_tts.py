import json
import onnx
import os
import urllib.request
import tarfile

def prepare_tts():
    # Ensure we are in the correct directory
    assets_dir = "android_app/app/src/main/assets/tts"
    os.makedirs(assets_dir, exist_ok=True)
    os.chdir(assets_dir)
    
    print("📥 Downloading model files...")
    urllib.request.urlretrieve(
        "https://github.com/vishala5000/PythonAndroid/releases/download/Pipertts/en_US-ljspeech-medium.onnx", 
        "en_US-ljspeech-medium.onnx"
    )
    urllib.request.urlretrieve(
        "https://github.com/vishala5000/PythonAndroid/releases/download/Pipertts/en_US-ljspeech-medium.onnx.json", 
        "en_US-ljspeech-medium.onnx.json"
    )
    
    print("🔧 Injecting Sherpa-ONNX metadata...")
    with open('en_US-ljspeech-medium.onnx.json', 'r') as f:
        config = json.load(f)
        
    with open('tokens.txt', 'w', encoding='utf-8') as f:
        for s, i in config['phoneme_id_map'].items():
            f.write(f'{s} {i[0]}\n')
            
    model = onnx.load('en_US-ljspeech-medium.onnx')
    meta = {
        'model_type': 'vits',
        'comment': 'piper',
        'language': config['language']['name_english'],
        'voice': config['espeak']['voice'],
        'has_espeak': 1,
        'n_speakers': config['num_speakers'],
        'sample_rate': config['audio']['sample_rate']
    }
    
    for k, v in meta.items():
        m = model.metadata_props.add()
        m.key = k
        m.value = str(v)
        
    onnx.save(model, 'ljspeech.onnx')
    print("✅ Model metadata injected successfully!")
    
    print("📥 Downloading espeak-ng-data...")
    urllib.request.urlretrieve(
        "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/espeak-ng-data.tar.bz2", 
        "espeak-ng-data.tar.bz2"
    )
    
    with tarfile.open("espeak-ng-data.tar.bz2", "r:bz2") as tar:
        tar.extractall()
        
    print("🧹 Cleaning up raw files to save APK space...")
    os.remove("en_US-ljspeech-medium.onnx")
    os.remove("en_US-ljspeech-medium.onnx.json")
    os.remove("espeak-ng-data.tar.bz2")
    
    print("✅ TTS assets prepared successfully!")

if __name__ == "__main__":
    prepare_tts()
