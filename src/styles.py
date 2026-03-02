"""
风格预设定义
"""

# 风格预设（通过STYLE_NAME选择；也支持运行时参数覆盖）
# 说明：
# - style: 风格关键词（给大模型看的）
# - color_matching: 配色建议
# - visual_rule: 视觉约束（尽量减少杂乱、抽象线条、信息过载）

STYLE_PRESETS = {
    # 扁平 / 极简
    "flat": {
        "style": "扁平插画风",
        "color_matching": "低饱和度配色，莫兰迪色系或中性色",
        "visual_rule": "扁平化色块，形状简化，轮廓清晰，层次不要太多，避免复杂构图，避免过多抽象线条",
    },
    "minimal": {
        "style": "极简风",
        "color_matching": "中性色为主，低饱和度点缀色",
        "visual_rule": "极简设计，单一核心元素，构图克制，细节适量，画面干净，避免复杂构图，避免过多抽象线条",
    },
    "semi_flat": {
        "style": "半扁平 / 轻拟物",
        "color_matching": "柔和配色，轻微明暗对比",
        "visual_rule": "以扁平为主，少量材质与阴影增强质感，避免堆叠太多元素，避免复杂构图，避免过多抽象线条",
    },

    # 拟物 / 轻奢
    "skeuomorphic": {
        "style": "拟物化风格",
        "color_matching": "真实材质色系，低饱和不过曝",
        "visual_rule": "真实材质质感（纸张/金属/塑料等），明确光源与阴影，细节适度但不杂乱，避免复杂构图，避免过多抽象线条",
    },
    "luxury_minimal": {
        "style": "极简轻奢",
        "color_matching": "高级灰 + 少量金属点缀色（香槟金/玫瑰金）",
        "visual_rule": "高级质感，精致材质与柔光，点缀元素克制，避免元素过多，避免复杂构图，避免过多抽象线条",
    },

    # 玻璃拟态 / 霓虹酸性
    "glassmorphism": {
        "style": "玻璃拟态",
        "color_matching": "清透浅色渐变 + 低饱和点缀",
        "visual_rule": "磨砂玻璃半透明卡片质感，柔和高光与阴影，层叠不超过2层，避免复杂构图，避免过多抽象线条",
    },
    "neon_acid": {
        "style": "霓虹酸性",
        "color_matching": "酸性荧光点缀 + 深浅对比（控制元素数量）",
        "visual_rule": "高对比但不刺眼，霓虹点缀克制，元素数量严格控制，避免复杂构图，避免过多抽象线条",
    },

    # 手绘 / 等距
    "hand_drawn": {
        "style": "手绘插画",
        "color_matching": "手绘自然配色，纸感中性色",
        "visual_rule": "手绘线条与笔触，纹理适度，主体清晰，避免线条过密导致杂乱，避免复杂构图",
    },
    "isometric": {
        "style": "等距3D风格",
        "color_matching": "明亮清晰配色，区分面与体",
        "visual_rule": "2.5D等距视角，几何感强，结构清晰，避免过于复杂的场景堆砌",
    },
    
    # 科技 / 抽象
    "tech_abstract": {
        "style": "科技抽象",
        "color_matching": "深色背景 + 科技蓝/青/紫渐变",
        "visual_rule": "抽象几何图形，数据流线条，光效点缀，避免过于具象的物体，保持现代感与未来感",
    },
    "cyberpunk": {
        "style": "赛博朋克",
        "color_matching": "高对比度霓虹色，蓝紫/粉红/青色",
        "visual_rule": "霓虹灯光，未来城市元素，机械质感，高光与阴影对比强烈，避免过于杂乱的细节",
    }
}

NO_TEXT_RULE = "无文字、无字母、无数字、无符号、无标签、无水印，纯视觉图形设计"

def get_style_config(style_name: str) -> dict:
    """获取指定风格的配置，如果不存在则返回默认风格（flat）"""
    return STYLE_PRESETS.get(style_name, STYLE_PRESETS["flat"])
