"""
图片生成模块
"""
import os
import re
import time
import base64
import requests
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

from src.config import Config
from src.utils.logger import logger

def generate_blog_cover(image_prompt: str, md_title: str) -> str:
    """
    生成博客封面图
    
    Args:
        image_prompt: 生图提示词
        md_title: 博客标题（用于生成文件名）
        
    Returns:
        str: 保存的图片路径
    """
    # 1. 准备保存路径
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    file_ext = ".jpg" if Config.ENABLE_COMPRESSION else ".png"
    safe_title = re.sub(r"[\/:*?\"<>|]", "_", md_title)
    file_name = f"{safe_title}{file_ext}"
    save_path = Config.OUTPUT_DIR / file_name

    logger.info(f"🎨 正在调用 {Config.IMAGE_PROVIDER} ({Config.IMAGE_MODEL}) 生成封面图...")
    start_time = time.time()

    try:
        if Config.IMAGE_PROVIDER == "gemini":
            # 根据模型名称判断使用哪种 API
            if "flash" in Config.IMAGE_MODEL.lower():
                image_data = _generate_gemini_flash(image_prompt)
            else:
                image_data = _generate_imagen(image_prompt)
        else:
            image_data = _generate_qwen(image_prompt)
            
        # 2. 保存图片
        # 如果是 JPG，需要先保存为 PNG 再压缩（或直接保存）
        # 这里统一先保存为临时文件
        temp_path = save_path.with_suffix(".png")
        
        with open(temp_path, "wb") as f:
            f.write(image_data)
            
        # 3. 压缩处理 (如果启用)
        if Config.ENABLE_COMPRESSION:
            _compress_image(temp_path, save_path)
            # 如果 temp_path 和 save_path 不一样（后缀不同），删除临时文件
            if temp_path != save_path:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
        else:
            # 如果不压缩，且原始就是PNG（通常是），则不做额外处理
            pass

        end_time = time.time()
        duration = end_time - start_time
        file_size = os.path.getsize(save_path) / 1024 # KB

        logger.info(f"✅ 封面图生成完成 | ⏱️ 耗时: {duration:.1f}s | 📦 大小: {file_size:.1f}KB | 📂 路径：{save_path}")
        return str(save_path)

    except Exception as e:
        logger.error(f"❌ 图片生成失败: {str(e)}")
        raise

def _generate_gemini_flash(prompt: str) -> bytes:
    """使用 Gemini 3.1 Flash Image Preview (via google-genai SDK) 生成图片"""
    if not genai:
        raise ImportError("请先安装 google-genai 库: pip install google-genai")
        
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    
    try:
        # 使用 SDK 生成内容
        # 注意: response_modalities 需要根据模型支持情况配置
        # gemini-3.1-flash-image-preview 通常默认支持生图
        response = client.models.generate_content(
            model=Config.IMAGE_MODEL,
            contents=[prompt],
            config={
                'response_modalities': ['IMAGE'],
            }
        )
        
        # 解析 SDK 响应
        if not response.candidates:
             raise Exception("无生成结果 (No candidates)")
             
        content = response.candidates[0].content
        if not content or not content.parts:
             raise Exception("生成结果为空 (No content parts)")
             
        for part in content.parts:
            # 检查是否有 inline_data (图片)
            if part.inline_data:
                data = part.inline_data.data
                # SDK 可能返回 bytes 或 base64 字符串
                if isinstance(data, bytes):
                    return data
                elif isinstance(data, str):
                    return base64.b64decode(data)
                
        # 如果没有找到图片，可能返回了文本拒绝原因
        text_content = "".join([p.text for p in content.parts if p.text])
        raise Exception(f"未能获取图片数据。可能原因: {text_content}")
            
    except Exception as e:
        # 捕获 SDK 抛出的异常并包装
        raise Exception(f"Gemini SDK Error: {str(e)}")

def _generate_imagen(prompt: str) -> bytes:
    """使用 Google Imagen (Imagen 3) 生成图片"""
    # 注意：Imagen 3 在 Google AI Studio API 中可能还未完全开放 REST，
    # 这里尝试使用标准的 predict 接口。如果失败，建议使用 google-generativeai 库。
    url = f"{Config.GEMINI_IMAGE_API_BASE}/models/{Config.IMAGE_MODEL}:predict?key={Config.GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "instances": [
            {"prompt": prompt}
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "4:3"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise Exception(f"Gemini API Error ({response.status_code}): {response.text}")
        
    result = response.json()
    
    # 解析响应
    predictions = result.get("predictions")
    if not predictions:
        raise Exception(f"Gemini API 返回结果为空: {result}")
        
    b64_data = predictions[0].get("bytesBase64Encoded")
    if not b64_data:
         raise Exception("未能从 Gemini API 获取图片数据")
         
    return base64.b64decode(b64_data)

