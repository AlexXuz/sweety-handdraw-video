# 声音与本机依赖

运行需要 Python 3.9+、Pillow、NumPy、SciPy、requests、ffmpeg/ffprobe。正文手写字体优先 macOS Hannotate；字幕使用独立的常规中文字体。字体回退不能当作手写风格已验收，不把系统商业字体复制进包。

## 本地配音能力

优先使用当前已配置可用的本地配音能力。VoiceStudio 不可达时可使用任务已明确配置的本地 VoxCPM2；两者都不可用且没有现成音频时，报告能力缺口。偏好超时不等于可以凭空生成声音、购买或安装服务。已有核对过的整篇旁白及其时间戳可离线合成。

VoiceStudio 适配器默认访问本机 `http://127.0.0.1:3900`，读取当前引擎后才生成，当前配置为 `mlx-audio` / `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16`。它不启动应用、不改引擎、不下载模型、不读凭据。

```bash
python3 scripts/voice_studio.py JOB --transcribe
```

声音目录 `assets/voices/catalog.json` 提供 `iapetus`、`sweet-student`、`friendly-man`、`calm-woman`、`warm-elder`、`story-narrator`、`bilibili-outro`。除需导入原片的 bilibili-outro 外，包内其余声音是合成参考，三条故事成片归为一个 `story-narrator`。Iapetus 来自用户的合成附件，通过本地模型参考合成，不是原生 Gemini 接口。

自定义声音用 `reference_audio/reference_text`；文本必须准确。不要把音频或凭据上传到未经授权的服务。整篇旁白按完整文本、参数、模型和参考音频哈希缓存，未追踪的现有音频不覆盖。ASR同音字须结合原文判断；识别完整不等于主观听感验收。

## 同文试听与指定参考

七个合成参考均有 `assets/voices/previews` 同文试听，实际由本地 VoxCPM2 生成；换后端重新合成仍可能改变听感。常见口播用途与官方可调用音色的区别见[音色依据](voice-sources.md)。

`bilibili-outro` 将两条指定 B站视频的共用片尾合并为一个选项，包内旧合成试听仅供回溯，禁止当作指定原片音色的生产参考；未导入原片录音时该选项不可选。原视频录音与原始逐字稿只保留在来源任务中，不复制进安装包。使用前必须导入用户指定的原片录音，准确记录清理过程及来源；不可拿新合成样音替代原始参考。没有证据时不声称官方授权、纯干声或完全复刻。

```bash
python3 scripts/import_voice.py JOB --id bilibili-outro --name "片尾解说" --audio reference.wav --transcript reference.txt --kind source_recording
```

导入结果在 `options/local-voices.json`，仅覆盖该任务的同名参考。参考文本必须逐字对应录音，不以记忆中的口号替换实际措辞。

## 已安装的 VoxCPM2

当前 Python 环境须已有 `mlx-audio`、`mlx`、`soundfile` 及本地模型。任务设置 `voxcpm:{"model_path":"实际已安装的模型目录","voice":"story-narrator","timesteps":10,"cfg_value":2.0}`，用该环境执行：

```bash
python scripts/voxcpm_voice.py JOB
```

适配器读取同一参考目录，按音频、文本、模型路径和参数缓存，不下载模型或改变 VoiceStudio。两种适配器都把全部 beats 的文本按原顺序合并为一次完整生成请求，目标是 `narration.source`（未配置时写 `inputs/narration/master.wav`）。VoxCPM2 默认 `mode:combined`，以原参考和准确逐字稿共同约束声音；`reference` 模式仅在明确选择时使用。当参考与稿件开头重合时，continuation 容易跳过开头，必须另查。`max_tokens` 默认6500，可按已安装模型能力显式设置；这只是上限，不能证明实际生成完整。生成后检查实际时长、全文、句尾、漏读和重复，再按[连续旁白约定](continuous-narration.md)制作 alignment，最后编排画面。

## 六款手、仅画笔与广告

`assets/hands/catalog.json` 提供六款手臂与 `pen-only` 完整画笔，全部有美术与隐私记录。手臂按笔尖到手腕距离校准尺度，让最上方落笔时前臂底边仍在画外。`pen-only` 的 `kind:pen` 不执行前臂检查，但笔尖仍须对齐。

`hand.pen_text` 最多16个字符，只在实测笔杆段排版。保留原文、不自动缩写；上限不等于细笔杆上一定可读，长广告优先选宽笔杆或仅画笔。`pen_text_color` 可覆盖预设颜色。自定义手提供 `source/nib/wrist`，广告再提供 `label_segment/label_height`；自定义仅画笔提供 `kind:pen/source/nib/scale`。所有缩放必须为正的有限数。

## 图像隐私

内置原脚本由 Bun 执行，本流程要求 ExifTool，避免隐式安装 sharp。执行 `python3 scripts/clean_image.py image.png --audit privacy.json`：先执行随包隐私清理，再去除模拟相机字段，核验元数据与残留扩展属性。缺依赖时准确报告，不静默跳过。

## 原片音色与纯旁白验收

先检查原片参考本身是否混有配乐、风声、底噪。必要时人声分离或降噪，保留原始输入、处理参数及前后哈希；降噪可能伤及音色，不能仅凭残差小或 ASR 完整通过。参考导入后音频或逐字稿改变必须重新导入；生成记录保存实际参考路径、哈希、模式与全部参数。

指定原片音色先做同文对照与另一段正文短样，再做完整连续旁白。按相近响度比较原片、清理后原声、合成短样与长段开头/中间/结尾。用户未认可的合成试听不能替代原片，也不能标成已验证的主力音色。无背景音乐只证明没有额外混音层；旁白本身的底噪、嗡声、合成伪影与漏字须单独检查。未实际听音或没有用户听感反馈时，状态保持待听感验收，不允许用信号指标、ASR 或文件可播放宣称音色一致或绝对无杂音。

## 本机主力音色

个人声音目录位于 `~/.local/share/sweety-handdraw-video/voices/catalog.json`，与可分发 Skill 包分开。该目录只有在用户明确指定、完成同文/正文短样及长段听感验收后才写入；`default` 表示本机主力音色。声音选择默认方案优先采用 `load_voices` 返回的 `preferred: true` 项，用户明确选择与任务内导入优先。目录中记录实际参考、逐字稿、哈希、清理过程、试听样本和验收范围，未经验收的参数不得沿用“已通过”标记。原片录音不放入公共包。

已验收配置可包含 `enhancement_model_path`，仅指向已经安装的本地 DeepFilterNet3 模型。适配器将其权重哈希纳入生成缓存，48kHz 后处理必须保持样本数；不自动下载模型。处理本身不会设置听感通过，新生成的正文仍需验收。
