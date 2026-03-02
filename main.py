"""
cover-gen - 博客封面图生成工具
"""
import sys
import argparse
from src.config import Config
from src.styles import STYLE_PRESETS
from src.utils.logger import logger
from src.utils.file_utils import parse_md_file
from src.core.analyzer import analyze_content
from src.core.prompter import generate_image_prompt
from src.core.imager import generate_blog_cover

def main():
    parser = argparse.ArgumentParser(description="cover-gen - 博客封面图生成工具")
    parser.add_argument("md_path", nargs="?", help="Markdown 或 MDX 文件路径")
    parser.add_argument("--style", help=f"风格预设 (默认: {Config.DEFAULT_STYLE})")
    parser.add_argument("--list-styles", action="store_true", help="列出所有可用风格")
    parser.add_argument("--background", help="背景色 (例如 #cccccc)")
    parser.add_argument("--dark-mode", choices=["true", "false"], help="是否适配深色模式")
    parser.add_argument("--ratio", type=float, help="内容占比 (0.0~1.0)")
    parser.add_argument("--extra-prompt", help="额外提示词")
    
    args = parser.parse_args()

    # 列出风格
    if args.list_styles:
        logger.info("🎨 可用风格预设：")
        for s in STYLE_PRESETS.keys():
            prefix = "-> " if s == Config.DEFAULT_STYLE else "   "
            print(f"{prefix}{s}")
        sys.exit(0)

    # 获取文件路径
    md_path = args.md_path
    if not md_path:
        # 尝试交互式输入
        try:
            md_path = input("📄 请输入 MD 文件路径: ").strip().strip('"').strip("'")
        except KeyboardInterrupt:
            sys.exit(0)
    
    if not md_path:
        logger.error("❌ 未提供文件路径")
        print("\n使用方法:")
        print("  python main.py <file_path> [options]")
        sys.exit(1)

    # 处理参数
    dark_mode = None
    if args.dark_mode is not None:
        dark_mode = args.dark_mode == "true"
        
    if args.ratio is not None and (args.ratio <= 0 or args.ratio >= 1):
        logger.error("❌ --ratio 必须在 0 到 1 之间")
        sys.exit(1)

    try:
        # 1. 解析文件
        logger.info(f"📂 正在读取文件: {md_path}")
        file_content = parse_md_file(md_path, Config.MAX_CONTENT_LENGTH)
        
        # 2. 分析内容
        md_info = analyze_content(file_content["clean_content"])
        # 合并原始内容用于后续处理
        md_info["clean_content"] = file_content["clean_content"]
        
        # 3. 生成提示词
        logger.info("🧠 正在生成生图提示词...")
        image_prompt = generate_image_prompt(
            md_info,
            style_name=args.style,
            background_color=args.background,
            dark_mode_adaptive=dark_mode,
            content_ratio=args.ratio,
            extra_prompt=args.extra_prompt
        )
        
        # 4. 生成图片
        save_path = generate_blog_cover(image_prompt, md_info["title"])
        
        print(f"\n✨ 全部完成！图片已保存至: {save_path}")
        
    except KeyboardInterrupt:
        print("\n🚫 操作已取消")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
