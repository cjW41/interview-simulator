# 测试库导入和基本功能
print("开始测试库导入...")

try:
    import numpy as np
    print("✓ numpy 导入成功")
except Exception as e:
    print(f"✗ numpy 导入失败: {e}")

try:
    import sounddevice as sd
    print("✓ sounddevice 导入成功")
    print(f"  可用音频设备: {len(sd.query_devices())}")
except Exception as e:
    print(f"✗ sounddevice 导入失败: {e}")

try:
    import whisper
    print("✓ whisper 导入成功")
    # 测试模型加载
    model = whisper.load_model("tiny")
    print("✓ Whisper 模型加载成功")
except Exception as e:
    print(f"✗ whisper 导入或模型加载失败: {e}")

print("\n测试完成！")
