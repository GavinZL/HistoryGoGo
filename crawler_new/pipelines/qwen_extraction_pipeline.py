"""
千问大模型提取 Pipeline
使用通义千问处理 HTML 并提取结构化数据
"""

from datetime import datetime
from typing import Dict, Any, List

from crawler_new.models.items import HtmlPageItem, ExtractedDataItem
from crawler_new.utils.qwen_extractor import QwenExtractor
from crawler_new.local_llm.local_extractor import LocalLLMExtractor


class QwenExtractionPipeline:
    """千问大模型提取Pipeline"""
    
    def __init__(self, api_key: str, model: str, use_local_llm: bool = False, local_llm_model: str = '', local_llm_base_url: str = ''):
        self.api_key = api_key
        self.model = model
        self.use_local_llm = use_local_llm
        self.local_llm_model = local_llm_model
        self.local_llm_base_url = local_llm_base_url
        self.extractor = None
        self.html_cache = {}  # 缓存已爬取的HTML，用于双源融合
    
    @classmethod
    def from_crawler(cls, crawler):
        # 读取配置
        use_local_llm = crawler.settings.get('USE_LOCAL_LLM', False)
        api_key = crawler.settings.get('QWEN_API_KEY', '')
        model = crawler.settings.get('QWEN_MODEL', 'qwen-max')
        local_llm_model = crawler.settings.get('LOCAL_LLM_MODEL', 'qwen2.5:7b')
        local_llm_base_url = crawler.settings.get('LOCAL_LLM_BASE_URL', 'http://localhost:11434')
        return cls(api_key, model, use_local_llm, local_llm_model, local_llm_base_url)
    
    def open_spider(self, spider):
        """Spider 开启时初始化提取器"""
        spider.logger.info(f"\n{'='*100}")
        spider.logger.info(f"🤖 [Pipeline-2] QwenExtractionPipeline 启动")
        
        # 判断使用哪种大模型
        if self.use_local_llm:
            # 使用本地大模型
            try:
                self.extractor = LocalLLMExtractor(self.local_llm_model, self.local_llm_base_url)
                spider.logger.info(f"   ✅ 本地大模型已初始化")
                spider.logger.info(f"   模型: {self.local_llm_model}")
                spider.logger.info(f"   API地址: {self.local_llm_base_url}")
                spider.logger.info(f"   优势: 无字符限制，完整HTML处理")
            except Exception as e:
                spider.logger.error(f"   ❌ 本地大模型初始化失败: {str(e)}")
                spider.logger.warning(f"   提示：请确保 Ollama 服务已启动 (ollama serve)")
                self.extractor = None
        else:
            # 使用 API
            if not self.api_key:
                spider.logger.warning(f"   ⚠️  QWEN_API_KEY 未配置，将跳过大模型提取")
                spider.logger.warning(f"   提示：请在 config/settings.py 中配置 QWEN_API_KEY")
                self.extractor = None
            else:
                self.extractor = QwenExtractor(self.api_key, self.model)
                spider.logger.info(f"   ✅ 千问 API 已初始化")
                spider.logger.info(f"   模型: {self.model}")
                spider.logger.info(f"   API Key: {self.api_key[:10]}...")
                spider.logger.info(f"   注意: 存在字符限制")
        
        spider.logger.info(f"{'='*100}\n")
    
    def process_item(self, item, spider):
        """处理 Item"""
        # 只处理 HtmlPageItem
        if not isinstance(item, HtmlPageItem):
            return item
        
        # 如果 API Key 未配置，跳过提取
        if not self.extractor:
            spider.logger.warning(f"⚠️  [跳过] 千问提取: {item['page_id']}（API Key 未配置）")
            return item
        
        try:
            # 根据页面类型处理
            page_type = item['page_type']
            page_name = item['page_name']
            data_source = item['data_source']
            
            spider.logger.info(f"\n{'='*80}")
            spider.logger.info(f"🤖 [Pipeline-2] 千问提取开始")
            spider.logger.info(f"   page_id: {item['page_id']}")
            spider.logger.info(f"   page_name: {page_name}")
            spider.logger.info(f"   data_source: {data_source}")
            
            # 先缓存HTML，等待双源都爬取完毕后再处理
            cache_key = f"{page_type}_{page_name}"
            
            if cache_key not in self.html_cache:
                self.html_cache[cache_key] = {}
            
            # 存储当前数据源的HTML
            self.html_cache[cache_key][data_source] = item['html_content']
            
            spider.logger.info(f"   💾 缓存HTML: {page_name} ({data_source})")
            
            # 检查是否双源都已完成
            has_wikipedia = 'wikipedia' in self.html_cache[cache_key]
            has_baidu = 'baidu' in self.html_cache[cache_key]
            
            spider.logger.info(f"   📋 数据源状态: Wikipedia={'✅' if has_wikipedia else '❌'}, Baidu={'✅' if has_baidu else '❌'}")
            
            # 如果双源都存在，执行提取
            if has_wikipedia and has_baidu:
                spider.logger.info(f"   ✅ 双源已完成，开始融合提取")
                spider.logger.info(f"{'='*80}\n")
                
                html_wiki = self.html_cache[cache_key].get('wikipedia', '')
                html_baidu = self.html_cache[cache_key].get('baidu', '')
                
                if page_type == 'emperor':
                    extracted_item = self._extract_emperor_dual_source(item, html_wiki, html_baidu, spider)
                elif page_type == 'event':
                    extracted_item = self._extract_event(item, spider)
                elif page_type == 'person':
                    extracted_item = self._extract_person(item, spider)
                else:
                    spider.logger.warning(f"⚠️  未知页面类型: {page_type}")
                    return item
                
                spider.logger.info(f"\n{'='*80}")
                spider.logger.info(f"✅ [Pipeline-2] 千问提取完成: {page_name}")
                spider.logger.info(f"{'='*80}\n")
                
                # 清理缓存
                del self.html_cache[cache_key]
                
                return extracted_item
            else:
                # 只有一个数据源，等待另一个
                spider.logger.info(f"   ⏳ 等待另一个数据源完成...")
                spider.logger.info(f"   已有: {', '.join(self.html_cache[cache_key].keys())}")
                spider.logger.info(f"{'='*80}\n")
                return item
                
        except Exception as e:
            spider.logger.error(f"\n{'='*80}")
            spider.logger.error(f"❌ [Pipeline-2] 千问提取失败")
            spider.logger.error(f"   page_id: {item['page_id']}")
            spider.logger.error(f"   错误: {str(e)}")
            spider.logger.error(f"{'='*80}\n")
            import traceback
            spider.logger.debug(traceback.format_exc())
            return item
    
    def _extract_emperor_dual_source(self, html_item: HtmlPageItem, html_wiki: str, html_baidu: str, spider) -> ExtractedDataItem:
        """提取皇帝信息（双源融合）"""
        page_name = html_item['page_name']
        
        spider.logger.info(f"\n{'='*80}")
        spider.logger.info(f"🤖 [大模型提取] 开始提取皇帝信息")
        spider.logger.info(f"   皇帝: {page_name}")
        spider.logger.info(f"   Wikipedia HTML: {len(html_wiki)} 字符")
        spider.logger.info(f"   Baidu HTML: {len(html_baidu)} 字符")
        spider.logger.info(f"   提取模式: 一次性提取（基本信息 + 生平事迹）")
        spider.logger.info(f"   传输限制: Wiki 10000字符 + Baidu 10000字符")
        spider.logger.info(f"{'='*80}")
        
        # 使用新的一次性提取方法
        spider.logger.info(f"\n🚀 [大模型调用] 一次性提取所有数据...")
        
        try:
            # 1. 一次性提取所有数据
            result = self.extractor.extract_emperor_all_data(
                html_content_wiki=html_wiki,
                html_content_baidu=html_baidu,
                page_name=page_name
            )
            
            emperor_info = result.get('emperor_info', {})
            events = result.get('events', [])
            
            spider.logger.info(f"   ✅ 数据提取完成")
            spider.logger.info(f"\n📑 [基本信息]")
            spider.logger.info(f"   皇帝: {emperor_info.get('皇帝')}")
            spider.logger.info(f"   庙号: {emperor_info.get('庙号')}")
            spider.logger.info(f"   年号: {emperor_info.get('年号')}")
            spider.logger.info(f"   出生: {emperor_info.get('出生')}")
            spider.logger.info(f"   去世: {emperor_info.get('去世')}")
            
            spider.logger.info(f"\n📜 [生平事迹] 提取完成: {len(events)} 条")
            for idx, event in enumerate(events[:3], 1):
                spider.logger.info(f"      {idx}. {event.get('时间')} - {event.get('事件', '')[:30]}...")
            if len(events) > 3:
                spider.logger.info(f"      ... 还有 {len(events) - 3} 条事迹")
            
        except Exception as e:
            # 如果一次性提取失败，降级为分次提取
            spider.logger.warning(f"   ⚠️  一次性提取失败: {str(e)}")
            spider.logger.warning(f"   🔄 降级为分次提取模式...")
            
            # 1. 提取皇帝基本信息
            spider.logger.info(f"\n📑 [Step 1] 调用大模型提取皇帝基本信息...")
            emperor_info = self.extractor.extract_emperor_info(
                html_content_wiki=html_wiki,
                html_content_baidu=html_baidu,
                page_name=page_name
            )
            
            spider.logger.info(f"   ✅ 皇帝信息提取完成")
            spider.logger.info(f"   皇帝: {emperor_info.get('皇帝')}")
            spider.logger.info(f"   庙号: {emperor_info.get('庙号')}")
            spider.logger.info(f"   年号: {emperor_info.get('年号')}")
            spider.logger.info(f"   出生: {emperor_info.get('出生')}")
            spider.logger.info(f"   去世: {emperor_info.get('去世')}")
            
            # 2. 提取生平事迹（双源融合）
            spider.logger.info(f"\n📜 [Step 2] 调用大模型提取生平事迹...")
            events = self.extractor.extract_emperor_events(
                html_content_wiki=html_wiki,
                html_content_baidu=html_baidu,
                page_name=page_name
            )
            
            spider.logger.info(f"   ✅ 生平事迹提取完成: {len(events)} 条")
            for idx, event in enumerate(events[:3], 1):
                spider.logger.info(f"      {idx}. {event.get('时间')} - {event.get('事件', '')[:30]}...")
            if len(events) > 3:
                spider.logger.info(f"      ... 还有 {len(events) - 3} 条事迹")
        
        # 3. 提取链接（用于递归爬取）
        spider.logger.info(f"\n🔗 [Step 3] 提取链接信息...")
        extracted_links = self._extract_links_from_events(events)
        
        event_links = [l for l in extracted_links if l['type'] == 'event']
        person_links = [l for l in extracted_links if l['type'] == 'person']
        
        spider.logger.info(f"   ✅ 链接提取完成")
        spider.logger.info(f"   事件链接: {len(event_links)} 个")
        spider.logger.info(f"   人物链接: {len(person_links)} 个")
        
        # 4. 创建 ExtractedDataItem
        spider.logger.info(f"\n📦 [Step 4] 创建 ExtractedDataItem")
        extracted_item = ExtractedDataItem(
            data_type='emperor',
            html_item=html_item,
            extracted_data={
                'emperor_info': emperor_info,
                'events': events
            },
            extracted_links=extracted_links,
            extraction_time=datetime.now().isoformat()
        )
        
        spider.logger.info(f"   ✅ ExtractedDataItem 创建完成")
        spider.logger.info(f"{'='*80}\n")
        
        return extracted_item
    
    def _extract_event(self, html_item: HtmlPageItem, spider) -> ExtractedDataItem:
        """提取事件信息（待实现）"""
        spider.logger.info(f"🤖 提取事件信息: {html_item['page_name']}（功能待实现）")
        
        # TODO: 实现事件信息提取
        event_info = {}
        
        extracted_item = ExtractedDataItem(
            data_type='event',
            html_item=html_item,
            extracted_data={'event_info': event_info},
            extracted_links=[],
            extraction_time=datetime.now().isoformat()
        )
        
        return extracted_item
    
    def _extract_person(self, html_item: HtmlPageItem, spider) -> ExtractedDataItem:
        """提取人物信息（待实现）"""
        spider.logger.info(f"🤖 提取人物信息: {html_item['page_name']}（功能待实现）")
        
        # TODO: 实现人物信息提取
        person_info = {}
        
        extracted_item = ExtractedDataItem(
            data_type='person',
            html_item=html_item,
            extracted_data={'person_info': person_info},
            extracted_links=[],
            extraction_time=datetime.now().isoformat()
        )
        
        return extracted_item
    
    def _extract_links_from_events(self, events: List[Dict]) -> List[Dict]:
        """从事迹中提取人物和事件链接（适配新数据格式）"""
        links = []
        
        for event in events:
            # 提取事件链接（如果有）
            event_link = event.get('事件链接')
            if event_link and event_link != 'null' and event_link:
                links.append({
                    'type': 'event',
                    'name': event.get('事件', ''),
                    'url': event_link,
                    'source': self._detect_source_from_url(event_link)
                })
            
            # 提取人物链接（新格式：对象数组）
            persons = event.get('人物', [])
            
            if persons and isinstance(persons, list):
                for person_obj in persons:
                    if isinstance(person_obj, dict):
                        person_link = person_obj.get('链接')
                        person_name = person_obj.get('姓名', '')
                        
                        if person_link and person_link != 'null' and person_link:
                            links.append({
                                'type': 'person',
                                'name': person_name,
                                'url': person_link,
                                'source': self._detect_source_from_url(person_link)
                            })
        
        return links
    
    def _detect_source_from_url(self, url: str) -> str:
        """根据URL检测数据源"""
        if 'wikipedia' in url:
            return 'wikipedia'
        elif 'baidu' in url:
            return 'baidu'
        else:
            return 'wikipedia'  # 默认
