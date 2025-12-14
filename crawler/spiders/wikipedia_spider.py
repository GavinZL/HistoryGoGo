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
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 4,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_parser = DateParser()
        
        # 获取爬取模式配置
        self.crawl_mode = self.settings.get('CRAWL_MODE', 'test')
        self.test_emperor_count = self.settings.get('TEST_EMPEROR_COUNT', 3)
    
    def start_requests(self):
        """生成起始请求"""
        # 根据爬取模式决定爬取多少位皇帝
        emperors_to_crawl = MING_EMPERORS
        if self.crawl_mode == 'test':
            emperors_to_crawl = MING_EMPERORS[:self.test_emperor_count]
            self.logger.info(f"[Wiki] 测试模式：只爬取前{self.test_emperor_count}位皇帝")
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
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取皇帝信息
            emperor_data = self._extract_emperor_data(soup, emperor_info)
            
            if emperor_data:
                self.logger.info(f"[Wiki] 成功爬取皇帝: {emperor_data['name']}")
                
                # 创建Emperor实体
                emperor = self._create_emperor_entity(emperor_data, emperor_info)
                yield emperor
                
        except Exception as e:
            self.logger.error(f"[Wiki] 解析皇帝页面失败: {emperor_info['name']}, 错误: {str(e)}")
    
    def _extract_emperor_data(self, soup: BeautifulSoup, emperor_info: Dict) -> Optional[Dict[str, Any]]:
        """从维基百科页面中提取皇帝数据"""
        data = {
            'name': emperor_info['name'],
            'temple_name': emperor_info.get('temple_name'),
            'reign_title': emperor_info.get('reign_title'),
            'biography': '',
            'achievements': '',
            'portrait_url': None
        }
        
        try:
            # 提取Infobox信息框
            infobox = soup.find('table', class_='infobox')
            if infobox:
                # 提取出生日期
                birth_row = infobox.find('th', text=re.compile('出生|誕生'))
                if birth_row and birth_row.find_next_sibling('td'):
                    birth_text = birth_row.find_next_sibling('td').get_text(strip=True)
                    data['birth_date'] = self.date_parser.parse_chinese_date(birth_text)
                
                # 提取去世日期
                death_row = infobox.find('th', text=re.compile('逝世'))
                if death_row and death_row.find_next_sibling('td'):
                    death_text = death_row.find_next_sibling('td').get_text(strip=True)
                    data['death_date'] = self.date_parser.parse_chinese_date(death_text)
                
                # 提取画像
                portrait = infobox.find('img')
                if portrait and portrait.get('src'):
                    # 维基百科图片URL需要加上https:前缀
                    img_url = portrait['src']
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    data['portrait_url'] = img_url
            
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
            
            # 尝试提取"主要成就"相关内容
            # 在维基百科中可能在不同的章节
            for heading in soup.find_all(['h2', 'h3']):
                heading_text = heading.get_text()
                if any(keyword in heading_text for keyword in ['成就', '贡献', '政绩']):
                    next_elem = heading.find_next_sibling()
                    if next_elem and next_elem.name in ['p', 'ul']:
                        data['achievements'] = clean_text(next_elem.get_text())
                        break
        
        except Exception as e:
            self.logger.warning(f"[Wiki] 提取皇帝详细信息时出错: {str(e)}")
        
        return data
    
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
            
            infobox = soup.find('table', class_='infobox')
            if infobox:
                # 提取别名
                alias_row = infobox.find('th', text=re.compile('字|號|別名'))
                if alias_row and alias_row.find_next_sibling('td'):
                    alias_text = alias_row.find_next_sibling('td').get_text(strip=True)
                    alias_list = [a.strip() for a in re.split('[，、\n]', alias_text) if a.strip()]
                
                # 提取出生日期
                birth_row = infobox.find('th', text=re.compile('出生'))
                if birth_row and birth_row.find_next_sibling('td'):
                    birth_text = birth_row.find_next_sibling('td').get_text(strip=True)
                    birth_date = self.date_parser.parse_chinese_date(birth_text)
                
                # 提取去世日期
                death_row = infobox.find('th', text=re.compile('逝世'))
                if death_row and death_row.find_next_sibling('td'):
                    death_text = death_row.find_next_sibling('td').get_text(strip=True)
                    death_date = self.date_parser.parse_chinese_date(death_text)
                
                # 提取职位
                position_row = infobox.find('th', text=re.compile('職業|官職'))
                if position_row and position_row.find_next_sibling('td'):
                    position = clean_text(position_row.find_next_sibling('td').get_text())
                    person_type = self._determine_person_type(position)
            
            # 提取生平
            content = soup.find('div', class_='mw-parser-output')
            if content:
                first_para = content.find('p', recursive=False)
                if first_para:
                    for sup in first_para.find_all('sup'):
                        sup.decompose()
                    biography = clean_text(first_para.get_text())
            
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
