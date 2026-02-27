import numpy as np
import sounddevice as sd
import whisper
import queue
import time

class RealTimeSpeechToText:
    def __init__(self, model_name="tiny", sample_rate=16000):
        print(f"加载 Whisper {model_name} 模型...")
        self.model = whisper.load_model(model_name)
        print("模型加载完成！")
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.running = False
        self.recognized_text = []
    
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"音频状态: {status}")
        audio_data = indata[:, 0].astype(np.float32)
        self.audio_queue.put(audio_data)
    
    def _is_speech(self, audio_data, threshold=0.01):
        """语音活动检测"""
        rms = np.sqrt(np.mean(np.square(audio_data)))
        return rms > threshold
    
    def _add_punctuation(self, text):
        """添加标点符号"""
        if not text:
            return text
        text = text.strip()
        if text and text[-1] not in ['。', '！', '？']:
            text += '。'
        return text
    
    def recognize_audio(self):
        audio_buffer = []
        last_speech_time = time.time()
        
        while self.running:
            try:
                # 处理音频数据
                try:
                    chunk = self.audio_queue.get(block=False)
                    if self._is_speech(chunk):
                        audio_buffer.append(chunk)
                        last_speech_time = time.time()
                except queue.Empty:
                    pass
                
                # 3秒静音检测
                current_time = time.time()
                if len(audio_buffer) > 0 and (current_time - last_speech_time > 3.0):
                    audio_data = np.concatenate(audio_buffer)
                    if len(audio_data) > self.sample_rate * 0.5:
                        # 语音识别
                        result = self.model.transcribe(
                            audio_data,
                            language="zh",
                            fp16=False,
                            initial_prompt="中文对话，清晰标准的普通话"
                        )
                        
                        if result["text"] and len(result["text"]) > 1:
                            text_with_punctuation = self._add_punctuation(result["text"])
                            self.recognized_text.append(text_with_punctuation)
                            self.text_queue.put(text_with_punctuation)
                        
                        audio_buffer = []
                        last_speech_time = time.time()
                
                time.sleep(0.1)
                    
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(0.1)
    
    def display_text(self):
        print("\n实时语音转文字 Demo")
        print("====================")
        print("开始说话，文字将实时显示")
        print("按 Ctrl+C 停止并查看结果")
        print("====================\n")
        
        while self.running:
            try:
                text = self.text_queue.get(block=False)
                print(f"识别: {text}")
            except queue.Empty:
                time.sleep(0.1)
    
    def start(self):
        self.running = True
        
        # 启动识别线程
        import threading
        recog_thread = threading.Thread(target=self.recognize_audio)
        recog_thread.daemon = True
        recog_thread.start()
        
        # 启动显示线程
        display_thread = threading.Thread(target=self.display_text)
        display_thread.daemon = True
        display_thread.start()
        
        # 开始音频采集
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback,
            blocksize=int(self.sample_rate * 0.5)
        ):
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n停止中...")
                self.running = False
                time.sleep(1)
    
    def get_final_text(self):
        return " ".join(self.recognized_text)

if __name__ == "__main__":
    demo = RealTimeSpeechToText()
    try:
        demo.start()
    finally:
        final_text = demo.get_final_text()
        print("\n====================")
        print("完整结果:")
        print("====================")
        print(final_text)
        print("====================")
