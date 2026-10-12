# sweety-handdraw-video

安装一个 Skill，按主题或文章制作完整手绘讲解视频。

- 使用入口：[SKILL.md](SKILL.md)
- 项目说明、安装与样片：[GitHub README](https://github.com/threerocks/sweety-handdraw-video)
- 编写任务：[运行格式](references/runtime-contract.md)
- 内置依赖和冲突处理：[依赖路由](references/dependencies.md)

VoiceStudio 用于生成和编辑旁白，需单独安装并启动兼容的本机服务。已核对的导出音频可以离线复用。生成新图片还需图像工具、Bun 和 ExifTool；Python 与 FFmpeg 负责本地合成。内置的参考指南不需要另行安装为 Skills。
