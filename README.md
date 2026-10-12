# sweety-handdraw-video · 主题手绘视频

把一个主题、一篇文章或一段讲解稿，做成有旁白、有封面、逐笔画出来的讲解视频。

**模型负责讲清楚与画什么；本地工具负责怎么画、何时画、如何合成。** 每次按内容重新设计，不套固定页数、时长和人物。

```bash
npx skills add threerocks/sweety-handdraw-video --skill sweety-handdraw-video
```

[看样片](https://github.com/threerocks/sweety-handdraw-video/releases/tag/v1.0.0) · [下载安装包](https://github.com/threerocks/sweety-handdraw-video/releases/download/v1.0.0/sweety-handdraw-video-v1.0.0.zip) · [制作规则](skills/sweety-handdraw-video/SKILL.md) · [验证范围](docs/validation.md)

## 看效果

### 《墨菲定律》

约2分05秒，8个画面、24段口播。从没带伞和文件打不开讲起，解释准备如何降低失误的代价，再落到清单、备份和提前试一次。示例使用淡彩速写、女性碎钻长甲手、笔杆定制文字与 Iapetus 参考音色。

[![墨菲定律封面](docs/media/murphy-cover.jpg)](https://github.com/threerocks/sweety-handdraw-video/releases/download/v1.0.0/murphy-law.mp4)

![描线、填色与文字](docs/media/murphy-drawing.gif)

GIF 无声循环，来自实际导出的视频。[下载有声完整样片](https://github.com/threerocks/sweety-handdraw-video/releases/download/v1.0.0/murphy-law.mp4)。

![完整页面](docs/media/murphy-final.jpg)

示例中的角色、布局、橙色和广告名称不属于默认模板。新主题重新设计；修订同一条片时可以复用已认可的图和声音。

## 你说，它做

| 你的要求 | 制作方式 |
|---|---|
| “用手绘视频讲清楚沉没成本” | 判断讲解路线，设计生活场景与因果关系，生成口播、画面和成片 |
| “把这篇文章变成讲解视频” | 先保留文章事实与限定，再编排适合听和看的短段落 |
| “换成女性手，在笔上印我的名字” | 使用校准手部预设，把指定文字排到笔杆上，检查正常尺寸可读性 |
| “这页字被裁掉了，重做” | 修对应文字层与布局，保留已通过的图片和配音，重渲染并核对 |

## 安装一个 Skill 即可

五项制作依赖已经内置，用户不需要再安装它们：

| 内置依赖 | 用途 |
|---|---|
| sweety-image-art-direction | 每张图的美术指导：主体、接触、构图、比例与观看主次 |
| hand-drawn-styles | 手绘风格的完整配方与参考锚点 |
| omniailab-ai-director | 导演规划、审美、声画关系和终审 |
| huashu-art-motion | 命中艺术动效题材时使用对应方法 |
| sweety-image-privacy | 清理生成图的隐私元数据并记录残留边界 |

采用固定版本的随包快照。依赖指南统一为 `GUIDE.md`，整个安装目录只有一个 `SKILL.md`；不会注册五个额外 Skill，也不在运行时悄悄更新上游。来源、许可证、改动与哈希都在[依赖说明](skills/sweety-handdraw-video/references/dependencies.md)和[来源清单](THIRD_PARTY_NOTICES.md)。

内置的是制作资料和运行代码，**仍需以下软件或能力**：

- **VoiceStudio**：生成、编辑和导出旁白。未安装或未启动，无法生成新旁白；已有核对过的导出音频可离线合成。不会自动切换声音供应商。
- **图像生成能力**：默认 Codex 内置生图。每张新图必须先经过美术指导。
- **Python 3.9+、FFmpeg/ffprobe 和中文字体**：用于描线、排版和合成。推荐在任务虚拟环境安装 `scripts/requirements.txt`。
- **Bun 与 ExifTool**：执行随包图像隐私清理。流程会删除原清理脚本写入的模拟相机字段。

当前 VoiceStudio 适配器面向本机 HTTP API，默认 `http://127.0.0.1:3900`，已适配 `mlx-audio / Qwen3-TTS-12Hz-1.7B-Base-bf16`。需要兼容的 `/engines/tts`、`/generate` 和可选 `/transcribe` 接口。并非任何同名软件都兼容，详见[接入要求](skills/sweety-handdraw-video/references/local-runtime.md)。不自动下载模型或修改全局引擎。

手动安装时，把 `skills/sweety-handdraw-video` **整个文件夹**复制到工具的个人 Skills 目录。例如 Codex 使用 `~/.codex/skills/sweety-handdraw-video`。更新前备份已有目录；不要只复制入口文件。

## 开始使用

安装后把需求发给 Agent：

```text
使用 $sweety-handdraw-video，把“墨菲定律”讲给普通成年人听。
从生活里的困扰切入，讲清机制与可执行的准备方法。
```

```text
使用 $sweety-handdraw-video，把下面的文章做成视频，保留重要条件和数据。
使用女性手臂，在笔杆上印 @leo_xiaolei。
```

不指定时采用：简体中文、1920×1080、30fps、深蓝袖马克笔和 Iapetus 参考音色。片长由讲解和实际配音决定。固定1秒封面：前0.5秒静止，后0.5秒渐隐，随后进入正文与旁白。

### 六款手、五款声音

![六款手部预设](docs/media/hand-presets.jpg)

手部：深蓝袖马克笔、女性柔粉碎钻长甲、儿童彩铅、上官婉儿灵感毛笔、白衬衫中性笔、针织袖钢笔。支持定制笔杆文字；前臂裁切边留在画外。

声音：清晰叙述 Iapetus、甜美学姐、亲切男讲师、知性女讲师、温厚男旁白。均为合成参考音色；Iapetus 通过参考音频在 VoiceStudio 合成，**不是直接调用 Gemini 原生 TTS**。声音名称和描述是选用方向，不能代替实际试听。

## 怎么做，怎么检查

模型先判断内容适合什么叙事和画面。常见生活概念默认评估“错误或困扰 → 概念 → 机制 → 行动 → 收束”；不适用时重新规划，不能硬套。

插画由模型看图标注语义部位，按顺序完成全部轮廓，再按相同顺序填色。文字逐字隔离，笔画间抬笔；颜色只在笔刷经过范围出现。字形按真实边界排版，保留四边余量，避免中文底部和英文下伸部分被截掉。

配音决定时间线。先检查代表片段，再导出整片。程序检查时序、覆盖、画布边界、字幕、音画完整性；模型还要查看成片，审查内容、语义分区、遮挡和阅读节奏。主观听感、情绪和学习效果分别记录，未检查不写“通过”。

最终交付：MP4、封面 PNG、SRT、口播稿与检查记录。`finalize` 会拒绝检查缺失、素材变更后沿用旧记录、运行测试夹具冒充成片等情况。

## 开发与验证

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r skills/sweety-handdraw-video/scripts/requirements.txt
python skills/sweety-handdraw-video/scripts/validate_package.py
python skills/sweety-handdraw-video/scripts/test_drawing_contract.py
python skills/sweety-handdraw-video/scripts/smoke_test.py --output /tmp/handdraw-smoke-new
```

最后一个命令会创建新的测试目录，需 FFmpeg 与中文字体。它验证运行行为，不是成片观感验收。生成安装包：`python3 tools/package.py --output dist`。

目前完整流程在 macOS 验证；附带 Linux CI，用于验证依赖完整性、字形与绘制回归和短片合成。Windows 与其他 VoiceStudio 后端未完成整流程验证。字形描线不保证规范书法笔顺，任意新题材仍需实际检查。

## 致谢与许可

主项目代码与文档采用 MIT。内置依赖保留各自版权和许可证，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。感谢花叔艺术动效、OmniAiLab AI导演、手绘风格库和美术指导提供的方法。AI 生成手部素材及合成参考音频单独说明来源，不宣称真人身份、官方角色授权或普遍输出质量保证。
