"""
千问大模型集成
通过通义千问 API 处理 HTML 并提取结构化数据
"""

import json
import os
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from openai import OpenAI
from datetime import datetime


class QwenExtractor:
    """千问大模型提取器"""
    
    def __init__(self, api_key: str, model: str = 'qwen-max'):
        """
        初始化千问提取器
        
        Args:
            api_key: 通义千问 API Key
            model: 模型名称，默认 qwen-max
        """
        self.api_key = api_key
        self.model = model
        # 使用 OpenAI SDK 客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
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


        print("Using QwenExtractor to extract emperor all data... 1")
        # 清理 HTML，只保留主要内容
        cleaned_wiki = self._clean_html(html_content_wiki, 'wikipedia') if html_content_wiki else ''
        cleaned_baidu = self._clean_html(html_content_baidu, 'baidu') if html_content_baidu else ''
        
        print("Using QwenExtractor to extract emperor all data... 2")
        # 构建一次性提取的融合提示词
        prompt = self._build_emperor_all_data_prompt(cleaned_wiki, cleaned_baidu, page_name)
        
        print("Using QwenExtractor to extract emperor all data... 3")
        # 调用千问 API
        response_text = self._call_qwen_api(prompt)

        print("Using QwenExtractor to extract emperor all data... 4")
        
        # 解析返回结果
        result = self._parse_emperor_all_data_response(response_text)

        print("Using QwenExtractor to extract emperor all data... 5")
        
        return result
    
    def extract_emperor_info(self, html_content_wiki: str, html_content_baidu: str, page_name: str) -> Dict[str, Any]:
        """
        从皇帝页面 HTML 中提取结构化信息（融合双源数据）
        【保留此方法以兼容旧代码，但推荐使用 extract_emperor_all_data】
        
        Args:
            html_content_wiki: Wikipedia HTML 内容
            html_content_baidu: 百度百科 HTML 内容
            page_name: 页面名称（皇帝姓名）
        
        Returns:
            结构化的皇帝信息字典
        """
        # 清理 HTML，只保留主要内容
        cleaned_wiki = self._clean_html(html_content_wiki, 'wikipedia') if html_content_wiki else ''
        cleaned_baidu = self._clean_html(html_content_baidu, 'baidu') if html_content_baidu else ''
        
        # 构建融合提示词
        prompt = self._build_emperor_prompt_dual_source(cleaned_wiki, cleaned_baidu, page_name)
        
        # 调用千问 API
        response_text = self._call_qwen_api(prompt)
        
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
        
        # 构建融合提示词
        prompt = self._build_events_prompt_dual_source(cleaned_wiki, cleaned_baidu, page_name)
        
        # 调用千问 API
        response_text = self._call_qwen_api(prompt)
        
        # 解析返回结果
        events = self._parse_events_response(response_text)
        
        return events
    
    def extract_person_info(self, html_content: str, page_name: str, data_source: str) -> Dict[str, Any]:
        """从人物页面提取信息（待实现）"""
        pass
    
    def extract_event_info(self, html_content: str, page_name: str, data_source: str) -> Dict[str, Any]:
        """从事件页面提取信息（待实现）"""
        pass
    
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
        # 优化后的字符限制：增加到 10000 字符，充分利用千问的上下文窗口
        wiki_content = cleaned_wiki[:10000]
        baidu_content = cleaned_baidu[:10000]
        
        prompt = f"""你是一个历史数据提取专家。请从以下维基百科和百度百科的网页内容中提取关于皇帝"{page_name}"的完整结构化信息，包括基本信息和生平事迹时间线，将两份资料互为补充，形成更完整准确的数据。

=== 维基百科内容 ===
{wiki_content}

=== 百度百科内容 ===
{baidu_content}

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
      "地点": "濠州钟离县东乡（今安徽省凤阳县小溪河镇燃灯寺村）",
      "事件链接": null
    }},
    {{
      "时间": "1344年（至正四年）",
      "事件": "淮北大旱，父母兄长相继去世；入皇觉寺为僧，不久被遣散，开始三年游方僧生涯，亲历民间疾苦，深刻影响其治国理念。",
      "事件影响": "亲历底层苦难，形成重农抑商政策基础",
      "人物": [],
      "地点": "皇觉寺（濠州，今安徽凤阳）",
      "事件链接": null
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
7. **事件链接**：如果事件在原文中有对应的链接（如"靖难之役"、"土木堡之变"等），提取该链接；没有则填写 null
8. **提取重点**：政治、军事、文化、外交等重大事件，按时间顺序排列
9. **数量控制**：15-20个关键事件
"""
        return prompt
    
    def _build_emperor_prompt_dual_source(self, cleaned_wiki: str, cleaned_baidu: str, page_name: str) -> str:
        """构建皇帝信息提取的提示词（双源融合）"""
        # 优化后的字符限制：从 3500 增加到 8000
        wiki_content = cleaned_wiki[:8000]
        baidu_content = cleaned_baidu[:8000]
        
        prompt = f"""你是一个历史数据提取专家。请从以下维基百科和百度百科的网页内容中提取关于皇帝"{page_name}"的结构化信息，并将两份资料互为补充，形成更完整准确的数据。

=== 维基百科内容 ===
{wiki_content}

=== 百度百科内容 ===
{baidu_content}

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
        # 优化后的字符限制：从 5000 增加到 10000
        wiki_content = cleaned_wiki[:10000]
        baidu_content = cleaned_baidu[:10000]
        
        prompt = f"""你是一个历史数据提取专家。请从以下维基百科和百度百科的网页内容中提取关于皇帝"{page_name}"的生平事迹时间线，并将两份资料互为补充，形成更完整的历史时间轴。

