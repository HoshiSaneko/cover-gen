"""
内容分析模块
使用大模型自动分析Markdown内容，提取元数据
"""
import json
import re
from typing import Dict, Any, List
from openai import OpenAI
from src.config import Config
from src.utils.logger import logger

# 初始化 OpenAI 客户端
_api_config = Config.get_chat_api_config()
client = OpenAI(api_key=_api_config["api_key"], base_url=_api_config["base_url"])

ANALYSIS_PROMPT = """请分析以下博客文章内容，提取关键信息并返回JSON格式：

**核心要求**：必须抓住文章的核心重点和关键主题，不要被次要信息干扰。

要求（必须全部完成，不要遗漏任何字段）：
1. 从内容中提取或生成文章标题（如果没有明确的标题，根据内容的核心重点生成一个简洁的标题）
2. **最重要**：生成一段50-100字的文章描述/摘要
   - 描述必须突出文章的核心主题、关键技术点或主要观点
   - 优先提取：核心技术概念、主要功能、关键方法、核心工具等最重要的信息
   - 忽略次要的细节、示例代码、具体步骤等
   - 描述应该能让读者一眼看出文章的核心价值，这是生成封面图的关键信息
   - 不能为空或过于简单，必须包含实质性的核心内容
3. 提取3-5个关键词作为标签（tags），必须是数组格式
   - 标签应该反映文章的核心主题和技术领域
   - 优先选择最能代表文章重点的关键词
4. 根据文章的核心主题和重点内容，推荐一个适合的十六进制颜色作为主题色（theme_color）
   - 颜色必须符合**该篇文章**的独特主题和氛围，不同文章必须推荐**明显不同**的主题色
   - 根据文章领域与情感选择有区分度的颜色（如：前端/JS 可用琥珀/橙，Python/数据 可用青绿/Teal，设计/UI 可用紫/粉，运维/云 可用灰蓝，自然/环保 用绿/棕等），避免多篇文章都返回相同或相近的色号
   - **严格避免使用蓝色系**（#0000FF到#7F7FFF范围，除非内容确实与海洋、天空、科技等蓝色主题相关）
   - 优先选择：暖色系、中性色、冷色系等莫兰迪色系，且要与文章核心主题情感匹配

**重要**：必须返回完整的JSON格式，包含所有必需字段，不要添加任何解释文字。

返回格式（必须是有效的JSON）：
{{
    "title": "文章标题",
    "description": "文章描述",
    "tags": ["标签1", "标签2", "标签3"],
    "theme_color": "#颜色代码"
}}

文章内容：
{content}
"""

def analyze_content(md_content: str) -> Dict[str, Any]:
    """
    使用大模型分析Markdown内容，自动提取元数据
    
    Args:
        md_content: Markdown文件内容（clean_content）
        
    Returns:
        dict: 包含title, description, tags, theme_color的字典
    """
    prompt = ANALYSIS_PROMPT.format(content=md_content)
    
    logger.info(f"🤖 正在使用 {Config.CHAT_PROVIDER} ({Config.CHAT_MODEL}) 分析内容...")
    
    try:
        # Gemini 的 response_format 需要根据模型版本小心使用
        # 对于非 gemini-1.5-pro/flash 的模型，或者旧版本，可能不支持 json_object
        # 这里做个判断，或者简单地移除强制格式，靠 Prompt 约束
        
        kwargs = {
            "model": Config.CHAT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000, # 增加到 2000 防止 JSON 截断
        }
        
        # 仅对已知支持 json_object 的模型启用
        # 包括所有 gemini 模型 (通常都支持，或会忽略)，以及 gpt/qwen
        if "gemini" in Config.CHAT_MODEL or "gpt" in Config.CHAT_MODEL or "qwen" in Config.CHAT_MODEL:
             kwargs["response_format"] = {"type": "json_object"}
             
        response = client.chat.completions.create(**kwargs)
        
        result_text = response.choices[0].message.content.strip()
        
        # 更加鲁棒的 JSON 提取逻辑
        
        # 0. 先尝试简单清洗：去除首尾空白
        result_text = result_text.strip()

        # 1. 尝试直接从 ```json ... ``` 或 ``` ... ``` 提取
        json_str = result_text
        if "```json" in result_text:
            try:
                # 找到第一个 ```json
                start_idx = result_text.find("```json") + 7
                # 找到对应的结束 ```
                end_idx = result_text.find("```", start_idx)
                if end_idx != -1:
                    json_str = result_text[start_idx:end_idx].strip()
            except:
                pass
        elif "```" in result_text:
             try:
                start_idx = result_text.find("```") + 3
                end_idx = result_text.find("```", start_idx)
                if end_idx != -1:
                    json_str = result_text[start_idx:end_idx].strip()
             except:
                pass

        # 2. 如果还没提取出来或不是以 { 开头，尝试正则匹配最外层的 {}
        # 增加 re.DOTALL 以匹配跨行内容
        if not json_str.strip().startswith("{"):
            match = re.search(r"\{.*\}", result_text, re.DOTALL)
            if match:
                json_str = match.group(0)
        
        # 3. 常见错误修复
        # 有时候模型会在 JSON 末尾加省略号 ... 或逗号
        json_str = json_str.strip()
        if json_str.endswith("..."):
            json_str = json_str[:-3].strip()
        if json_str.endswith(","):
            json_str = json_str[:-1].strip()
            
        # 尝试修复未闭合的 string
        # 统计双引号数量，如果是奇数，尝试在末尾补一个 "
        # 这是一个非常粗糙的 heuristic，但对于简单的截断可能有效
        if json_str.count('"') % 2 != 0:
             # 检查最后是否是截断的 key 或 value
             # 如果最后字符不是 " or } or ]，那可能就是 string 没闭合
             if not json_str.endswith(('"', '}', ']')):
                  json_str += '"'

        # 尝试修复未闭合的 JSON (简单情况)
        if json_str.startswith("{"):
             # 简单的堆栈来检查括号平衡
             stack = []
             for char in json_str:
                 if char == '{': stack.append('{')
                 elif char == '}': 
                     if stack: stack.pop()
             
             # 补全缺失的 }
             json_str += "}" * len(stack)

        try:
            md_info = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️  JSON解析失败: {e}")
            logger.debug(f"原始返回: {result_text}")
            logger.debug(f"提取后字符串: {json_str}")
            
            # 最后的兜底：如果解析失败，尝试使用更宽松的解析库（如果已安装）或者简单的手动提取
            # 这里我们尝试一种极其简单的容错：如果是因为末尾有多余字符
            try:
                # 尝试找到最后一个 } 并截断
                last_brace = json_str.rfind("}")
                if last_brace != -1:
                    json_str_fixed = json_str[:last_brace+1]
                    md_info = json.loads(json_str_fixed)
                else:
                    raise e
            except:
                raise ValueError(f"AI返回的内容不是有效的JSON格式。提取内容: {json_str[:100]}...")

        
        # 验证必需字段
        required_fields = ["title", "description", "tags", "theme_color"]
        missing_fields = [field for field in required_fields if field not in md_info]
        if missing_fields:
            raise ValueError(f"AI分析结果不完整，缺少字段：{', '.join(missing_fields)}")
        
        logger.info(f"📊 内容分析完成：")
        logger.info(f"   标题：{md_info.get('title')}")
        logger.info(f"   主题色：{md_info.get('theme_color')}")
        logger.info(f"   标签：{', '.join(md_info.get('tags', []))}")
        
        return md_info

    except Exception as e:
        logger.error(f"❌ 内容分析出错: {str(e)}")
        raise
