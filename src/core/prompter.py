"""
提示词生成器模块
"""
from typing import Dict, Any, Optional
from openai import OpenAI
from src.config import Config
from src.styles import get_style_config, NO_TEXT_RULE
from src.utils.logger import logger

# 初始化 OpenAI 客户端
_api_config = Config.get_chat_api_config()
client = OpenAI(api_key=_api_config["api_key"], base_url=_api_config["base_url"])

PROMPT_INSTRUCTION_TEMPLATE = """请根据以下博客文章信息，设计一个**高质量的博客封面AI生图提示词**。

# 博客文章信息
- **标题**：{title}
- **描述（核心）**：{description}
- **标签**：{tags}
- **内容摘要**：{content}
- **主题色**：{theme_color}

# 设计要求（请严格执行）
1. **核心任务**：基于文章描述，提炼出一个最能代表文章核心价值的**具体视觉场景或物体**作为画面主体。
   - 不要使用抽象的概念（如“思考”、“连接”），要具象化（如“一个发光的灯泡”、“紧密咬合的齿轮”）。
   - 核心视觉元素必须与文章主题强相关，让读者一眼能看出文章大概讲什么。
2. **风格规范**：必须包含以下风格关键词：
   - 风格：{style}
   - 配色：{color_matching}
   - 视觉约束：{visual_rule}
   - 尺寸：{size}，{dpi}DPI高清
3. **构图要求**：
   - {content_ratio_requirement}
   - 必须包含关键词：画面饱满、少留白、主体占满画面、避免大块空白背景。
4. **颜色要求**：
   - 必须在提示词中明确写出主题色：{theme_color}。
   {background_color_requirement}
   {dark_mode_requirement}
5. **绝对禁令**：
   - {no_text_rule} (禁止任何文字、字母、数字、水印)。

# 输出格式
请直接输出一段**连贯的、描述性的中文提示词**，不要包含任何解释、序号或前缀（如“提示词：”）。
提示词应包含：核心视觉意象描述 + 风格关键词 + 构图关键词 + 颜色关键词 + 禁令关键词。
"""

def generate_image_prompt(
    md_info: Dict[str, Any],
    style_name: Optional[str] = None,
    background_color: Optional[str] = None,
    dark_mode_adaptive: Optional[bool] = None,
    content_ratio: Optional[float] = None,
    extra_prompt: Optional[str] = None
) -> str:
    """
    生成AI生图提示词
    """
    # 1. 准备参数
    style_name = style_name or Config.DEFAULT_STYLE
    style_config = get_style_config(style_name)
    
    bg_color = background_color if background_color is not None else Config.BACKGROUND_COLOR
    is_dark_mode = dark_mode_adaptive if dark_mode_adaptive is not None else Config.DARK_MODE_ADAPTIVE
    ratio = content_ratio if content_ratio is not None else Config.CONTENT_RATIO
    extra = extra_prompt or Config.EXTRA_PROMPT

    # 2. 构造 Prompt 指令
    content_pct = int(round(ratio * 100))
    background_pct = int(round((1 - ratio) * 100))
    
    # 构图要求
    content_ratio_req = f"""5.3. **画面占比与构图**：核心视觉元素（内容）约占画面 {content_pct}%，背景仅占 {background_pct}%；要求画面饱满、主体尽量填满画面、避免大块空白背景、留白尽量少。"""
    
    # 背景色要求
    if bg_color:
        bg_req = f"""5.1. **背景色要求**：图片背景色必须使用 {bg_color}，在提示词中明确说明背景色为 {bg_color}；"""
    else:
        bg_req = """5.1. **背景色要求**：背景色可以自由发挥，选择与主题色协调的柔和背景色；"""
    
    # 深色模式要求
    dark_req = """5.2. **深色模式适配**：图片需要适配深色和浅色两种模式，确保在深色背景下清晰可见；""" if is_dark_mode else ""

    # 图片尺寸描述 (仅用于提示词，实际尺寸由API参数控制)
    size_desc = "4:3" if Config.IMAGE_PROVIDER == "gemini" else "1280*720"

    prompt_instruction = PROMPT_INSTRUCTION_TEMPLATE.format(
        theme_color=md_info.get('theme_color', ''),
        style=style_config['style'],
        size=size_desc,
        dpi="300", # 固定
        color_matching=style_config['color_matching'],
        visual_rule=style_config['visual_rule'],
        no_text_rule=NO_TEXT_RULE,
        title=md_info.get('title', ''),
        description=md_info.get('description', ''),
        tags=','.join(md_info.get('tags', [])),
        content=md_info.get('clean_content', '')[:1000], # 截取前1000字符避免过长
        background_color_requirement=bg_req,
        dark_mode_requirement=dark_req,
        content_ratio_requirement=content_ratio_req
    )

    logger.info(f"🎨 风格预设：{style_name} ({style_config['style']})")
    
    # 增加调试日志
    logger.debug(f"🔍 Prompt 指令: {prompt_instruction[:500]}...")
    logger.debug(f"📊 输入信息 - 标题: {md_info.get('title')}, 描述长度: {len(md_info.get('description', ''))}")
    
    # 3. 调用 LLM 生成提示词
    try:
        response = client.chat.completions.create(
            model=Config.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt_instruction}],
            temperature=0.7,
            max_tokens=200
        )
        image_prompt = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"❌ 生成提示词失败: {str(e)}")
        raise

    # 4. 后处理提示词
    # 强制追加无文字规则
    if "无文字" not in image_prompt:
        image_prompt += f"，{NO_TEXT_RULE}"
    
    # 强制追加额外提示词
    if extra:
        image_prompt += f"，{extra}"
        
    logger.info(f"📝 生成提示词：{image_prompt}")
    return image_prompt
