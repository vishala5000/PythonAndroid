import os
import shutil
import struct
import wave
import threading
import sherpa_onnx
from java import dynamic_proxy
from android.view import View
from android.media import MediaPlayer
from android.widget import Toast, ProgressBar
from android.content import ContentValues
from android.provider import MediaStore
from android.os import Environment

def main(activity):
    def get_id(name):
        return activity.getResources().getIdentifier(name, "id", activity.getPackageName())

    text_input = activity.findViewById(get_id("text_input"))
    speak_btn = activity.findViewById(get_id("speak_btn"))
    download_btn = activity.findViewById(get_id("download_btn"))
    status_text = activity.findViewById(get_id("status_text"))
    progress_bar = activity.findViewById(get_id("progress_bar"))

    files_dir = activity.getFilesDir().getAbsolutePath()
    tts_dir = os.path.join(files_dir, "tts")
    espeak_dir = os.path.join(tts_dir, "espeak-ng-data")
    
    # Mutable state to hold the path of the last generated audio
    current_wav_path = [None]

    # 1. Extract assets to internal storage on first run
    if not os.path.exists(tts_dir):
        os.makedirs(tts_dir)
        asset_manager = activity.getAssets()
        
        def copy_asset_dir(asset_path, dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
            for item in asset_manager.list(asset_path):
                full_asset = os.path.join(asset_path, item)
                full_dest = os.path.join(dest_dir, item)
                try:
                    asset_manager.list(full_asset) # Check if directory
                    copy_asset_dir(full_asset, full_dest)
                except Exception:
                    os.makedirs(os.path.dirname(full_dest), exist_ok=True)
                    with asset_manager.open(full_asset) as src, open(full_dest, "wb") as dst:
                        shutil.copyfileobj(src, dst)

        activity.runOnUiThread(lambda: status_text.setText("Extracting TTS models (one-time setup)..."))
        copy_asset_dir("tts", tts_dir)

    # 2. Initialize sherpa-onnx (max_num_sentences=-1 allows unlimited text processing)
    model_path = os.path.join(tts_dir, "ljspeech.onnx")
    tokens_path = os.path.join(tts_dir, "tokens.txt")
    
    tts_config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=model_path,
                tokens=tokens_path,
                data_dir=espeak_dir,
            ),
            provider="cpu",
            num_threads=2,
        ),
        max_num_sentences=-1, # Process all sentences (unlimited text)
    )
    
    if not tts_config.validate():
        activity.runOnUiThread(lambda: status_text.setText("Config validation failed!"))
        return
        
    tts = sherpa_onnx.OfflineTts(tts_config)
    activity.runOnUiThread(lambda: status_text.setText("TTS Engine Loaded. Ready."))

    # 3. Pure Python WAV writer
    def save_wav(filename, samples, sample_rate):
        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(sample_rate)
            for s in samples:
                s = max(-1.0, min(1.0, float(s)))
                val = int(s * 32767)
                wf.writeframes(struct.pack('<h', val))

    # 4. Save to Public Music Folder via MediaStore (No broad permissions needed on Android 10+)
    def save_to_music_folder(source_wav_path, filename):
        try:
            resolver = activity.getContentResolver()
            values = ContentValues()
            values.put(MediaStore.Audio.Media.DISPLAY_NAME, filename)
            values.put(MediaStore.Audio.Media.MIME_TYPE, "audio/wav")
            values.put(MediaStore.Audio.Media.RELATIVE_PATH, Environment.DIRECTORY_MUSIC)
            values.put(MediaStore.Audio.Media.IS_PENDING, 1)

            uri = resolver.insert(MediaStore.Audio.Media.EXTERNAL_CONTENT_URI, values)
            
            out_stream = resolver.openOutputStream(uri)
            with open(source_wav_path, "rb") as in_file:
                chunk = in_file.read(8192)
                while chunk:
                    out_stream.write(chunk)
                    chunk = in_file.read(8192)
            out_stream.close()
            
            values.clear()
            values.put(MediaStore.Audio.Media.IS_PENDING, 0)
            resolver.update(uri, values, None, None)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    # 5. Generate & Play Click Handler
    class SpeakListener(dynamic_proxy(View.OnClickListener)):
        def onClick(self, view):
            text = str(text_input.getText())
            if not text.strip():
                activity.runOnUiThread(lambda: Toast.makeText(activity, "Please enter text", Toast.LENGTH_SHORT).show())
                return
                
            activity.runOnUiThread(lambda: [
                status_text.setText("Generating speech (this may take a moment for long text)..."),
                progress_bar.setVisibility(ProgressBar.VISIBLE),
                speak_btn.setEnabled(False),
                download_btn.setEnabled(False)
            ])
            current_wav_path[0] = None
            
            def run_tts():
                try:
                    gen_config = sherpa_onnx.GenerationConfig()
                    gen_config.sid = 0
                    gen_config.speed = 1.0
                    
                    audio = tts.generate(text, gen_config)
                    
                    if len(audio.samples) == 0:
                        activity.runOnUiThread(lambda: status_text.setText("Error generating audio."))
                        return
                        
                    wav_path = os.path.join(files_dir, "output.wav")
                    save_wav(wav_path, audio.samples, audio.sample_rate)
                    current_wav_path[0] = wav_path
                    
                    activity.runOnUiThread(lambda: status_text.setText("Playing..."))
                    
                    player = MediaPlayer()
                    player.setDataSource(wav_path)
                    player.prepare()
                    player.start()
                    
                    player.setOnCompletionListener(dynamic_proxy(MediaPlayer.OnCompletionListener)(
                        lambda mp: activity.runOnUiThread(lambda: [
                            status_text.setText("Finished playing. Ready to download or generate again."),
                            progress_bar.setVisibility(ProgressBar.GONE),
                            speak_btn.setEnabled(True),
                            download_btn.setEnabled(True)
                        ])
                    ))
                except Exception as e:
                    activity.runOnUiThread(lambda: [
                        status_text.setText(f"Error: {str(e)}"),
                        progress_bar.setVisibility(ProgressBar.GONE),
                        speak_btn.setEnabled(True)
                    ])
            
            threading.Thread(target=run_tts, daemon=True).start()

    # 6. Download Click Handler
    class DownloadListener(dynamic_proxy(View.OnClickListener)):
        def onClick(self, view):
            path = current_wav_path[0]
            if not path or not os.path.exists(path):
                Toast.makeText(activity, "No audio generated yet", Toast.LENGTH_SHORT).show()
                return
                
            activity.runOnUiThread(lambda: Toast.makeText(activity, "Saving to Music folder...", Toast.LENGTH_SHORT).show())
            
            def run_save():
                filename = f"PiperTTS_{os.path.getmtime(path)}.wav"
                success = save_to_music_folder(path, filename)
                if success:
                    activity.runOnUiThread(lambda: Toast.makeText(activity, "✅ Saved to Music folder!", Toast.LENGTH_LONG).show())
                else:
                    activity.runOnUiThread(lambda: Toast.makeText(activity, "❌ Failed to save.", Toast.LENGTH_LONG).show())
                    
            threading.Thread(target=run_save, daemon=True).start()

    speak_btn.setOnClickListener(SpeakListener())
    download_btn.setOnClickListener(DownloadListener())
