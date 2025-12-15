"""
本地大模型提取器
使用 Ollama 本地部署的大模型进行结构化数据提取
"""

import json
import requests
from typing import Dict, Any, List
from bs4 import BeautifulSoup


class LocalLLMExtractor:
    """本地大模型提取器（基于 Ollama）"""
    
    def __init__(self, model_name: str = 'qwen2.5:7b', base_url: str = 'http://localhost:11434'):
        """
        初始化本地大模型提取器
        
        Args:
            model_name: Ollama 模型名称，默认 qwen2.5:7b
            base_url: Ollama API 地址，默认本地
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f'{base_url}/api/generate'
    
    def extract_emperor_all_data(self, html_content_wiki: str, html_content_baidu: str, page_name: str) -> Dict[str, Any]:
        """
        一次性提取皇帝所有信息（基本信息 + 生平事迹，融合双源数据）
        
        Args:
            html_content_wiki: Wikipedia HTML 内容
            html_content_baidu: 百度百科 HTML 内容
            page_name: 页面名称（皇帝姓名）
        
        Returns:
            包含 emperor_info 和 events 的字典
        """
        # 清理 HTML，只保留主要内容
        cleaned_wiki = self._clean_html(html_content_wiki, 'wikipedia') if html_content_wiki else ''
        cleaned_baidu = self._clean_html(html_content_baidu, 'baidu') if html_content_baidu else ''
        
        # 构建一次性提取的融合提示词（无字符限制）
        prompt = self._build_emperor_all_data_prompt(cleaned_wiki, cleaned_baidu, page_name)
        
        # 调用本地大模型 API
        response_text = self._call_local_llm(prompt)
        
        # 解析返回结果
        result = self._parse_emperor_all_data_response(response_text)
        
        return result
    
    def extract_emperor_info(self, html_content_wiki: str, html_content_baidu: str, page_name: str) -> Dict[str, Any]:
        """
        从皇帝页面 HTML 中提取结构化信息（融合双源数据）
        
        Args:
            html_content_wiki: Wikipedia HTML 内容
            html_content_baidu: 百度百科 HTML 内容
            page_name: 页面名称（皇帝姓名）
        
        Returns:
            结构化的皇帝信息字典
        """
        # 清理 HTML
        cleaned_wiki = self._clean_html(html_content_wiki, 'wikipedia') if html_content_wiki else ''
        cleaned_baidu = self._clean_html(html_content_baidu, 'baidu') if html_content_baidu else ''
        
        # 构建融合提示词（无字符限制）
        prompt = self._build_emperor_prompt_dual_source(cleaned_wiki, cleaned_baidu, page_name)
        
        # 调用本地大模型 API
        response_text = self._call_local_llm(prompt)
        
        # 解析返回结果
        emperor_info = self._parse_emperor_response(response_text)
        
        return emperor_info
    
    def extract_emperor_events(self, html_content_wiki: str, html_content_baidu: str, page_name: str) -> List[Dict[str, Any]]:
        """
        从皇帝页面 HTML 中提取生平事迹（融合双源数据）
        
        Args:
            html_content_wiki: Wikipedia HTML 内容
            html_content_baidu: 百度百科 HTML 内容
            page_name: 页面名称（皇帝姓名）
        
        Returns:
            生平事迹列表
        """
        # 清理 HTML
        cleaned_wiki = self._clean_html(html_content_wiki, 'wikipedia') if html_content_wiki else ''
        cleaned_baidu = self._clean_html(html_content_baidu, 'baidu') if html_content_baidu else ''
        
        # 构建融合提示词（无字符限制）
        prompt = self._build_events_prompt_dual_source(cleaned_wiki, cleaned_baidu, page_name)
        
        # 调用本地大模型 API
        response_text = self._call_local_llm(prompt)
        
        # 解析返回结果
        events = self._parse_events_response(response_text)
        
        return events
    
    def _clean_html(self, html_content: str, data_source: str) -> str:
        """
        清理 HTML，移除脚本、样式等无关内容
        
        Args:
            html_content: 原始 HTML
            data_source: 数据源
        
        Returns:
            清理后的 HTML 文本
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 移除无关标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # 根据数据源提取主要内容
        if data_source == 'wikipedia':
            # Wikipedia：提取 mw-parser-output
            main_content = soup.find('div', class_='mw-parser-output')
            if main_content:
                return main_content.get_text(separator='\n', strip=True)
        
        elif data_source == 'baidu':
            # 百度百科：提取主体内容
            main_content = soup.find('div', class_='lemma-summary')
            if not main_content:
                main_content = soup.find('div', class_='main-content')
            if main_content:
                return main_content.get_text(separator='\n', strip=True)
        
        # 默认返回全文本
        return soup.get_text(separator='\n', strip=True)
    
    def _build_emperor_all_data_prompt(self, cleaned_wiki: str, cleaned_baidu: str, page_name: str) -> str:
        """构建一次性提取皇帝所有信息的提示词（基本信息 + 生平事迹，双源融合）"""
        # 本地大模型无字符限制，可传完整内容
        prompt = f"""你是一个历史数据提取专家。请从以下维基百科和百度百科的网页内容中提取关于皇帝"{page_name}"的完整结构化信息，包括基本信息和生平事迹时间线，将两份资料互为补充，形成更完整准确的数据。

=== 维基百科内容 ===
{cleaned_wiki}

=== 百度百科内容 ===
{cleaned_baidu}

请按照以下 JSON 格式输出，只返回 JSON，不要有其他内容：

{{
  "emperor_info": {{
    "皇帝": "朱元璋",
    "庙号": "明太祖",
    "年号": "洪武",
    "画像url": "https://...",
    "出生": "1328年10月21日（元天历元年九月十八日）",
    "去世": "1398年6月24日（洪武三十一年闰五月初十）",
    "简介": "明朝开国皇帝..."
  }},
  "events": [
    {{
      "时间": "1328年10月29日（元天历元年九月十八日）",
      "事件": "出生于贫农家庭，原名朱重八，后改名朱兴宗。出身寒微为其日后重农、严惩贪腐埋下思想基础。",
      "事件影响": "塑造了朱元璋的平民意识和反腐决心",
      "人物": [
        {{"姓名": "朱五四", "关系": "父", "链接": "https://..."}},
        {{"姓名": "陈氏", "关系": "母", "链接": "https://..."}}
      ],
      "地点": "濠州钟离县东乡（今安徽省凤阳县小溪河镇燃灯寺村）"
    }},
    {{
      "时间": "1344年（至正四年）",
      "事件": "淮北大旱，父母兄长相继去世；入皇觉寺为僧，不久被遣散，开始三年游方僧生涯，亲历民间疾苦，深刻影响其治国理念。",
      "事件影响": "亲历底层苦难，形成重农抑商政策基础",
      "人物": [],
      "地点": "皇觉寺（濠州，今安徽凤阳）"
    }}
  ]
}}

注意：
**基本信息部分**：
1. **数据融合**：优先从两个来源中选择更准确、更详细的信息，互为补充
2. **日期格式**："YYYY年MM月DD日（古代年号纪年）"，如"1328年10月21日（元天历元年九月十八日）"
3. **画像url**：优先使用维基百科的高清图片链接
4. **简介**：综合两个来源，控制在250字以内，突出关键成就
5. **缺失字段**：如果某个字段在两个来源都找不到，填写 null

**生平事迹部分**：
1. **数据融合**：综合维基百科和百度百科的信息，互为补充，形成更完整的时间线
2. **时间格式**：精确到年月日，并标注古代年号，如"1328年10月29日（元天历元年九月十八日）"
3. **事件描述**：详细记录事件经过和背景，200字以内
4. **事件影响**：简述该事件对后续历史的影响，可选字段
5. **人物结构**：每个人物包含"姓名"、"关系"（如父、母、好友、大臣等）、"链接"（优先从维基百科提取，其次百度百科）
6. **地点格式**："古代地名（今地名）"，如"应天府（今南京市）"
7. **提取重点**：政治、军事、文化、外交等重大事件，按时间顺序排列
8. **数量控制**：15-20个关键事件
9. **链接提取**：从原网页中提取实际链接，如果没有则填写 null
"""
        return prompt
    
    def _build_emperor_prompt_dual_source(self, cleaned_wiki: str, cleaned_baidu: str, page_name: str) -> str:
        """构建皇帝信息提取的提示词（双源融合）"""
        prompt = f"""你是一个历史数据提取专家。请从以下维基百科和百度百科的网页内容中提取关于皇帝"{page_name}"的结构化信息，并将两份资料互为补充，形成更完整准确的数据。

=== 维基百科内容 ===
{cleaned_wiki}

=== 百度百科内容 ===
{cleaned_baidu}

请按照以下 JSON 格式输出，只返回 JSON，不要有其他内容：

{{
  "皇帝": "朱元璋",
  "庙号": "明太祖",
  "年号": "洪武",
  "画像url": "https://...",
  "出生": "1328年10月21日（元天历元年九月十八日）",
  "去世": "1398年6月24日（洪武三十一年闰五月初十）",
  "简介": "明朝开国皇帝..."
}}

注意：
1. **数据融合**：优先从两个来源中选择更准确、更详细的信息，互为补充
2. **日期格式**："YYYY年MM月DD日（古代年号纪年）"，如"1328年10月21日（元天历元年九月十八日）"
3. **画像url**：优先使用维基百科的高清图片链接
4. **简介**：综合两个来源，控制在250字以内，突出关键成就
5. **缺失字段**：如果某个字段在两个来源都找不到，填写 null
"""
        return prompt
    
    def _build_events_prompt_dual_source(self, cleaned_wiki: str, cleaned_baidu: str, page_name: str) -> str:
        """构建生平事迹提取的提示词（双源融合）"""
        prompt = f"""你是一个历史数据提取专家。请从以下维基百科和百度百科的网页内容中提取关于皇帝"{page_name}"的生平事迹时间线，并将两份资料互为补充，形成更完整的历史时间轴。

=== 维基百科内容 ===
{cleaned_wiki}

=== 百度百科内容 ===
{cleaned_baidu}

请按照以下 JSON 格式输出事迹列表，只返回 JSON，不要有其他内容：

[
  {{
    "时间": "1328年10月29日（元天历元年九月十八日）",
    "事件": "出生于贫农家庭，原名朱重八，后改名朱兴宗。出身寒微为其日后重农、严惩贪腐埋下思想基础。",
    "事件影响": "塑造了朱元璋的平民意识和反腐决心",
    "人物": [
      {{"姓名": "朱五四", "关系": "父", "链接": "https://..."}},
      {{"姓名": "陈氏", "关系": "母", "链接": "https://..."}},
      {{"姓名": "句容朱氏", "关系": "祖父", "链接": null}}
    ],
    "地点": "濠州钟离县东乡（今安徽省凤阳县小溪河镇燃灯寺村）"
  }},
  {{
    "时间": "1344年（至正四年）",
    "事件": "淮北大旱，父母兄长相继去世；入皇觉寺为僧，不久被遣散，开始三年游方僧生涯，亲历民间疾苦，深刻影响其治国理念。",
    "事件影响": "亲历底层苦难，形成重农抑商政策基础",
    "人物": [],
    "地点": "皇觉寺（濠州，今安徽凤阳）"
  }}
]

注意：
1. **数据融合**：综合维基百科和百度百科的信息，互为补充，形成更完整的时间线
2. **时间格式**：精确到年月日，并标注古代年号，如"1328年10月29日（元天历元年九月十八日）"
3. **事件描述**：详细记录事件经过和背景，200字以内
4. **事件影响**：简述该事件对后续历史的影响，可选字段
5. **人物结构**：每个人物包含"姓名"、"关系"（如父、母、好友、大臣等）、"链接"（优先从维基百科提取，其次百度百科）
6. **地点格式**："古代地名（今地名）"，如"应天府（今南京市）"
7. **提取重点**：政治、军事、文化、外交等重大事件，按时间顺序排列
8. **数量控制**：15-20个关键事件
9. **链接提取**：从原网页中提取实际链接，如果没有则填写 null
"""
        return prompt
    
    def _call_local_llm(self, prompt: str, max_retries: int = 3) -> str:
        """
        调用本地大模型 API (Ollama)
        
        Args:
            prompt: 提示词
            max_retries: 最大重试次数
        
        Returns:
            API 返回的文本
        """
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model_name,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.1,  # 降低随机性，提升结构化输出稳定性
                'top_p': 0.9,
                'top_k': 40
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=data,
                    timeout=300  # 本地推理可能较慢，增加超时时间
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # 提取返回文本
                    content = result.get('response', '')
                    return content
                else:
                    raise Exception(f"API请求失败: {response.status_code}, {response.text}")
            
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"调用本地大模型失败（已重试{max_retries}次）: {str(e)}")
                continue
        
        return ""
    
    def _parse_emperor_all_data_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析一次性提取的完整数据（基本信息 + 生平事迹）
        
        Args:
            response_text: API 返回文本
        
        Returns:
            包含 emperor_info 和 events 的字典
        """
        try:
            # 尝试提取 JSON 部分
            json_str = self._extract_json(response_text)
            result = json.loads(json_str)
            
            # 验证返回数据结构
            if not isinstance(result, dict):
                raise Exception("返回结果不是字典格式")
            
            if 'emperor_info' not in result or 'events' not in result:
                raise Exception("返回结果缺少 emperor_info 或 events 字段")
            
            return result
        except Exception as e:
            raise Exception(f"解析皇帝完整数据失败: {str(e)}, 返回文本: {response_text[:200]}")
    
    def _parse_emperor_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析皇帝信息返回结果
        
        Args:
            response_text: API 返回文本
        
        Returns:
            解析后的字典
        """
        try:
            # 尝试提取 JSON 部分
            json_str = self._extract_json(response_text)
            emperor_info = json.loads(json_str)
            return emperor_info
        except Exception as e:
            raise Exception(f"解析皇帝信息失败: {str(e)}, 返回文本: {response_text[:200]}")
    
    def _parse_events_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        解析生平事迹返回结果
        
        Args:
            response_text: API 返回文本
        
        Returns:
            事迹列表
        """
        try:
            # 尝试提取 JSON 部分
            json_str = self._extract_json(response_text)
            events = json.loads(json_str)
            return events if isinstance(events, list) else []
        except Exception as e:
            raise Exception(f"解析生平事迹失败: {str(e)}, 返回文本: {response_text[:200]}")
    
    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON 部分"""
        # 移除可能的 markdown 代码块标记
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        # 查找第一个 { 或 [
        start_idx = -1
        for i, char in enumerate(text):
            if char in ['{', '[']:
                start_idx = i
                break
        
        if start_idx == -1:
            raise Exception("未找到 JSON 起始标记")
        
        return text[start_idx:].strip()
