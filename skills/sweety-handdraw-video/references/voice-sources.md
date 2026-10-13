# 音色选择依据

核实日期：2026-10-13。没有找到足够依据支持“国内自媒体公认排名”，选择器按常见口播用途提供声音和同文试听，不用热度名称代替真实可用性。

当前本地合成参考覆盖清晰叙述、甜美女声、亲切男声、知性女声、温厚男旁白，以及三条故事成片使用的叙事声音。两条指定 B站片尾只算一个用户参考。声音名称代表使用方向，不是与真实人物身份的绑定或音质保证。

官方开源 Qwen3-TTS CustomVoice 可调用 Vivian、Serena、Uncle_Fu、Dylan、Eric 等预设，但当前 Base 参考合成接口不能把这些 ID 当作参考音频使用。需对应的 CustomVoice 模型与接口；不要添加实际上不可调用的占位音色。[官方 CustomVoice](https://github.com/QwenLM/Qwen3-TTS#custom-voice-generate)

Qwen3-TTS 支持 VoiceDesign 先设计声音，再用 Base 参考合成，可用于扩展原创合成参考。[官方流程](https://github.com/QwenLM/Qwen3-TTS#voice-design-then-clone)、[官方模型卡](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)

百炼 Cherry、Ethan、Maia、Eldric Sage 等是云端备选，需要账号、API Key与额度，不能把官网试听自动打包为克隆素材。[官方音色表](https://help.aliyun.com/zh/model-studio/qwen-tts-voice-list)、[调用条件](https://help.aliyun.com/zh/model-studio/non-realtime-tts-user-guide)

指定参考：[BV1SXZyYtEVy](https://www.bilibili.com/video/BV1SXZyYtEVy/)、[BV16UR1YuE6z](https://www.bilibili.com/video/BV16UR1YuE6z/)。两段共同片尾经对齐有高波形相关，支持复用同一片尾录音。用户记忆中的开场措辞与原声有差异，导入时以实际提取的逐字稿为准。源录音没有随公开包提供。
