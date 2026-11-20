# 分镜合成

已测试 Node 24.22.1、npm 12.2.1。运行 `npm ci` 安装锁定依赖。安装后从工程目录执行 `node -e "require('node:fs').mkdirSync('public/shots',{recursive:true})"` 创建素材目录（macOS、Linux、Windows 通用）。把视频放到 `public/shots/`，编辑 `film.json`，然后运行：

    npm run check
    npm start
    npm run still -- out/check.png --frame=15
    npm run render -- out/film.mp4

示例配置含两个占位路径。可增删、重排 shots；每段从源文件开头取 frames 帧，按合成 fps 计算时长，总帧数自动求和。fps 使用正整数，width 与 height 取正偶数。画面居中裁满输出尺寸。建议源素材采用带明确流时长的 MP4，换镜以帧为界。

title 填字符串会在第一镜显示，可用 null 隐藏。titlePosition 可选 top-left、top-right、bottom-left 或 bottom-right；省略时默认右下角。根据首镜主体所在位置选择留白角落。music 填 public/ 下音频相对路径或 null；视频原声始终静音。配乐至少覆盖整片，超出部分自动截断。无配乐的默认导出只包含视频流。check 会检测缺文件、缺音视频流、片段或配乐过短。

默认使用 Remotion 随包提供的 ffprobe，也可用 FFPROBE 环境变量指定可执行文件。首次出帧时 Remotion 可下载浏览器；设 REMOTION_BROWSER 为兼容 Chrome 的可执行文件路径即可使用现有浏览器。源文件和输出都在工程内，out/ 为默认导出目录。