=== 维基百科内容 ===
{wiki_content}

=== 百度百科内容 ===
{baidu_content}

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
    "地点": "濠州钟离县东乡（今安徽省凤阳县小溪河镇燃灯寺村）",
    "事件链接": null
  }},
  {{
    "时间": "1344年（至正四年）",
    "事件": "淮北大旱，父母兄长相继去世；入皇觉寺为僧，不久被遣散，开始三年游方僧生涯，亲历民间疾苦，深刻影响其治国理念。",
    "事件影响": "亲历底层苦难，形成重农抑商政策基础",
    "人物": [],
    "地点": "皇觉寺（濠州，今安徽凤阳）",
    "事件链接": null
  }},
  {{
    "时间": "1352年",
    "事件": "受儿时好友汤和邀请投奔郭子兴红巾军，赐名朱元璋，字国瑞；娶郭子兴养女马氏，奠定政治姻缘基础。",
    "事件影响": "开启军事生涯，获得政治联姻支持",
    "人物": [
      {{"姓名": "汤和", "关系": "好友", "链接": "https://zh.wikipedia.org/wiki/汤和"}},
      {{"姓名": "郭子兴", "关系": "义父", "链接": "https://baike.baidu.com/item/郭子兴"}},
      {{"姓名": "马氏", "关系": "妻", "链接": "https://zh.wikipedia.org/wiki/马皇后_(明太祖)"}}
    ],
    "地点": "濠州（今安徽凤阳）",
    "事件链接": null
  }},
  {{
    "时间": "1353年",
    "事件": "回乡募兵，徐达等加入；攻叠淮州，得地李善长，建立首个根据地。",
    "事件影响": "初步建立军事力量和谋士团队",
    "人物": [
      {{"姓名": "徐达", "关系": "部将", "链接": "https://zh.wikipedia.org/wiki/徐达"}},
      {{"姓名": "李善长", "关系": "谋士", "链接": "https://zh.wikipedia.org/wiki/李善长"}}
    ],
    "地点": "淮州（今安徽淮安）",
    "事件链接": null
  }}
]

注意：
1. **数据融合**：综合维基百科和百度百科的信息，互为补充，形成更完整的时间线
2. **时间格式**：精确到年月日，并标注古代年号，如"1328年10月29日（元天历元年九月十八日）"
3. **事件描述**：详细记录事件经过和背景，200字以内
4. **事件影响**：简述该事件对后续历史的影响，可选字段
5. **人物结构**：每个人物包含"姓名"、"关系"（如父、母、好友、大臣等）、"链接"（优先从维基百科提取，其次百度百科）
6. **地点格式**："古代地名（今地名）"，如"应天府（今南京市）"
7. **事件链接**：如果事件在原文中有对应的链接（如"靖难之役"、"胡惟庸案"、"土木堡之变"等），提取该链接；没有则填写 null
8. **提取重点**：政治、军事、文化、外交等重大事件，按时间顺序排列
9. **数量控制**：15-20个关键事件
"""
        return prompt
    
    def _build_events_prompt(self, cleaned_html: str, page_name: str, data_source: str) -> str:
        """构建生平事迹提取的提示词"""
        prompt = f"""你是一个历史数据提取专家。请从以下{data_source}网页内容中提取关于皇帝"{page_name}"的生平事迹时间线。

网页内容：
{cleaned_html[:6000]}

请按照以下 JSON 格式输出事迹列表，只返回 JSON，不要有其他内容：

[
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
  }},
  {{
    "时间": "1352年",
    "事件": "受儿时好友汤和邀请投奔郭子兴红巾军，赐名朱元璋，字国瑞；娶郭子兴养女马氏，奠定政治姻缘基础。",
    "事件影响": "开启军事生涯，获得政治联姻支持",
    "人物": [
      {{"姓名": "汤和", "关系": "好友", "链接": "https://..."}},
      {{"姓名": "郭子兴", "关系": "义父", "链接": "https://..."}},
      {{"姓名": "马氏", "关系": "妻", "链接": "https://..."}}
    ],
    "地点": "濠州（今安徽凤阳）"
  }}
]

注意：
1. **时间格式**：精确到年月日，并标注古代年号，如"1328年10月29日（元天历元年九月十八日）"
2. **事件描述**：详细记录事件经过和背景，200字以内
3. **事件影响**：简述该事件对后续历史的影响，可选字段
4. **人物结构**：每个人物包含"姓名"、"关系"（如父、母、好友、大臣等）、"链接"（从原网页提取）
5. **地点格式**："古代地名（今地名）"，如"应天府（今南京市）"
6. **事件链接**：如果事件在原文中有对应的链接（如"靖难之役"、"胡惟庸案"、"土木堡之变"等），提取该链接；没有则填写 null
7. **提取重点**：政治、军事、文化、外交等重大事件，按时间顺序排列
8. **数量控制**：15-20个关键事件
"""
        return prompt
    
    def _call_qwen_api(self, prompt: str, max_retries: int = 3) -> str:
        """
        调用千问 API（使用 OpenAI SDK）
        
        Args:
            prompt: 提示词
            max_retries: 最大重试次数
        
        Returns:
            API 返回的文本
        """
        print("Calling Qwen API...")
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} to call Qwen API...")
                
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {'role': 'user', 'content': prompt}
                    ]
                )
                
                # 提取返回内容
                content = completion.choices[0].message.content
                print(f"✅ Qwen API call successful")
                
                # 保存原始JSON响应到文件
                self._save_response_to_file(content)
                
                return content
            
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"调用千问API失败（已重试{max_retries}次）: {str(e)}")
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