def _generate_qwen(prompt: str) -> bytes:
    """使用阿里云 Qwen (Wan) 生成图片"""
    headers = {
        "Authorization": f"Bearer {Config.QWEN_API_KEY}",
        "Content-Type": "application/json",
        # "X-DashScope-Async": "enable" # Wan 2.1 API 不支持异步调用
    }
    
    # 区分模型 API
    if "wanx" in Config.IMAGE_MODEL:
         api_url = Config.QWEN_IMAGE_API_URL_V1
         headers["X-DashScope-Async"] = "enable" # Wanx v1 必须异步
         # 使用 Wanx v1 模型的 Payload 结构
         payload = {
            "model": Config.IMAGE_MODEL,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": "1280*720", # Wanx v1 支持 1280*720
                "n": 1,
            }
        }
    else:
        # Wan 2.1 / Wan 2.0 (同步调用)
        api_url = Config.QWEN_IMAGE_API_URL
        payload = {
            "model": Config.IMAGE_MODEL,
            "input": {
                "messages": [{
                    "role": "user",
                    "content": [{"text": prompt}]
                }]
            },
            "parameters": {
                "size": "1024*768", # Wan 2.1 支持 1024*768
                "n": 1,
            }
        }
    
    # 1. 发送请求
    response = requests.post(api_url, json=payload, headers=headers, timeout=120) # 同步生成可能较慢，增加超时
    if response.status_code != 200:
         raise Exception(f"Qwen API Error ({response.status_code}): {response.text}")
         
    result = response.json()
    
    # 2. 处理结果
    # Wanx v1 (异步) 返回 task_id
    if "wanx" in Config.IMAGE_MODEL:
        task_id = result.get("output", {}).get("task_id")
        if not task_id:
            raise Exception(f"无法获取任务ID: {result}")
            
        logger.info(f"⏳ Qwen 任务已提交 (ID: {task_id})，正在生成...")
        
        # 轮询任务状态
        task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        for _ in range(60): # 最多等待 120秒
            time.sleep(2)
            check_resp = requests.get(task_url, headers={"Authorization": f"Bearer {Config.QWEN_API_KEY}"})
            if check_resp.status_code != 200:
                continue
                
            check_data = check_resp.json()
            task_status = check_data.get("output", {}).get("task_status")
            
            if task_status == "SUCCEEDED":
                results = check_data.get("output", {}).get("results", [])
                if results:
                    image_url = results[0].get("url")
                    if image_url:
                        return requests.get(image_url).content
                raise Exception(f"任务成功但未找到图片URL: {check_data}")
                
            elif task_status == "FAILED":
                raise Exception(f"任务失败: {check_data.get('output', {}).get('message')}")
                
        raise Exception("Qwen 生图任务超时")
        
    else:
        # Wan 2.1 (同步) 直接返回 output.choices[0].message.content[0].image
        # 结构: output: { choices: [ { message: { content: [ { image: "...", type: "image" } ] } } ] }
        try:
            output = result.get("output", {})
            choices = output.get("choices", [])
            if not choices:
                 raise Exception(f"无返回结果: {result}")
            
            content = choices[0].get("message", {}).get("content", [])
            if not content:
                 raise Exception("返回内容为空")
                 
            # 注意: Wan 2.1 返回的字段名是 'image' 而不是 'img'
            image_url = content[0].get("image")
            if not image_url:
                 # 尝试兼容旧版或文档不一致的情况
                 image_url = content[0].get("img")
                 
            if not image_url:
                 raise Exception("未能获取图片URL")
            
            # 清理可能的 Markdown 格式 URL (如 `url`)
            image_url = image_url.strip().strip('`')
                 
            return requests.get(image_url).content
            
        except Exception as e:
            raise Exception(f"解析 Wan 2.1 响应失败: {str(e)} | 原始响应: {result}")

def _compress_image(input_path: Path, output_path: Path):
    """压缩图片为JPG"""
    try:
        img = Image.open(input_path)
        
        # 转换颜色模式
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(output_path, 'JPEG', quality=Config.JPG_QUALITY, optimize=True)
        
    except Exception as e:
        logger.warning(f"图片压缩失败，保留原图: {e}")
        if input_path != output_path:
             import shutil
             shutil.copy(input_path, output_path)
