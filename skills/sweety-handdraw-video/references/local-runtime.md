# 声音与本机依赖

运行需要 Python 3.9+、Pillow、NumPy、SciPy、requests、ffmpeg/ffprobe。字体优先 macOS Hannotate，其后才是可读性回退；字体回退不能当作手写风格已验收。不把系统商业字体复制进包。

## 必需 VoiceStudio

VoiceStudio 未安装时没有旁白生成能力；服务未启动或引擎不匹配也应明确停止，不静默换外部服务。用户可通过 VoiceStudio 编辑、试听并导出旁白，准确文本和逐段文件必须对应。

适配器默认访问本机 `http://127.0.0.1:3900`，读取当前引擎后才生成。当前适配配置为 `mlx-audio` / `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16`。它不启动应用、不改引擎、不下载模型、不读凭据。

```bash
python3 /path/to/sweety-handdraw-video/scripts/voice_studio.py /path/to/job --transcribe
```

`voice_studio.voice` 对应 `assets/voices/catalog.json`：`iapetus`（默认）、`sweet-student`、`friendly-man`、`calm-woman`、`warm-elder`。这些是合成参考音色；默认 Iapetus 由用户附件转换，是在 VoiceStudio 中参考合成，并非原生 Gemini 接口。

自定义声音用 `reference_audio/reference_text`；参考文本必须准确。不要把真人音频或凭据上传到未经授权的服务。每句按文本、参数、模型和参考音频哈希缓存；未追踪的现有音频不会被覆盖。ASR同音字须结合原文判断，ASR不等于主观听感验收。

## 六款手与广告文字

素材和校准位于 `assets/hands/catalog.json`，全部在强制美术指导后重新生成。`hand.preset` 默认 `navy`；其它为 `diamond-woman/child-pencil/waner-brush/teacher-pen/cardigan-fountain`。

按笔尖到手腕距离校准显示尺度，并设最小比例，让最上方落笔时前臂底部仍在画外。自定义 `scale` 过小会被提高至安全值。不同材质的衣袖保持自然宽度，不宣称不同款轮廓逐像素一致。

`hand.pen_text` 在各款实测笔杆段排版，最多20字符；这只是上限，实际需按视频观看尺寸检查可读性，保留指定原文，过长时先调整笔杆排版，不擅自缩写名称。`pen_text_color` 可覆盖预设颜色。用户自定义手图须提供 `source/nib/wrist`，需要广告文字时再提供 `label_segment/label_height`。都须通过本任务的美术指导记录和前臂边界检查。

## 图像隐私运行条件

无需安装外部隐私 Skill。内置原脚本由 Bun 执行，本流程强制要求 ExifTool，避免隐式安装 sharp。运行 `python3 scripts/clean_image.py /path/to/image.png --audit /path/to/privacy.json`；它先执行随包隐私清理，再去除模拟相机字段并报告残留扩展属性。两者缺少时报告依赖，不静默跳过。
