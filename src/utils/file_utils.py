"""
文件处理工具模块
"""
import os
import re
from pathlib import Path
from typing import Dict, Any

SUPPORTED_EXTENSIONS = (".md", ".mdx")

def _strip_mdx(content: str) -> str:
    """去除 MDX/JSX 语法，保留可读文本用于分析。"""
    # 去掉 {...} 表达式（含一层嵌套）
    prev_content = ""
    while content != prev_content:
        prev_content = content
        content = re.sub(r"\{[^{}]*\}", " ", content)
        
    # 自闭合标签 <... />
    content = re.sub(r"<[^>]+/\s*>", " ", content)
    # 其余 HTML/JSX 标签，去掉标签本身保留内部文字
    content = re.sub(r"<[^>]+>", " ", content)
    return content

def parse_md_file(md_path: str, max_length: int = 8000) -> Dict[str, str]:
    """
    读取 Markdown 或 MDX 文件内容。

    Args:
        md_path: 文件路径（支持 .md 或 .mdx）
        max_length: 最大读取长度

    Returns:
        dict: 包含 raw_content 和 clean_content 的字典

    Raises:
        FileNotFoundError: 文件不存在或扩展名不是 .md/.mdx
    """
    path = Path(md_path)
    if not path.exists() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise FileNotFoundError(f"请输入有效的文件路径（后缀为 {', '.join(SUPPORTED_EXTENSIONS)}）")

    with open(path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # 先去除 MDX/JSX，再按 Markdown 清理
    text = _strip_mdx(raw_content)
    clean_content = re.sub(
        r"#{1,6} |\*\*|\*|`|```.*?```|<.*?>|\[.*?\]\(.*?\)",
        "",
        text,
        flags=re.DOTALL,
    )
    # 去除多余空行
    clean_content = "\n".join([line.strip() for line in clean_content.split("\n") if line.strip()])

    return {
        "raw_content": raw_content,
        "clean_content": clean_content[:max_length]
    }
