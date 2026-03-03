# cover-gen - 智能博客封面生成器 🎨

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Models](https://img.shields.io/badge/Models-Qwen%20%7C%20Gemini-orange.svg)

**cover-gen** 是一款基于 AI 大模型的智能博客封面生成工具。它能深度阅读你的文章，提取核心视觉意象，并自动生成风格统一、构图精美的高质量封面图。

不再为寻找配图烦恼，让 AI 为你的每一篇文章定制专属封面。

---

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.10+，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置密钥

复制配置文件模板：

```bash
# macOS / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```ini
# --- 核心配置 ---
CHAT_PROVIDER=qwen          # 分析模型: qwen | gemini
IMAGE_PROVIDER=gemini         # 绘图模型: qwen | gemini

# --- API 密钥 ---
QWEN_API_KEY=sk-xxxxxxxx    # 阿里云 DashScope Key
GEMINI_API_KEY=AIzaSyxxxx   # Google AI Studio Key
```

### 3. 一键生成

```bash
# 基础用法 (交互式输入文件路径)
python main.py

# 指定文件路径
python main.py example/example.md

# 指定风格和背景色
python main.py example/example.md --style isometric --background "#1a1a1a"
```

### 4. 运行示例

```text
D:\cover-gen>python main.py example\example.md --extra-prompt minecraft 
 ℹ️ INFO: 📂 正在读取文件: example\example.md 
 ℹ️ INFO: 🤖 正在使用 qwen (qwen-turbo) 分析内容... 
 ℹ️ INFO: 📊 内容分析完成： 
 ℹ️ INFO:    标题：Minecraft 1.21: 险恶试炼更新详解 
 ℹ️ INFO:    主题色：#C15A3E 
 ℹ️ INFO:    标签：Minecraft, 1.21更新, 试炼密室, 自动合成器, 红石工程 
 ℹ️ INFO: 🧠 正在生成生图提示词... 
 ℹ️ INFO: 🎨 风格预设：isometric (等距3D风格) 
 ℹ️ INFO: 📝 生成提示词：一个由铜块和凝灰岩构成的复杂试炼密室结构，内部布满陷阱与宝箱，中央悬浮着一个闪烁红石光芒的自动合成器，周围环绕着风弹轨迹与重锤武器，背景为柔和的浅灰色调，画面采用等距3D风格，明亮清晰配色，几何感强，2.5D等距视角，画面饱满、少留白、主体占满画面、避免大块空白背景，主题色#C15A3E，适配深色和浅色模式，纯视觉图形设计。，无文字、无字母、无数字、无符号、无标签、无水印，纯视觉图形设计，minecraft 
 ℹ️ INFO: 🎨 正在调用 gemini (gemini-3.1-flash-image-preview) 生成封面图... 
 ℹ️ INFO: ✅ 封面图生成完成 | ⏱️ 耗时: 28.6s | 📦 大小: 311.4KB | 📂 路径：D:\cover-gen\output\Minecraft 1.21_ 险恶试炼更新详解.jpg 
 
 ✨ 全部完成！图片已保存至: D:\cover-gen\output\Minecraft 1.21_ 险恶试炼更新详解.jpg
```

![Minecraft 1.21 封面示例](example/Minecraft%201.21_%20险恶试炼更新详解.jpg)

---

## 🛠️ 命令行参数详解

| 参数 | 说明 | 示例 |
| :--- | :--- | :--- |
| `md_path` | Markdown 或 MDX 文件路径 | `example/post.md` |
| `--style` | 指定风格预设 | `--style tech_abstract` |
| `--list-styles` | 列出所有可用风格预设 | `python main.py --list-styles` |
| `--background` | 指定背景色 (Hex) | `--background "#ffffff"` |
| `--dark-mode` | 是否适配深色模式 | `--dark-mode true` |
| `--ratio` | 内容主体占比 (0.1 - 0.9) | `--ratio 0.7` |
| `--extra-prompt` | 强制追加的额外提示词 | `--extra-prompt "high quality"` |

---

## 🎨 风格预设 (Styles)

cover-gen 内置了多种精心调教的 Prompt 风格，满足不同类型文章的需求：

| 风格代码 | 名称 | 适用场景 |
| :--- | :--- | :--- |
| **flat** | 扁平插画风 | 通用，适合大多数技术/生活博客 |
| **minimal** | 极简风 | 适合文艺、随笔、简单说明 |
| **isometric** | 2.5D等距 | 适合架构图、技术原理、城市规划 |
| **tech_abstract** | 科技抽象 | 适合AI、区块链、硬核技术文章 |
| **cyberpunk** | 赛博朋克 | 适合未来主义、游戏、科幻话题 |
| **glassmorphism** | 玻璃拟态 | 适合UI设计、现代软件介绍 |
| **hand_drawn** | 手绘插画 | 适合教程、笔记、轻松话题 |

更多风格请运行 `python main.py --list-styles` 查看。

---

## 📝 许可证

MIT License
