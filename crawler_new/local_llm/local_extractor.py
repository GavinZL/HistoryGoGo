"""
本地大模型提取器
使用 Ollama 本地部署的大模型进行结构化数据提取
"""

import json
import os
from datetime import datetime
import requests
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from .html_cleaner import HTMLCleanerFactory, CleanedContent


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
    
    def extract_emperor_all_data(self, html_content: str, page_name: str) -> Dict[str, Any]:
        """
        一次性提取皇帝所有信息（基本信息 + 生平事迹）
        
        Args:
            html_content: Wikipedia HTML 内容
            page_name: 页面名称（皇帝姓名）
        
        Returns:
            包含 emperor_info 和 events 的字典
        """
        # 清理 HTML，只保留主要内容
        cleaned_html = self._clean_html(html_content, 'wikipedia', page_name)
        
        print(f'Cleaning HTML content for {page_name}...')
        # 构建一次性提取的提示词
        prompt = self._build_emperor_all_data_prompt(cleaned_html, page_name)
        print(f'Building prompt for {page_name}...')

        # 调用本地大模型 API
        response_text = self._call_local_llm(prompt)
        print(f'Calling local LLM for {page_name}...')

        # 存储 JSON 响应
        self._save_response_to_file(response_text)
        print(f'Saving response to file for {page_name}...')
        # 解析返回结果
        result = self._parse_emperor_all_data_response(response_text)
        print(f'Parsing response for {page_name}...')
        
        return result
    
    def extract_emperor_info(self, html_content: str, page_name: str) -> Dict[str, Any]:
        """
        从皇帝页面 HTML 中提取结构化信息
        
        Args:
            html_content: Wikipedia HTML 内容
            page_name: 页面名称（皇帝姓名）
        
        Returns:
            结构化的皇帝信息字典
        """
        # 清理 HTML
        cleaned_html = self._clean_html(html_content, 'wikipedia', page_name)
        
        # 构建提示词
        prompt = self._build_emperor_prompt(cleaned_html, page_name)
        
        # 调用本地大模型 API
        response_text = self._call_local_llm(prompt)
        
        # 解析返回结果
        emperor_info = self._parse_emperor_response(response_text)
        
        return emperor_info
    
    def extract_emperor_events(self, html_content: str, page_name: str) -> List[Dict[str, Any]]:
        """
        从皇帝页面 HTML 中提取生平事迹
        
        Args:
            html_content: Wikipedia HTML 内容
            page_name: 页面名称（皇帝姓名）
        
        Returns:
            生平事迹列表
        """
        # 清理 HTML
        cleaned_html = self._clean_html(html_content, 'wikipedia', page_name)
        
        # 构建提示词
        prompt = self._build_events_prompt(cleaned_html, page_name)
        
        # 调用本地大模型 API
        response_text = self._call_local_llm(prompt)
        
        # 存储 JSON 响应
        self._save_response_to_file(response_text)

        # 解析返回结果
        events = self._parse_events_response(response_text)
        
        return events
    
    def _clean_html(self, html_content: str, data_source: str = 'wikipedia', page_name: str = None) -> str:
        """
        清理 HTML，移除脚本、样式等无关内容
        提取 infobox vcard 到 id="评价" 之间的主要内容
        同时提取目录结构和人物/事件链接
        
        Args:
            html_content: 原始 HTML
            data_source: 数据源（固定为 'wikipedia'）
            page_name: 页面名称（可选，用于保存文件命名）
        
        Returns:
            清理后的 HTML 文本
        """
        # 使用独立的HTML清理器
        cleaner = HTMLCleanerFactory.create_cleaner(data_source)
        cleaned_content = cleaner.clean(html_content)
        
        # 保存清理后的文本
        self._save_cleaned_text(cleaned_content.text, page_name)
        
        # 保存目录结构
        self._save_toc(cleaned_content.toc, page_name)
        
        # 保存链接数据
        self._save_links(cleaned_content.links, page_name)
        
        return cleaned_content.text
    
    def _build_emperor_all_data_prompt(self, cleaned_html: str, page_name: str) -> str:
        """构建一次性提取皇帝所有信息的提示词(基本信息 + 生平事迹)"""
        # 对于本地小模型,适当限制输入长度以提升提取质量
        html_content = cleaned_html
        
        prompt = f"""你是一个历史数据提取专家。从以下 Wikipedia 内容中提取关于皇帝“{page_name}”的结构化信息。

重要要求:
1. 必须提取 20+ 条生平事迹，按时间顺序排列
2. 每个事件必须包含:时间、事件、事件影响、人物、地点
3. 从出生到去世，全面覆盖重要事件
4. 只返回 JSON 格式，不要有其他内容

=== Wikipedia 内容 ===
{html_content}

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
1. **日期格式**："YYYY年MM月DD日（古代年号纪年）"，如"1328年10月21日（元天历元年九月十八日）"
2. **画像url**：使用 Wikipedia 的高清图片链接
3. **简介**：控制在250字以内，突出关键成就
4. **缺失字段**：如果某个字段找不到，填写 null

**生平事迹部分（最重要）**：
1. **数量要求**：必须提取足够多的事件，覆盖从出生到去世的完整生涯
2. **时间格式**：精确到年月日，并标注古代年号，如"1328年10月29日（元天历元年九月十八日）"
3. **事件描述**：详细记录事件经过和背景，150-200字
4. **事件影响**：必填，简述该事件对后续历史的影响
5. **人物结构**：每个人物包含“姓名”、“关系”（如父、母、好友、大臣等）、“链接”
6. **地点格式**：“古代地名（今地名）”，如“应天府（今南京市）”
7. **提取重点**：政治、军事、文化、外交等重大事件，按时间顺序排列
8. **链接提取**：从原网页中提取实际链接，如果没有则填写 null

特别提醒：生平事迹必须详细且全面，包括：
- 出生和早年经历
- 重要军事行动和战役
- 登基和政治改革
- 文化和制度建设
- 重大历史事件参与
- 晚年政策和去世
确保提取 15-20 条事迹！
"""
        return prompt
    
    def _build_emperor_prompt(self, cleaned_html: str, page_name: str) -> str:
        """构建皇帝信息提取的提示词"""
        prompt = f"""你是一个历史数据提取专家。请从以下 Wikipedia 的网页内容中提取关于皇帝“{page_name}”的结构化信息。

=== Wikipedia 内容 ===
{cleaned_html}

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
1. **日期格式**："YYYY年MM月DD日（古代年号纪年）"，如"1328年10月21日（元天历元年九月十八日）"
2. **画像url**：使用 Wikipedia 的高清图片链接
3. **简介**：控制在250字以内，突出关键成就
4. **缺失字段**：如果某个字段找不到，填写 null
"""
        return prompt
    
    def _build_events_prompt(self, cleaned_html: str, page_name: str) -> str:
        """构建生平事迹提取的提示词"""
        prompt = f"""你是一个历史数据提取专家。请从以下 Wikipedia 的网页内容中提取关于皇帝“{page_name}”的生平事迹时间线。

=== Wikipedia 内容 ===
{cleaned_html}

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
1. **时间格式**：精确到年月日，并标注古代年号，如"1328年10月29日（元天历元年九月十八日）"
2. **事件描述**：详细记录事件经过和背景，200字以内
3. **事件影响**：简述该事件对后续历史的影响，可选字段
4. **人物结构**：每个人物包含“姓名”、“关系”（如父、母、好友、大臣等）、“链接”（从 Wikipedia 提取）
5. **地点格式**：“古代地名（今地名）”，如“应天府（今南京市）”
6. **提取重点**：政治、军事、文化、外交等重大事件，按时间顺序排列
7. **数量控制**：15-20个关键事件
8. **链接提取**：从原网页中提取实际链接，如果没有则填写 null
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
                'temperature': 0.2,  # 降低随机性，提升结构化输出稳定性
                'top_p': 0.8,
                'top_k': 40,
                'num_predict': 4096,  # 增加最大输出长度，确保能输出 15-20 条事迹
                'repeat_penalty': 1.1  # 防止重复内容
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


    def _save_cleaned_text(self, content: str, page_name: str = None) -> None:
        """
        保存清理后的HTML文本到data/html/cleaned_text文件夹
        
        Args:
            content: 清理后的文本内容
            page_name: 页面名称（可选）
        """
        try:
            # 确定保存目录
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data', 'html', 'cleaned_text'
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名（时间戳 + 页面名称）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if page_name:
                filename = f'cleaned_{page_name}_{timestamp}.txt'
            else:
                filename = f'cleaned_text_{timestamp}.txt'
            filepath = os.path.join(output_dir, filename)
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 已保存清理后的文本: {filepath}")
            print(f"   文本大小: {len(content)} 字符")
        except Exception as e:
            print(f"⚠️  保存清理文本失败: {str(e)}")
    
    def _save_response_to_file(self, content: str) -> None:
        """
        保存API响应到data/html文件夹
        
        Args:
            content: API返回的JSON内容
        """
        try:
            # 确定保存目录
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data', 'html', 'qwen_responses'
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名（时间戳）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:17]
            filename = f'qwen_response_{timestamp}.json'
            filepath = os.path.join(output_dir, filename)
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 已保存API响应: {filepath}")
        except Exception as e:
            print(f"⚠️  保存API响应失败: {str(e)}")
    
    def _save_toc(self, toc: List[Dict[str, str]], page_name: str = None) -> None:
        """
        保存目录结构到data/html/toc文件夹
        
        Args:
            toc: 目录列表
            page_name: 页面名称（可选）
        """
        try:
            # 确定保存目录
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data', 'html', 'toc'
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if page_name:
                filename = f'toc_{page_name}_{timestamp}.json'
            else:
                filename = f'toc_{timestamp}.json'
            filepath = os.path.join(output_dir, filename)
            
            # 保存为JSON格式
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(toc, f, ensure_ascii=False, indent=2)
            
            print(f"📑 已保存目录结构: {filepath}")
            print(f"   目录条目数: {len(toc)}")
        except Exception as e:
            print(f"⚠️  保存目录结构失败: {str(e)}")
    
    def _save_links(self, links: List[Dict[str, str]], page_name: str = None) -> None:
        """
        保存链接数据到data/html/links文件夹
        
        Args:
            links: 链接列表
            page_name: 页面名称（可选）
        """
        try:
            # 确定保存目录
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data', 'html', 'links'
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if page_name:
                filename = f'links_{page_name}_{timestamp}.json'
            else:
                filename = f'links_{timestamp}.json'
            filepath = os.path.join(output_dir, filename)
            
            # 统计链接类型
            link_stats = {}
            for link in links:
                link_type = link.get('type', 'unknown')
                link_stats[link_type] = link_stats.get(link_type, 0) + 1
            
            # 保存为JSON格式
            data = {
                'total': len(links),
                'statistics': link_stats,
                'links': links
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"🔗 已保存链接数据: {filepath}")
            print(f"   链接总数: {len(links)}")
            print(f"   链接分类: {link_stats}")
        except Exception as e:
            print(f"⚠️  保存链接数据失败: {str(e)}")