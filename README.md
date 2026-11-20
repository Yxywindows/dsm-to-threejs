# dsm-to-threejs

一个用于三维场景重建与展示的 Codex skill。它从多视角照片、扫描或已有模型出发，先辨认地物与空间关系，再根据具体疑点选择验证方法。交付可以是可编辑模型、three.js 网页，也可以是带有真实摄影机运动的 Remotion 宣传片。

## 安装

在 Codex 中输入：

> 用 skill-installer 从 GitHub 安装 Yxywindows/dsm-to-threejs 仓库的 skills/dsm-to-threejs 目录。

安装完成后重启 Codex 以加载技能。使用仓库里的[技能目录](skills/dsm-to-threejs/SKILL.md)可以直接查看完整工作流。

## 使用示例

- **从实拍建模**：「用 $dsm-to-threejs 根据这组三视角照片重建步行桥。先判断双塔、拉索与桥面之间的位置关系，再选机位与原图核对。」
- **从模型拍片**：「用 $dsm-to-threejs 把这个 Blender 场景拍成 20 秒竖屏宣传片。用 Remotion，从街道推进到建筑入口，最后交付 MP4 和可编辑工程。」
- **交互展示**：「把这个 GLB 做成可旋转、缩放的 three.js 网页，并检查它在浏览器里的材质和构图。」

## 成片流程

先用目标画幅试拍，再从源场景渲染镜头。镜头顺序、取用帧数、标题与可选配乐都可在 Remotion 工程中调整。导出后，可以对实际解码帧、画幅、时序和声音做检查，再用联系表复核主体与字幕。只有选择视频路线才需要视频工具。[成片指南](skills/dsm-to-threejs/references/scene-film.md) · [Remotion 模板](skills/dsm-to-threejs/assets/remotion-starter/README.md)

## 南京眼步行桥

这支 24 秒短片使用基于多视角实拍重建的模型。从江心洲弯引桥切到桥面，一路穿过近侧环塔，最后拉远看双塔与索面。江岸和植被用于示意。

https://github.com/user-attachments/assets/a38a4831-dbcc-4143-b502-69c701c8da79

[下载 1080p 原片](https://github.com/Yxywindows/dsm-to-threejs/releases/download/v1.0.0/nanjing-eye-1080p.mp4) · [在作者主页观看](https://github.com/Yxywindows#nanjing-eye-footbridge)
