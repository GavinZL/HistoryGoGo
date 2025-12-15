"""
维基百科爬虫
用于爬取明朝皇帝、事件、人物信息（中文维基百科）
"""

import scrapy
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import re
from datetime import date

from crawler.models.entities import Emperor, Event, Person, EventType, PersonType
from crawler.utils.date_utils import DateParser, clean_text, generate_id
from crawler.config.ming_data import MING_EMPERORS, MING_DYNASTY


class WikipediaSpider(scrapy.Spider):
    """维基百科爬虫"""
    
    name = 'wikipedia'
    allowed_domains = ['zh.wikipedia.org']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 4,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_parser = DateParser()
    
    def start_requests(self):
        """生成起始请求"""
        # 从 settings 中获取爬取模式配置
        crawl_mode = self.settings.get('CRAWL_MODE', 'test')
        test_emperor_count = self.settings.get('TEST_EMPEROR_COUNT', 3)
        
        # 根据爬取模式决定爬取多少位皇帝
        emperors_to_crawl = MING_EMPERORS
        if crawl_mode == 'test':
            emperors_to_crawl = MING_EMPERORS[:test_emperor_count]
            self.logger.info(f"[Wiki] 测试模式：只爬取前{test_emperor_count}位皇帝")
        else:
            self.logger.info(f"[Wiki] 全量模式：爬取所有{len(MING_EMPERORS)}位皇帝")
        
        # 爬取皇帝信息
        for emperor_info in emperors_to_crawl:
            url = self._build_wiki_url(emperor_info['name'])
            yield scrapy.Request(
                url=url,
                callback=self.parse_emperor,
                meta={'emperor_info': emperor_info},
                dont_filter=True
            )
    
    def _build_wiki_url(self, keyword: str) -> str:
        """构建维基百科URL"""
        return f"https://zh.wikipedia.org/wiki/{keyword}"
    
    def parse_emperor(self, response):
        """解析皇帝页面"""
        emperor_info = response.meta['emperor_info']
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"👑 [维基] 开始解析皇帝: {emperor_info['name']}")
        self.logger.info(f"   URL: {response.url}")
        self.logger.info(f"   朝代顺序: {emperor_info.get('dynasty_order')}")
        self.logger.info(f"{'='*80}")
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取皇帝信息
            self.logger.info(f"📋 开始提取 {emperor_info['name']} 的详细信息...")
            emperor_data = self._extract_emperor_data(soup, emperor_info)
            
            if emperor_data:
                self.logger.info(f"✅ 成功爱取皇帝: {emperor_data['name']}")
                self.logger.info(f"   - 庙号: {emperor_data.get('temple_name', '未知')}")
                self.logger.info(f"   - 年号: {emperor_data.get('reign_title', '未知')}")
                self.logger.info(f"   - 出生: {emperor_data.get('birth_date', '未知')}")
                self.logger.info(f"   - 去世: {emperor_data.get('death_date', '未知')}")
                self.logger.info(f"   - 简介长度: {len(emperor_data.get('biography', ''))} 字符")
                self.logger.info(f"   - Infobox字段: {len(emperor_data.get('infobox_data', {}))} 项")
                
                # 创建Emperor实体
                emperor = self._create_emperor_entity(emperor_data, emperor_info)
                yield emperor
                
        except Exception as e:
            self.logger.error(f"❌ [维基] 解析皇帝页面失败: {emperor_info['name']}, 错误: {str(e)}")
            import traceback
            self.logger.debug(f"   错误堆栈: {traceback.format_exc()}")
    
    def _extract_emperor_data(self, soup: BeautifulSoup, emperor_info: Dict) -> Optional[Dict[str, Any]]:
        """从维基百科页面中提取皇帝数据"""
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
            self.logger.info("  🔍 开始提取infobox表格数据...")
            
            # 提取Infobox信息框（基于<tr>标签解析）
            infobox = soup.find('table', class_='infobox')
            if infobox:
                self.logger.info("  ✓ 找到infobox表格")
                self._extract_infobox_table(infobox, data)
            else:
                self.logger.warning("  ⚠ 未找到infobox表格")
            
            # 提取首段简介
            content = soup.find('div', class_='mw-parser-output')
            if content:
                # 获取第一个段落（通常是简介）
                first_para = content.find('p', recursive=False)
                if first_para:
                    # 移除引用标记
                    for sup in first_para.find_all('sup'):
                        sup.decompose()
                    data['biography'] = clean_text(first_para.get_text())
                
                # 提取生平内容（从mw-heading mw-heading2开始到下一个mw-heading2）
                data['biography_html'] = self._extract_biography_section(soup)
            
            # 尝试提取"主要成就"相关内容
            # 在维基百科中可能在不同的章节
            for heading in soup.find_all(['h2', 'h3']):
                heading_text = heading.get_text()
                if any(keyword in heading_text for keyword in ['成就', '贡献', '政绩']):
                    next_elem = heading.find_next_sibling()
                    if next_elem and next_elem.name in ['p', 'ul']:
                        data['achievements'] = clean_text(next_elem.get_text())
                        break
            
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
    
    def _extract_infobox_table(self, infobox, data: Dict) -> None:
        """
        从infobox表格中提取<tr>标签信息
        维基百科的基础信息在infobox表格中，每行是一个<tr>标签
        """
        try:
            self.logger.debug("    🔍 开始提取infobox表格行...")
            
            # 遍历表格行
            rows = infobox.find_all('tr')
            self.logger.debug(f"    📊 找到 {len(rows)} 行数据")
            
            row_count = 0
            for row in rows:
                try:
                    # 提取表头和表数据
                    th = row.find('th')
                    td = row.find('td')
                    
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
                    # 出生日期
                    if any(keyword in field_name for keyword in ['出生', '誕生', '生于']):
                        if not data.get('birth_date'):
                            parsed_date = self.date_parser.parse_chinese_date(field_value)
                            if parsed_date:
                                data['birth_date'] = parsed_date
                                self.logger.debug(f"    ✓ 从表格提取出生日期: {field_value} -> {parsed_date}")
                    
                    # 去世日期
                    elif any(keyword in field_name for keyword in ['逝世', '卒于', '去世']):
                        if not data.get('death_date'):
                            parsed_date = self.date_parser.parse_chinese_date(field_value)
                            if parsed_date:
                                data['death_date'] = parsed_date
                                self.logger.debug(f"    ✓ 从表格提取去世日期: {field_value} -> {parsed_date}")
                    
                    # 在位时间/统治
                    elif any(keyword in field_name for keyword in ['统治', '在位', 'reign']):
                        data['infobox_data']['reign'] = field_value
                        self.logger.debug(f"    ✓ 从表格提取在位时间: {field_value}")
                    
                    # 庙号
                    elif any(keyword in field_name for keyword in ['庙号']):
                        if not data.get('temple_name'):
                            data['temple_name'] = field_value
                            self.logger.debug(f"    ✓ 从表格提取庙号: {field_value}")
                    
                    # 谥号
                    elif any(keyword in field_name for keyword in ['谥号']):
                        data['infobox_data']['posthumous_name'] = field_value
                        self.logger.debug(f"    ✓ 从表格提取谥号: {field_value}")
                    
                    # 年号
                    elif any(keyword in field_name for keyword in ['年号', '年號']):
                        if not data.get('reign_title'):
                            data['reign_title'] = field_value
                            self.logger.debug(f"    ✓ 从表格提取年号: {field_value}")
                    
                    # 陵墓
                    elif any(keyword in field_name for keyword in ['陵墓', '陵寝', '安葬']):
                        data['infobox_data']['tomb'] = field_value
                        self.logger.debug(f"    ✓ 从表格提取陵墓: {field_value}")
                    
                    # 皇后
                    elif any(keyword in field_name for keyword in ['皇后']):
                        data['infobox_data']['empress'] = field_value
                        self.logger.debug(f"    ✓ 从表格提取皇后: {field_value}")
                    
                except Exception as row_error:
                    self.logger.debug(f"    ⚠ 处理行时出错: {str(row_error)}")
                    continue
            
            # 尝试提取图片URL
            if not data.get('portrait_url'):
                img = infobox.find('img')
                if img and img.get('src'):
                    img_url = img['src']
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://zh.wikipedia.org' + img_url
                    
                    data['portrait_url'] = img_url
                    data['infobox_data']['portrait_url'] = img_url
                    self.logger.debug(f"    ✓ 从表格提取图片URL: {img_url[:60]}...")
            
            self.logger.debug(f"    ✓ Infobox表格提取完成，共 {len(data['infobox_data'])} 个字段")
        
        except Exception as e:
            self.logger.error(f"    ❌ 提取infobox表格时出错: {str(e)}")
            import traceback
            self.logger.debug(f"    错误堆栈: {traceback.format_exc()}")
    
    def _extract_biography_section(self, soup: BeautifulSoup) -> str:
        """
        提取生平章节的HTML内容
        查找标题包含"生平"、"早期"等关键词的章节
        支持桌面版和移动版两种HTML结构：
        - 桌面版：<div class="mw-heading mw-heading2"><h2 id="生平">...</h2></div>
        - 移动版：<div class="mw-heading mw-heading2 section-heading" onclick="..."><h2 id="生平">...</h2></div>
        """
        try:
            self.logger.debug("    🔍 开始提取生平章节HTML...")
            
            # 查找所有 mw-heading2，找到第一个标题包含生平相关关键词的章节
            all_headings = soup.find_all('div', class_=lambda x: x and 'mw-heading' in x and 'mw-heading2' in x)
            
            if not all_headings:
                self.logger.warning("    ⚠ 未找到任何mw-heading2标题")
                return ''
            
            # 查找生平相关章节（按优先级匹配）
            biography_keywords = ['生平', '早期', '经历', '即位', '登基']
            first_heading = None
            
            for heading in all_headings:
                h2_elem = heading.find('h2')
                if h2_elem:
                    h2_text = h2_elem.get_text()
                    if any(keyword in h2_text for keyword in biography_keywords):
                        first_heading = heading
                        self.logger.debug(f"    ✓ 找到生平相关章节: {h2_text}")
                        break
            
            # 如果没找到关键词匹配的，使用第一个heading
            if not first_heading:
                first_heading = all_headings[0]
                h2_elem = first_heading.find('h2')
                h2_text = h2_elem.get_text() if h2_elem else '未知'
                self.logger.warning(f"    ⚠ 未找到生平关键词，使用第一个章节: {h2_text}")
            
            # 移动版使用 <section> 标签包裹内容，桌面版直接跟在heading后
            html_parts = []
            html_parts.append(str(first_heading))  # 包含标题本身
            
            # 检查是否是移动版（下一个元素是section标签）
            next_elem = first_heading.find_next_sibling()
            if next_elem and next_elem.name == 'section':
                # 移动版：提取section内的全部内容
                self.logger.debug(f"    ✓ 检测到移动版HTML结构（section标签）")
                html_parts.append(str(next_elem))
                element_count = 1
            else:
                # 桌面版：收集该heading之后、下一个heading2之前的所有内容
                self.logger.debug(f"    ✓ 检测到桌面版HTML结构")
                current_elem = next_elem
                element_count = 0
                
                while current_elem:
                    # 检查是否遇到下一个 mw-heading2
                    if current_elem.name == 'div':
                        classes = current_elem.get('class', [])
                        if 'mw-heading' in classes and 'mw-heading2' in classes:
                            self.logger.debug(f"    ✓ 遇到下一个heading2，停止采集")
                            break
                    
                    html_parts.append(str(current_elem))
                    element_count += 1
                    current_elem = current_elem.find_next_sibling()
            
            biography_html = '\n'.join(html_parts)
            self.logger.debug(f"    ✓ 生平章节提取完成: {element_count} 个元素, {len(biography_html)} 字符")
            
            return biography_html
        
        except Exception as e:
            self.logger.error(f"    ❌ 提取生平章节失败: {str(e)}")
            import traceback
            self.logger.debug(f"    错误堆栈: {traceback.format_exc()}")
            return ''

    def _create_emperor_entity(self, emperor_data: Dict, emperor_info: Dict) -> Emperor:
        """创建皇帝实体"""
        emperor_id = generate_id("ming_emperor", emperor_data['name'], emperor_info['dynasty_order'])
        
        # 解析在位时间
        reign_years = emperor_info.get('reign_years', '')
        reign_start, reign_end = self._parse_reign_years(reign_years)
        
        return Emperor(
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
            source_url=f"https://zh.wikipedia.org/wiki/{emperor_data['name']}",
            data_source='wikipedia'
        )
    
    def _parse_reign_years(self, reign_years_str: str) -> tuple:
        """解析在位年份"""
        try:
            years = reign_years_str.split(',')[0].strip()
            start_year, end_year = years.split('-')
            return (date(int(start_year), 1, 1), date(int(end_year), 12, 31))
        except Exception:
            return (date(1368, 1, 1), None)
    
    def parse_event(self, response):
        """解析事件页面"""
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            event_data = self._extract_event_data(soup, response.meta.get('emperor_id'))
            
            if event_data:
                self.logger.info(f"[Wiki] 成功爬取事件: {event_data.title}")
                yield event_data
        
        except Exception as e:
            self.logger.error(f"[Wiki] 解析事件页面失败: {str(e)}")
    
    def _extract_event_data(self, soup: BeautifulSoup, emperor_id: str) -> Optional[Event]:
        """从维基百科页面中提取事件数据"""
        try:
            # 获取标题
            title_elem = soup.find('h1', class_='firstHeading')
            if not title_elem:
                return None
            
            title = clean_text(title_elem.get_text())
            
            # 提取Infobox信息
            start_date = None
            location = None
            description = ''
            
            infobox = soup.find('table', class_='infobox')
            if infobox:
                # 提取时间
                time_row = infobox.find('th', text=re.compile('时间|日期'))
                if time_row and time_row.find_next_sibling('td'):
                    time_text = time_row.find_next_sibling('td').get_text(strip=True)
                    start_date = self.date_parser.parse_chinese_date(time_text)
                
                # 提取地点
                location_row = infobox.find('th', text=re.compile('地点|地區'))
                if location_row and location_row.find_next_sibling('td'):
                    location = clean_text(location_row.find_next_sibling('td').get_text())
            
            # 提取描述
            content = soup.find('div', class_='mw-parser-output')
            if content:
                first_para = content.find('p', recursive=False)
                if first_para:
                    for sup in first_para.find_all('sup'):
                        sup.decompose()
                    description = clean_text(first_para.get_text())
            
            # 创建Event实体
            event_id = generate_id("ming_event", title)
            
            event = Event(
                event_id=event_id,
                dynasty_id=MING_DYNASTY['dynasty_id'],
                emperor_id=emperor_id,
                title=title,
                event_type=self._determine_event_type(title),
                start_date=start_date or date(1368, 1, 1),
                location=location,
                description=description,
                data_source='wikipedia'
            )
            
            return event
        
        except Exception as e:
            self.logger.warning(f"[Wiki] 提取事件数据时出错: {str(e)}")
            return None
    
    def _determine_event_type(self, title: str) -> EventType:
        """根据标题判断事件类型"""
        if any(keyword in title for keyword in ['之战', '之役', '战争', '战役']):
            return EventType.MILITARY
        elif any(keyword in title for keyword in ['政变', '改革', '废除', '设立']):
            return EventType.POLITICAL
        elif any(keyword in title for keyword in ['文化', '运动', '著作']):
            return EventType.CULTURAL
        elif any(keyword in title for keyword in ['贸易', '下西洋', '通商']):
            return EventType.DIPLOMATIC
        else:
            return EventType.POLITICAL
    
    def parse_person(self, response):
        """解析人物页面"""
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            person_data = self._extract_person_data(soup, response.meta.get('emperor_id'))
            
            if person_data:
                self.logger.info(f"[Wiki] 成功爬取人物: {person_data.name}")
                yield person_data
        
        except Exception as e:
            self.logger.error(f"[Wiki] 解析人物页面失败: {str(e)}")
    
    def _extract_person_data(self, soup: BeautifulSoup, emperor_id: str) -> Optional[Person]:
        """从维基百科页面中提取人物数据"""
        try:
            # 获取人名
            title_elem = soup.find('h1', class_='firstHeading')
            if not title_elem:
                return None
            
            name = clean_text(title_elem.get_text())
            
            # 提取信息
            alias_list = []
            birth_date = None
            death_date = None
            position = None
            person_type = PersonType.OTHER
            biography = ''
            infobox_data = {}  # 存储infobox中的所有信息
            biography_html = ''  # 存储生平HTML内容
            
            infobox = soup.find('table', class_='infobox')
            if infobox:
                # 提取infobox中的所有段落
                infobox_paragraphs = infobox.find_all('p')
                for p in infobox_paragraphs:
                    p_text = clean_text(p.get_text())
                    if p_text:
                        infobox_data.setdefault('paragraphs', []).append(p_text)
                
                # 提取别名
                alias_row = infobox.find('th', text=re.compile('字|號|別名'))
                if alias_row and alias_row.find_next_sibling('td'):
                    alias_text = alias_row.find_next_sibling('td').get_text(strip=True)
                    alias_list = [a.strip() for a in re.split('[，、\n]', alias_text) if a.strip()]
                    infobox_data['alias'] = alias_text
                
                # 提取出生日期
                birth_row = infobox.find('th', text=re.compile('出生'))
                if birth_row and birth_row.find_next_sibling('td'):
                    birth_text = birth_row.find_next_sibling('td').get_text(strip=True)
                    birth_date = self.date_parser.parse_chinese_date(birth_text)
                    infobox_data['birth'] = birth_text
                
                # 提取去世日期
                death_row = infobox.find('th', text=re.compile('逝世'))
                if death_row and death_row.find_next_sibling('td'):
                    death_text = death_row.find_next_sibling('td').get_text(strip=True)
                    death_date = self.date_parser.parse_chinese_date(death_text)
                    infobox_data['death'] = death_text
                
                # 提取职位
                position_row = infobox.find('th', text=re.compile('職業|官職'))
                if position_row and position_row.find_next_sibling('td'):
                    position = clean_text(position_row.find_next_sibling('td').get_text())
                    person_type = self._determine_person_type(position)
                    infobox_data['position'] = position
            
            # 提取生平
            content = soup.find('div', class_='mw-parser-output')
            if content:
                first_para = content.find('p', recursive=False)
                if first_para:
                    for sup in first_para.find_all('sup'):
                        sup.decompose()
                    biography = clean_text(first_para.get_text())
                
                # 提取生平HTML内容
                biography_html = self._extract_biography_section(soup)
            
            # 创建Person实体
            person_id = generate_id("ming_person", name)
            
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
                html_content=biography_html,
                source_url=f"https://zh.wikipedia.org/wiki/{name}",
                data_source='wikipedia'
            )
            
            return person
        
        except Exception as e:
            self.logger.warning(f"[Wiki] 提取人物数据时出错: {str(e)}")
            return None
    
    def _determine_person_type(self, position: str) -> PersonType:
        """根据职位判断人物类型"""
        if not position:
            return PersonType.OTHER
        
        if any(keyword in position for keyword in ['將軍', '將领', '武', '军']):
            return PersonType.GENERAL
        elif any(keyword in position for keyword in ['詩人', '文学', '作家', '詞人']):
            return PersonType.WRITER
        elif any(keyword in position for keyword in ['畫家', '書法', '藝術']):
            return PersonType.ARTIST
        elif any(keyword in position for keyword in ['大臣', '尚書', '侍郎', '學士', '閣']):
            return PersonType.OFFICIAL
        elif any(keyword in position for keyword in ['皇子', '皇后', '妃']):
            return PersonType.ROYAL
        elif any(keyword in position for keyword in ['僧', '道']):
            return PersonType.MONK
        elif any(keyword in position for keyword in ['思想', '哲學']):
            return PersonType.THINKER
        elif any(keyword in position for keyword in ['科學', '天文', '數學', '醫']):
            return PersonType.SCIENTIST
        else:
            return PersonType.OTHER
