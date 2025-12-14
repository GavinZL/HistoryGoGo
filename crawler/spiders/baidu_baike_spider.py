"""
百度百科爬虫
用于爬取明朝皇帝、事件、人物信息
"""

import scrapy
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import re
from datetime import date

from crawler.models.entities import Emperor, Event, Person, EventType, PersonType
from crawler.utils.date_utils import DateParser, clean_text, generate_id
from crawler.config.ming_data import MING_EMPERORS, MING_DYNASTY


class BaiduBaikeSpider(scrapy.Spider):
    """百度百科爬虫"""
    
    name = 'baidu_baike'
    allowed_domains = ['baike.baidu.com']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 4,
    }
    
    def __init__(self, crawl_mode='test', test_emperor_count=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_parser = DateParser()
        self.emperor_data = {}  # 存储已爬取的皇帝数据
        
        # 获取爬取模式配置
        self.crawl_mode = crawl_mode
        self.test_emperor_count = int(test_emperor_count)
        
        # 爬取统计
        self.stats = {
            'emperors': 0,
            'events': 0,
            'persons': 0,
            'requests_made': 0,
            'requests_failed': 0,
            'parse_errors': 0
        }
        
        self.logger.info("=" * 80)
        self.logger.info(f"🚀 百度百科爬虫启动")
        self.logger.info(f"   爬取模式: {'测试模式' if crawl_mode == 'test' else '全量模式'}")
        if crawl_mode == 'test':
            self.logger.info(f"   爬取数量: 前 {test_emperor_count} 位皇帝")
        self.logger.info("=" * 80)
    
    def start_requests(self):
        """生成起始请求"""
        # 根据爬取模式决定爬取多少位皇帝
        emperors_to_crawl = MING_EMPERORS
        if self.crawl_mode == 'test':
            emperors_to_crawl = MING_EMPERORS[:self.test_emperor_count]
            self.logger.info(f"📋 测试模式：只爬取前{self.test_emperor_count}位皇帝")
        else:
            self.logger.info(f"📋 全量模式：爬取所有{len(MING_EMPERORS)}位皇帝")
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"开始生成皇帝爬取请求...")
        self.logger.info(f"{'='*80}\n")
        
        # 首先爬取皇帝信息
        for idx, emperor_info in enumerate(emperors_to_crawl, 1):
            url = self._build_baidu_url(emperor_info['name'])
            self.logger.info(f"📤 [{idx}/{len(emperors_to_crawl)}] 请求皇帝: {emperor_info['name']} - {url}")
            self.stats['requests_made'] += 1
            yield scrapy.Request(
                url=url,
                callback=self.parse_emperor,
                meta={'emperor_info': emperor_info},
                dont_filter=True,
                errback=self.handle_error
            )
    
    def _build_baidu_url(self, keyword: str) -> str:
        """构建百度百科URL"""
        return f"https://baike.baidu.com/item/{keyword}"
    
    def parse_emperor(self, response):
        """解析皇帝页面"""
        emperor_info = response.meta['emperor_info']


        self.logger.info(f"📥 接收到皇帝页面: {emperor_info}")
        emperor_name = emperor_info['name']
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"👑 开始解析皇帝: {emperor_name}")
        self.logger.info(f"   URL: {response.url}")
        self.logger.info(f"   状态码: {response.status}")
        self.logger.info(f"{'='*80}")
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取皇帝信息
            self.logger.info(f"📊 正在提取 {emperor_name} 的详细信息...")
            emperor_data = self._extract_emperor_data(soup, emperor_info)
            
            if emperor_data:
                self.stats['emperors'] += 1
                self.logger.info(f"✅ 成功提取皇帝数据: {emperor_data['name']}")
                self.logger.info(f"   - 庙号: {emperor_data.get('temple_name', '未知')}")
                self.logger.info(f"   - 年号: {emperor_data.get('reign_title', '未知')}")
                self.logger.info(f"   - 出生: {emperor_data.get('birth_date', '未知')}")
                self.logger.info(f"   - 去世: {emperor_data.get('death_date', '未知')}")
                self.logger.info(f"   - 简介长度: {len(emperor_data.get('biography', ''))} 字符")
                
                # 存储皇帝数据供后续使用
                emperor_id = generate_id("ming_emperor", emperor_data['name'], emperor_info['dynasty_order'])
                self.emperor_data[emperor_id] = emperor_data
                
                # 创建Emperor实体
                emperor = self._create_emperor_entity(emperor_data, emperor_info)
                yield emperor
                
                # 提取该皇帝时期的重大事件链接
                event_links = self._extract_event_links(soup)
                self.logger.info(f"🔍 发现 {len(event_links)} 个相关事件链接")
                
                event_count = 0
                for event_name in event_links[:10]:  # 限制每个皇帝最多爬取10个事件
                    url = self._build_baidu_url(event_name)
                    event_count += 1
                    self.stats['requests_made'] += 1
                    self.logger.info(f"   📤 [{event_count}/10] 请求事件: {event_name}")
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_event,
                        meta={'emperor_id': emperor_id, 'emperor_name': emperor_data['name']},
                        dont_filter=True,
                        errback=self.handle_error
                    )
                
                # 提取相关人物链接
                person_links = self._extract_person_links(soup)
                self.logger.info(f"🔍 发现 {len(person_links)} 个相关人物链接")
                
                person_count = 0
                for person_name in person_links[:20]:  # 限制每个皇帝最多爬取20个人物
                    url = self._build_baidu_url(person_name)
                    person_count += 1
                    self.stats['requests_made'] += 1
                    self.logger.info(f"   📤 [{person_count}/20] 请求人物: {person_name}")
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_person,
                        meta={'emperor_id': emperor_id},
                        dont_filter=True,
                        errback=self.handle_error
                    )
                
                self.logger.info(f"✅ 皇帝 {emperor_name} 解析完成\n")
            else:
                self.stats['parse_errors'] += 1
                self.logger.warning(f"⚠️ 未能提取到 {emperor_name} 的有效数据\n")
        
        except Exception as e:
            self.stats['parse_errors'] += 1
            self.logger.error(f"❌ 解析皇帝页面失败: {emperor_name}")
            self.logger.error(f"   错误信息: {str(e)}")
            self.logger.error(f"   错误类型: {type(e).__name__}\n")
    
    def _extract_emperor_data(self, soup: BeautifulSoup, emperor_info: Dict) -> Optional[Dict[str, Any]]:
        """从页面中提取皇帝数据
        
        百度百科已升级为动态加载，数据以JSON形式嵌入在script标签中
        同时保留传统DOM解析作为备用方案
        """
        data = {
            'name': emperor_info['name'],
            'temple_name': emperor_info.get('temple_name'),
            'reign_title': emperor_info.get('reign_title'),
            'biography': '',
            'achievements': '',
            'portrait_url': None,
            'infobox_data': {},  # 存储infobox中的所有信息
            'biography_html': ''  # 存储生平HTML内容
        }
        
        try:
            self.logger.info("  📋 开始提取皇帝详细信息...")
            
            # 方法1: 尝试从script标签中提取JSON数据（百度百科新版）
            self.logger.info("  🔍 尝试从JSON提取数据...")
            json_data_extracted = self._extract_from_json(soup, data)
            
            # 方法2: 传统DOM解析（作为备用）
            if not json_data_extracted:
                self.logger.info("  → JSON提取未成功，使用传统DOM解析方式")
                self._extract_from_dom(soup, data)
            else:
                self.logger.info("  ✓ 成功从JSON提取数据")
            
            # 方法3: 提取infobox中的<tr>标签信息
            self.logger.info("  🔍 提取infobox表格数据...")
            self._extract_infobox_table(soup, data)
            
            # 记录提取结果
            self.logger.info(f"  📊 提取结果统计:")
            self.logger.info(f"     - 出生日期: {'✓' if data.get('birth_date') else '✗'}")
            self.logger.info(f"     - 去世日期: {'✓' if data.get('death_date') else '✗'}")
            self.logger.info(f"     - 简介长度: {len(data.get('biography', ''))} 字符")
            self.logger.info(f"     - 成就长度: {len(data.get('achievements', ''))} 字符")
            self.logger.info(f"     - 画像URL: {'✓' if data.get('portrait_url') else '✗'}")
            self.logger.info(f"     - Infobox字段: {len(data.get('infobox_data', {}))} 项")
        
        except Exception as e:
            self.logger.error(f"  ❌ 提取皇帝详细信息时出错: {str(e)}")
            import traceback
            self.logger.debug(f"  错误堆栈: {traceback.format_exc()}")
        
        return data
    
    def _extract_from_json(self, soup: BeautifulSoup, data: Dict) -> bool:
        """从页面中的JSON数据提取信息（百度百科新版）"""
        try:
            import json
            
            # 查找包含lemmaBasicInfo的script标签
            for script in soup.find_all('script'):
                if not script.string:
                    continue
                    
                script_text = script.string
                
                # 查找基础信息JSON
                if '"lemmaBasicInfo"' in script_text or '"basicInfo"' in script_text:
                    # 提取出生日期
                    birth_match = re.search(r'"dateOfBirth".*?"text":\[\{"tag":"text","text":"([^"]+)"', script_text)
                    if birth_match:
                        birth_text = birth_match.group(1)
                        data['birth_date'] = self.date_parser.parse_chinese_date(birth_text)
                        self.logger.debug(f"    提取到出生日期: {birth_text}")
                    
                    # 提取逝世日期
                    death_match = re.search(r'"dateOfDeath".*?"text":\[\{"tag":"text","text":"([^"]+)"', script_text)
                    if death_match:
                        death_text = death_match.group(1)
                        data['death_date'] = self.date_parser.parse_chinese_date(death_text)
                        self.logger.debug(f"    提取到逝世日期: {death_text}")
                    
                    # 提取主要成就
                    achievement_match = re.search(r'"majorAchievement".*?"data":\[(.*?)\]\}', script_text)
                    if achievement_match:
                        achievement_json = achievement_match.group(1)
                        # 提取所有成就文本
                        achievement_texts = re.findall(r'"text":"([^"]+)"', achievement_json)
                        if achievement_texts:
                            data['achievements'] = '；'.join(achievement_texts)
                            self.logger.debug(f"    提取到主要成就: {len(achievement_texts)}项")
                
                # 查找描述信息
                if '"description"' in script_text:
                    desc_match = re.search(r'"description":"([^"]+)"', script_text)
                    if desc_match:
                        description = desc_match.group(1)
                        # 如果简介为空，使用描述
                        if not data['biography']:
                            data['biography'] = description
                            self.logger.debug(f"    提取到描述: {len(description)}字符")
            
            # 检查是否成功提取到关键信息
            if data.get('birth_date') or data.get('biography'):
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"    JSON提取失败: {str(e)}")
            return False
    
    def _extract_from_dom(self, soup: BeautifulSoup, data: Dict) -> None:
        """从DOM结构提取信息（传统方式）"""
        try:
            self.logger.debug("    🔍 开始DOM解析...")
            
            # 提取基础信息框
            info_box = soup.select_one('.basic-info')
            if info_box:
                self.logger.debug("    ✓ 找到基础信息框")
                
                # 提取出生日期
                birth_elem = info_box.find('dt', string=re.compile('出生日期|出生时间'))
                if birth_elem and birth_elem.find_next_sibling('dd'):
                    birth_text = birth_elem.find_next_sibling('dd').get_text(strip=True)
                    data['birth_date'] = self.date_parser.parse_chinese_date(birth_text)
                    self.logger.debug(f"    ✓ 提取出生日期: {birth_text}")
                
                # 提取去世日期
                death_elem = info_box.find('dt', string=re.compile('逝世日期|逝世时间'))
                if death_elem and death_elem.find_next_sibling('dd'):
                    death_text = death_elem.find_next_sibling('dd').get_text(strip=True)
                    data['death_date'] = self.date_parser.parse_chinese_date(death_text)
                    self.logger.debug(f"    ✓ 提取去世日期: {death_text}")
            else:
                self.logger.debug("    ✗ 未找到基础信息框")
            
            # 提取简介 - 尝试多种选择器
            biography_texts = []
            
            # 尝试1: lemma-summary
            summary = soup.select_one('.lemma-summary')
            if summary:
                self.logger.debug("    ✓ 找到lemma-summary")
                paragraphs = summary.find_all('div', class_='para')
                for para in paragraphs[:3]:  # 提取前3段
                    text = clean_text(para.get_text())
                    if text:
                        biography_texts.append(text)
                self.logger.debug(f"    ✓ 提取了 {len(biography_texts)} 段简介")
            
            # 尝试2: 查找所有段落
            if not biography_texts:
                self.logger.debug("    → 尝试查找所有段落...")
                all_paras = soup.find_all('div', class_='para')
                for para in all_paras[:5]:  # 提取前5段
                    text = clean_text(para.get_text())
                    if text and len(text) > 50:  # 过滤太短的段落
                        biography_texts.append(text)
                self.logger.debug(f"    ✓ 从所有段落中提取了 {len(biography_texts)} 段")
            
            if biography_texts:
                data['biography'] = '\n'.join(biography_texts)
                self.logger.debug(f"    ✓ 简介总长度: {len(data['biography'])} 字符")
            
            # 提取主要成就 - 尝试多种方式
            # 方式1: 查找data-title
            achievement_section = soup.find('div', {'data-title': '主要成就'})
            if achievement_section:
                data['achievements'] = clean_text(achievement_section.get_text())
                self.logger.debug(f"    ✓ 从data-title提取成就: {len(data['achievements'])} 字符")
            
            # 方式2: 查找包含"主要成就"的标题
            if not data['achievements']:
                for heading in soup.find_all(['h2', 'h3']):
                    if '主要成就' in heading.get_text():
                        # 提取该标题后的内容
                        next_elem = heading.find_next_sibling()
                        if next_elem:
                            data['achievements'] = clean_text(next_elem.get_text())
                            self.logger.debug(f"    ✓ 从标题提取成就: {len(data['achievements'])} 字符")
                            break
            
            # 提取画像URL
            portrait = soup.select_one('.summary-pic img')
            if portrait and portrait.get('src'):
                data['portrait_url'] = portrait['src']
                self.logger.debug(f"    ✓ 提取画像URL: {data['portrait_url'][:60]}...")
        
        except Exception as e:
            self.logger.error(f"    ❌ DOM提取出错: {str(e)}")
            import traceback
            self.logger.debug(f"    错误堆栈: {traceback.format_exc()}")
    
    def _extract_infobox_table(self, soup: BeautifulSoup, data: Dict) -> None:
        """
        从infobox表格中提取<tr>标签信息
        百度百科的基础信息通常在.basic-info表格中，每行是一个<tr>标签
        """
        try:
            self.logger.debug("    🔍 开始提取infobox表格...")
            
            # 查找基础信息表格
            # 百度百科可能使用: .basic-info, .basicInfo-block, table.infobox等
            info_tables = []
            
            # 尝试多种选择器
            selectors = [
                '.basic-info',
                '.basicInfo-block table',
                'table.infobox',
                '.lemma-table',
            ]
            
            for selector in selectors:
                table = soup.select_one(selector)
                if table:
                    info_tables.append(table)
                    self.logger.debug(f"    ✓ 找到表格: {selector}")
                    break
            
            if not info_tables:
                self.logger.debug("    ⚠ 未找到infobox表格")
                return
            
            # 遍历表格行
            for table in info_tables:
                rows = table.find_all('tr')
                self.logger.debug(f"    📊 找到 {len(rows)} 行数据")
                
                row_count = 0
                for row in rows:
                    try:
                        # 提取表头和表数据
                        th = row.find(['th', 'dt'])
                        td = row.find(['td', 'dd'])
                        
                        if not th or not td:
                            continue
                        
                        row_count += 1
                        field_name = clean_text(th.get_text())
                        field_value = clean_text(td.get_text())
                        
                        if not field_name or not field_value:
                            continue
                        
                        # 存储到infobox_data
                        data['infobox_data'][field_name] = field_value
                        self.logger.debug(f"    📌 [{row_count}] {field_name}: {field_value[:50]}...")
                        
                        # 根据字段名提取特定信息
                        field_name_lower = field_name.lower()
                        
                        # 出生日期
                        if any(keyword in field_name for keyword in ['出生日期', '出生时间', '出生', '生于']):
                            if not data.get('birth_date'):
                                parsed_date = self.date_parser.parse_chinese_date(field_value)
                                if parsed_date:
                                    data['birth_date'] = parsed_date
                                    self.logger.debug(f"    ✓ 从表格提取出生日期: {field_value} -> {parsed_date}")
                        
                        # 去世日期
                        elif any(keyword in field_name for keyword in ['逝世日期', '逝世时间', '逝世', '卒于', '去世']):
                            if not data.get('death_date'):
                                parsed_date = self.date_parser.parse_chinese_date(field_value)
                                if parsed_date:
                                    data['death_date'] = parsed_date
                                    self.logger.debug(f"    ✓ 从表格提取去世日期: {field_value} -> {parsed_date}")
                        
                        # 在位时间
                        elif any(keyword in field_name for keyword in ['在位时间', '在位', '统治时间']):
                            data['infobox_data']['reign_period'] = field_value
                            self.logger.debug(f"    ✓ 从表格提取在位时间: {field_value}")
                        
                        # 庙号
                        elif any(keyword in field_name for keyword in ['庙号']):
                            if not data.get('temple_name'):
                                data['temple_name'] = field_value
                                data['infobox_data']['temple_name'] = field_value
                                self.logger.debug(f"    ✓ 从表格提取庙号: {field_value}")
                        
                        # 谥号
                        elif any(keyword in field_name for keyword in ['谥号']):
                            data['infobox_data']['posthumous_name'] = field_value
                            self.logger.debug(f"    ✓ 从表格提取谥号: {field_value}")
                        
                        # 年号
                        elif any(keyword in field_name for keyword in ['年号']):
                            if not data.get('reign_title'):
                                data['reign_title'] = field_value
                                data['infobox_data']['era_name'] = field_value
                                self.logger.debug(f"    ✓ 从表格提取年号: {field_value}")
                        
                        # 陵寝
                        elif any(keyword in field_name for keyword in ['陵墓', '陵寝']):
                            data['infobox_data']['tomb'] = field_value
                            self.logger.debug(f"    ✓ 从表格提取陵寝: {field_value}")
                        
                        # 皇后
                        elif any(keyword in field_name for keyword in ['皇后']):
                            data['infobox_data']['empress'] = field_value
                            self.logger.debug(f"    ✓ 从表格提取皇后: {field_value}")
                        
                    except Exception as row_error:
                        self.logger.debug(f"    ⚠ 处理行时出错: {str(row_error)}")
                        continue
                
                # 尝试提取图片URL
                if not data.get('portrait_url'):
                    img = table.find('img')
                    if img and img.get('src'):
                        # 处理相对路径
                        img_url = img['src']
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://baike.baidu.com' + img_url
                        
                        data['portrait_url'] = img_url
                        data['infobox_data']['portrait_url'] = img_url
                        self.logger.debug(f"    ✓ 从表格提取图片URL: {img_url[:60]}...")
            
            self.logger.debug(f"    ✓ Infobox表格提取完成，共 {len(data['infobox_data'])} 个字段")
        
        except Exception as e:
            self.logger.error(f"    ❌ 提取infobox表格时出错: {str(e)}")
            import traceback
            self.logger.debug(f"    错误堆栈: {traceback.format_exc()}")
    
    def _create_emperor_entity(self, emperor_data: Dict, emperor_info: Dict) -> Emperor:
        """创建皇帝实体"""
        emperor_id = generate_id("ming_emperor", emperor_data['name'], emperor_info['dynasty_order'])
        
        self.logger.info(f"  🔨 创建Emperor实体: {emperor_id}")
        
        # 解析在位时间
        reign_years = emperor_info.get('reign_years', '')
        reign_start, reign_end = self._parse_reign_years(reign_years)
        
        emperor = Emperor(
            emperor_id=emperor_id,
            dynasty_id=MING_DYNASTY['dynasty_id'],
            name=emperor_data['name'],
            temple_name=emperor_data.get('temple_name'),
            reign_title=emperor_data.get('reign_title'),
            birth_date=emperor_data.get('birth_date'),
            death_date=emperor_data.get('death_date'),
            reign_start=reign_start,
            reign_end=reign_end,
            dynasty_order=emperor_info['dynasty_order'],
            biography=emperor_data.get('biography'),
            achievements=emperor_data.get('achievements'),
            portrait_url=emperor_data.get('portrait_url'),
            html_content=emperor_data.get('biography_html', ''),
            source_url=f"https://baike.baidu.com/item/{emperor_data['name']}",
            data_source='baidu'
        )
        
        self.logger.info(f"  ✓ Emperor实体创建成功")
        return emperor
    
    def _parse_reign_years(self, reign_years_str: str) -> tuple:
        """解析在位年份"""
        try:
            # 格式: "1368-1398" 或 "1435-1449, 1457-1464"
            years = reign_years_str.split(',')[0].strip()
            start_year, end_year = years.split('-')
            return (date(int(start_year), 1, 1), date(int(end_year), 12, 31))
        except Exception:
            return (date(1368, 1, 1), None)
    
    def _extract_event_links(self, soup: BeautifulSoup) -> List[str]:
        """提取事件相关链接"""
        events = []
        
        # 从正文中提取事件链接
        content = soup.select_one('.main-content')
        if content:
            # 查找包含特定关键词的链接
            event_keywords = ['之役', '之战', '之变', '政变', '起义', '改革', '运动', '下西洋', '案']
            links = content.find_all('a', href=True)
            
            for link in links:
                link_text = link.get_text(strip=True)
                if any(keyword in link_text for keyword in event_keywords):
                    if link_text and len(link_text) < 20:  # 过滤过长的文本
                        events.append(link_text)
        
        return list(set(events))[:15]  # 去重并限制数量
    
    def _extract_person_links(self, soup: BeautifulSoup) -> List[str]:
        """提取人物相关链接"""
        persons = []
        
        # 从正文中提取人物链接
        content = soup.select_one('.main-content')
        if content:
            # 查找人名链接（通常是2-4个字）
            links = content.find_all('a', href=True)
            
            for link in links:
                link_text = link.get_text(strip=True)
                # 简单的人名判断：2-4个中文字符
                if link_text and 2 <= len(link_text) <= 4 and all('\u4e00' <= c <= '\u9fff' for c in link_text):
                    persons.append(link_text)
        
        return list(set(persons))[:25]  # 去重并限制数量
    
    def parse_event(self, response):
        """解析事件页面"""
        emperor_id = response.meta.get('emperor_id')
        emperor_name = response.meta.get('emperor_name')
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"📖 开始解析事件页面")
        self.logger.info(f"   URL: {response.url}")
        self.logger.info(f"   关联皇帝: {emperor_name} ({emperor_id})")
        self.logger.info(f"{'='*60}")
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取事件数据
            self.logger.info("🔍 开始提取事件数据...")
            event_data = self._extract_event_data(soup, emperor_id)
            
            if event_data:
                self.stats['events'] += 1
                self.logger.info(f"✅ 成功爬取事件: {event_data.title}")
                self.logger.info(f"   - 类型: {event_data.event_type.value}")
                self.logger.info(f"   - 时间: {event_data.start_date}")
                self.logger.info(f"   - 地点: {event_data.location or '未知'}")
                self.logger.info(f"   - 关联皇帝: {emperor_name}")
                yield event_data
            else:
                self.stats['parse_errors'] += 1
                self.logger.warning(f"⚠️ 事件数据提取失败: {response.url}")
        
        except Exception as e:
            self.stats['parse_errors'] += 1
            self.logger.error(f"❌ 解析事件页面失败: {response.url}")
            self.logger.error(f"   错误信息: {str(e)}")
            import traceback
            self.logger.debug(f"   错误堆栈: {traceback.format_exc()}")
    
    def _extract_event_data(self, soup: BeautifulSoup, emperor_id: str) -> Optional[Dict]:
        """从页面中提取事件数据"""
        try:
            self.logger.debug("  🔍 开始提取事件详细信息...")
            
            # 获取标题
            title_elem = soup.select_one('.lemmaWgt-lemmaTitle-title h1')
            if not title_elem:
                self.logger.warning("  ✗ 未找到事件标题")
                return None
            
            title = clean_text(title_elem.get_text())
            self.logger.debug(f"  ✓ 提取标题: {title}")
            
            data = {
                'title': title,
                'event_type': self._determine_event_type(title, soup),
                'start_date': None,
                'end_date': None,
                'location': None,
                'description': '',
                'significance': '',
                'emperor_id': emperor_id
            }
            
            self.logger.debug(f"  ✓ 判断事件类型: {data['event_type'].value}")
            
            # 提取基础信息框
            info_box = soup.select_one('.basic-info')
            if info_box:
                self.logger.debug("  ✓ 找到基础信息框")
                
                # 提取时间
                time_elem = info_box.find('dt', string=re.compile('时间|发生时间|年代'))
                if time_elem and time_elem.find_next_sibling('dd'):
                    time_text = time_elem.find_next_sibling('dd').get_text(strip=True)
                    data['start_date'] = self.date_parser.parse_chinese_date(time_text)
                    self.logger.debug(f"  ✓ 提取时间: {time_text} -> {data['start_date']}")
                
                # 提取地点
                location_elem = info_box.find('dt', string=re.compile('地点|发生地点'))
                if location_elem and location_elem.find_next_sibling('dd'):
                    data['location'] = clean_text(location_elem.find_next_sibling('dd').get_text())
                    self.logger.debug(f"  ✓ 提取地点: {data['location']}")
            else:
                self.logger.debug("  ✗ 未找到基础信息框")
            
            # 提取描述
            summary = soup.select_one('.lemma-summary')
            if summary:
                paragraphs = summary.find_all('div', class_='para')
                if paragraphs:
                    data['description'] = clean_text(paragraphs[0].get_text())
                    self.logger.debug(f"  ✓ 提取描述: {len(data['description'])} 字符")
            
            # 创建Event实体
            event_id = generate_id("ming_event", title)
            self.logger.debug(f"  ✓ 生成event_id: {event_id}")
            
            event = Event(
                event_id=event_id,
                dynasty_id=MING_DYNASTY['dynasty_id'],
                emperor_id=emperor_id,
                title=data['title'],
                event_type=data['event_type'],
                start_date=data['start_date'] or date(1368, 1, 1),
                end_date=data.get('end_date'),
                location=data.get('location'),
                description=data.get('description'),
                significance=data.get('significance'),
                source_url=f"https://baike.baidu.com/item/{title}",
                data_source='baidu'
            )
            
            self.logger.debug(f"  ✓ Event实体创建成功")
            return event
        
        except Exception as e:
            self.logger.error(f"  ❌ 提取事件数据时出错: {str(e)}")
            import traceback
            self.logger.debug(f"  错误堆栈: {traceback.format_exc()}")
            return None
    
    def _determine_event_type(self, title: str, soup: BeautifulSoup) -> EventType:
        """根据标题和内容判断事件类型"""
        if any(keyword in title for keyword in ['之战', '之役', '战争', '战役']):
            return EventType.MILITARY
        elif any(keyword in title for keyword in ['政变', '改革', '废除', '设立']):
            return EventType.POLITICAL
        elif any(keyword in title for keyword in ['文化', '运动', '著作']):
            return EventType.CULTURAL
        elif any(keyword in title for keyword in ['贸易', '下西洋', '通商']):
            return EventType.DIPLOMATIC
        else:
            return EventType.POLITICAL  # 默认为政治事件
    
    def parse_person(self, response):
        """解析人物页面"""
        emperor_id = response.meta.get('emperor_id')
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"👤 开始解析人物页面")
        self.logger.info(f"   URL: {response.url}")
        self.logger.info(f"   关联皇帝 ID: {emperor_id}")
        self.logger.info(f"{'='*60}")
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取人物数据
            self.logger.info("🔍 开始提取人物数据...")
            person_data = self._extract_person_data(soup, emperor_id)
            
            if person_data:
                self.stats['persons'] += 1
                self.logger.info(f"✅ 成功爬取人物: {person_data.name}")
                self.logger.info(f"   - 类型: {person_data.person_type.value}")
                self.logger.info(f"   - 职位: {person_data.position or '未知'}")
                self.logger.info(f"   - 生卒: {person_data.birth_date or '?'} - {person_data.death_date or '?'}")
                yield person_data
            else:
                self.stats['parse_errors'] += 1
                self.logger.warning(f"⚠️ 人物数据提取失败: {response.url}")
        
        except Exception as e:
            self.stats['parse_errors'] += 1
            self.logger.error(f"❌ 解析人物页面失败: {response.url}")
            self.logger.error(f"   错误信息: {str(e)}")
            import traceback
            self.logger.debug(f"   错误堆栈: {traceback.format_exc()}")
    
    def _extract_person_data(self, soup: BeautifulSoup, emperor_id: str) -> Optional[Person]:
        """从页面中提取人物数据"""
        try:
            self.logger.debug("  🔍 开始提取人物详细信息...")
            
            # 获取人名
            title_elem = soup.select_one('.lemmaWgt-lemmaTitle-title h1')
            if not title_elem:
                self.logger.warning("  ✗ 未找到人物名称")
                return None
            
            name = clean_text(title_elem.get_text())
            self.logger.debug(f"  ✓ 提取人名: {name}")
            
            # 提取基础信息
            alias_list = []
            birth_date = None
            death_date = None
            position = None
            person_type = PersonType.OTHER
            
            info_box = soup.select_one('.basic-info')
            if info_box:
                self.logger.debug("  ✓ 找到基础信息框")
                
                # 提取别名、字号
                alias_elem = info_box.find('dt', string=re.compile('别名|字号|本名'))
                if alias_elem and alias_elem.find_next_sibling('dd'):
                    alias_text = alias_elem.find_next_sibling('dd').get_text(strip=True)
                    alias_list = [a.strip() for a in re.split('[，、]', alias_text) if a.strip()]
                    self.logger.debug(f"  ✓ 提取别名: {len(alias_list)} 个")
                
                # 提取出生日期
                birth_elem = info_box.find('dt', string=re.compile('出生日期|出生时间'))
                if birth_elem and birth_elem.find_next_sibling('dd'):
                    birth_text = birth_elem.find_next_sibling('dd').get_text(strip=True)
                    birth_date = self.date_parser.parse_chinese_date(birth_text)
                    self.logger.debug(f"  ✓ 提取出生日期: {birth_text} -> {birth_date}")
                
                # 提取去世日期
                death_elem = info_box.find('dt', string=re.compile('逝世日期|逝世时间'))
                if death_elem and death_elem.find_next_sibling('dd'):
                    death_text = death_elem.find_next_sibling('dd').get_text(strip=True)
                    death_date = self.date_parser.parse_chinese_date(death_text)
                    self.logger.debug(f"  ✓ 提取去世日期: {death_text} -> {death_date}")
                
                # 提取职位
                position_elem = info_box.find('dt', string=re.compile('职业|主要成就|职务'))
                if position_elem and position_elem.find_next_sibling('dd'):
                    position = clean_text(position_elem.find_next_sibling('dd').get_text())
                    # 根据职位判断人物类型
                    person_type = self._determine_person_type(position, soup)
                    self.logger.debug(f"  ✓ 提取职位: {position} -> 类型: {person_type.value}")
            else:
                self.logger.debug("  ✗ 未找到基础信息框")
            
            # 提取生平
            biography = ''
            summary = soup.select_one('.lemma-summary')
            if summary:
                paragraphs = summary.find_all('div', class_='para')
                if paragraphs:
                    biography = clean_text(paragraphs[0].get_text())
                    self.logger.debug(f"  ✓ 提取生平: {len(biography)} 字符")
            
            # 创建Person实体
            person_id = generate_id("ming_person", name)
            self.logger.debug(f"  ✓ 生成person_id: {person_id}")
            
            person = Person(
                person_id=person_id,
                dynasty_id=MING_DYNASTY['dynasty_id'],
                name=name,
                person_type=person_type,
                alias=alias_list,
                birth_date=birth_date,
                death_date=death_date,
                position=position,
                biography=biography,
                related_emperors=[emperor_id] if emperor_id else [],
                source_url=f"https://baike.baidu.com/item/{name}",
                data_source='baidu'
            )
            
            self.logger.debug(f"  ✓ Person实体创建成功")
            return person
        
        except Exception as e:
            self.logger.error(f"  ❌ 提取人物数据时出错: {str(e)}")
            import traceback
            self.logger.debug(f"  错误堆栈: {traceback.format_exc()}")
            return None
    
    def _determine_person_type(self, position: str, soup: BeautifulSoup) -> PersonType:
        """根据职位和内容判断人物类型"""
        if not position:
            return PersonType.OTHER
        
        position_lower = position.lower()
        
        if any(keyword in position for keyword in ['将军', '将领', '武', '军']):
            return PersonType.GENERAL
        elif any(keyword in position for keyword in ['诗人', '文学', '作家', '词人']):
            return PersonType.WRITER
        elif any(keyword in position for keyword in ['画家', '书法', '艺术']):
            return PersonType.ARTIST
        elif any(keyword in position for keyword in ['大臣', '尚书', '侍郎', '学士', '阁']):
            return PersonType.OFFICIAL
        elif any(keyword in position for keyword in ['皇子', '皇后', '妃']):
            return PersonType.ROYAL
        elif any(keyword in position for keyword in ['僧', '道']):
            return PersonType.MONK
        elif any(keyword in position for keyword in ['思想', '哲学']):
            return PersonType.THINKER
        elif any(keyword in position for keyword in ['科学', '天文', '数学', '医']):
            return PersonType.SCIENTIST
        else:
            return PersonType.OTHER
    
    def handle_error(self, failure):
        """处理请求错误"""
        self.stats['requests_failed'] += 1
        self.logger.error(f"❌ 请求失败: {failure.request.url}")
        self.logger.error(f"   错误类型: {failure.type.__name__}")
        self.logger.error(f"   错误信息: {failure.getErrorMessage()}")
    
    def closed(self, reason):
        """爬虫关闭时调用"""
        self.logger.info("\n" + "="*80)
        self.logger.info("🏁 爬虫运行结束")
        self.logger.info(f"   关闭原因: {reason}")
        self.logger.info("="*80)
        
        self.logger.info("\n📊 爬取统计报告:")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"成功爬取数据：")
        self.logger.info(f"  - 皇帝: {self.stats['emperors']} 位")
        self.logger.info(f"  - 事件: {self.stats['events']} 个")
        self.logger.info(f"  - 人物: {self.stats['persons']} 位")
        self.logger.info(f"  - 总计: {self.stats['emperors'] + self.stats['events'] + self.stats['persons']} 条")
        self.logger.info(f"")
        self.logger.info(f"请求统计：")
        self.logger.info(f"  - 发送请求: {self.stats['requests_made']} 次")
        self.logger.info(f"  - 请求失败: {self.stats['requests_failed']} 次")
        self.logger.info(f"  - 解析错误: {self.stats['parse_errors']} 次")
        self.logger.info(f"")
        
        # 计算成功率
        total_requests = self.stats['requests_made']
        if total_requests > 0:
            success_rate = ((total_requests - self.stats['requests_failed']) / total_requests) * 100
            self.logger.info(f"成功率：")
            self.logger.info(f"  - 请求成功率: {success_rate:.2f}%")
            
            total_items = self.stats['emperors'] + self.stats['events'] + self.stats['persons']
            if total_items > 0:
                data_quality = ((total_items - self.stats['parse_errors']) / total_items) * 100
                self.logger.info(f"  - 数据质量率: {data_quality:.2f}%")
        
        self.logger.info(f"{'='*80}")
        
        # 检查是否成功
        if self.stats['emperors'] > 0:
            self.logger.info("✅ 爬取任务成功完成！")
        else:
            self.logger.error("❌ 警告：未能爬取到任何皇帝数据！")
        
        self.logger.info("="*80 + "\n")
