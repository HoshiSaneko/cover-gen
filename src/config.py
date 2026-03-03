"""
全局配置模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# 加载 .env 文件
load_dotenv()

class Config:
    # --- 基础路径 ---
    ROOT_DIR = Path(__file__).parent.parent
    OUTPUT_DIR = ROOT_DIR / "output"  # 默认输出目录
    DOCS_DIR = ROOT_DIR / "docs"
    
    # --- 服务提供商配置 ---
    # 聊天模型提供商: qwen | gemini
    CHAT_PROVIDER = os.getenv("CHAT_PROVIDER", "qwen").strip().lower()
    # 生图模型提供商: qwen (Wan) | gemini (Imagen)
    # 如果未设置，默认跟随 CHAT_PROVIDER (如果是 gemini 则用 gemini，否则用 qwen)
    IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", CHAT_PROVIDER).strip().lower()

    # --- API 密钥 ---
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "").strip()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

    # --- API 地址 ---
    # Qwen (OpenAI Compatible for Chat)
    QWEN_CHAT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # Qwen (Wan Image Gen)
    QWEN_IMAGE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    # Qwen (Wanx v1 Image Gen)
    QWEN_IMAGE_API_URL_V1 = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    
    # Gemini (OpenAI Compatible for Chat)
    GEMINI_CHAT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
    # Gemini (Imagen Image Gen - REST)
    # 这里的URL需要配合具体的模型版本
    GEMINI_IMAGE_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

    # --- 模型名称 ---
    # 聊天模型
    CHAT_MODEL_QWEN = "qwen-turbo"
    CHAT_MODEL_GEMINI = "gemini-3-flash-preview" 
    CHAT_MODEL = os.getenv("CHAT_MODEL", CHAT_MODEL_GEMINI if CHAT_PROVIDER == "gemini" else CHAT_MODEL_QWEN).strip()

    # 生图模型
    IMAGE_MODEL_QWEN = "wan2.6-t2i" 
    # Gemini 2.0 Flash 原生支持生图，速度快 (Nano Banana)
    IMAGE_MODEL_GEMINI = "gemini-3.1-flash-image-preview" 
    # IMAGE_MODEL_GEMINI = "imagen-3.0-generate-001" # Imagen 3
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", IMAGE_MODEL_GEMINI if IMAGE_PROVIDER == "gemini" else IMAGE_MODEL_QWEN).strip()

    # --- 生成参数 ---
    # 默认风格
    DEFAULT_STYLE = os.getenv("DEFAULT_STYLE", "isometric")
    # 内容占比 (0.1 - 0.9)
    CONTENT_RATIO = float(os.getenv("CONTENT_RATIO", "0.6"))
    # 是否适配深色模式
    DARK_MODE_ADAPTIVE = os.getenv("DARK_MODE_ADAPTIVE", "true").lower() == "true"
    # 背景色 (空表示自动)
    BACKGROUND_COLOR = os.getenv("BACKGROUND_COLOR", "")
    # 额外提示词
    EXTRA_PROMPT = os.getenv("EXTRA_PROMPT", "")
    # 禁止的提示词（负向提示词，不希望出现在画面中的内容，逗号或空格分隔）
    NEGATIVE_PROMPT = os.getenv("NEGATIVE_PROMPT", "text, watermark, low quality, blurry, distorted, ugly, bad anatomy").strip()

    # --- 输出设置 ---
    # 图片尺寸
    IMAGE_SIZE_QWEN = "1024*768" # Qwen Wan 2.1 支持的尺寸
    IMAGE_SIZE_GEMINI = "4:3"    # Gemini (Imagen) 宽高比
    
    # 是否压缩图片
    ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
    JPG_QUALITY = int(os.getenv("JPG_QUALITY", "85"))
    
    # 分析内容最大长度
    MAX_CONTENT_LENGTH = 8000

    @classmethod
    def validate(cls):
        """验证配置有效性"""
        errors = []
        if cls.CHAT_PROVIDER not in ("qwen", "gemini"):
            errors.append(f"不支持的 CHAT_PROVIDER: {cls.CHAT_PROVIDER}")
        
        if cls.IMAGE_PROVIDER not in ("qwen", "gemini"):
            errors.append(f"不支持的 IMAGE_PROVIDER: {cls.IMAGE_PROVIDER}")

        if cls.CHAT_PROVIDER == "qwen" and not cls.QWEN_API_KEY:
            errors.append("CHAT_PROVIDER=qwen 需要 QWEN_API_KEY")
        
        if cls.CHAT_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("CHAT_PROVIDER=gemini 需要 GEMINI_API_KEY")

        if cls.IMAGE_PROVIDER == "qwen" and not cls.QWEN_API_KEY:
            errors.append("IMAGE_PROVIDER=qwen 需要 QWEN_API_KEY")
            
        if cls.IMAGE_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("IMAGE_PROVIDER=gemini 需要 GEMINI_API_KEY")
            
        if errors:
            raise ValueError("\n".join(errors))

    @classmethod
    def get_chat_api_config(cls) -> Dict[str, str]:
        """获取聊天 API 配置"""
        if cls.CHAT_PROVIDER == "gemini":
            return {"api_key": cls.GEMINI_API_KEY, "base_url": cls.GEMINI_CHAT_BASE_URL}
        return {"api_key": cls.QWEN_API_KEY, "base_url": cls.QWEN_CHAT_BASE_URL}

# 初始化时验证
try:
    Config.validate()
except ValueError as e:
    # 仅在运行时抛出，允许导入
    pass
