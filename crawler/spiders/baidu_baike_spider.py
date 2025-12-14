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
    
    def __init__(self, crawl_mode='test', test_emperor_count=3, *args, **kwargs):
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
        """从页面中提取皇帝数据"""
        data = {
            'name': emperor_info['name'],
            'temple_name': emperor_info.get('temple_name'),
            'reign_title': emperor_info.get('reign_title'),
            'biography': '',
            'achievements': '',
            'portrait_url': None
        }
        
        try:
            # 提取基础信息框
            info_box = soup.select_one('.basic-info')
            if info_box:
                # 提取出生日期
                birth_elem = info_box.find('dt', text=re.compile('出生日期|出生时间'))
                if birth_elem and birth_elem.find_next_sibling('dd'):
                    birth_text = birth_elem.find_next_sibling('dd').get_text(strip=True)
                    data['birth_date'] = self.date_parser.parse_chinese_date(birth_text)
                
                # 提取去世日期
                death_elem = info_box.find('dt', text=re.compile('逝世日期|逝世时间'))
                if death_elem and death_elem.find_next_sibling('dd'):
                    death_text = death_elem.find_next_sibling('dd').get_text(strip=True)
                    data['death_date'] = self.date_parser.parse_chinese_date(death_text)
            
            # 提取简介（第一段）
            summary = soup.select_one('.lemma-summary')
            if summary:
                paragraphs = summary.find_all('div', class_='para')
                if paragraphs:
                    data['biography'] = clean_text(paragraphs[0].get_text())
            
            # 提取主要成就
            achievement_section = soup.find('div', {'data-title': '主要成就'})
            if achievement_section:
                data['achievements'] = clean_text(achievement_section.get_text())
            
            # 提取画像URL
            portrait = soup.select_one('.summary-pic img')
            if portrait and portrait.get('src'):
                data['portrait_url'] = portrait['src']
        
        except Exception as e:
            self.logger.warning(f"提取皇帝详细信息时出错: {str(e)}")
        
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
            data_source='baidu'
        )
    
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
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取事件数据
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
    
    def _extract_event_data(self, soup: BeautifulSoup, emperor_id: str) -> Optional[Dict]:
        """从页面中提取事件数据"""
        try:
            # 获取标题
            title_elem = soup.select_one('.lemmaWgt-lemmaTitle-title h1')
            if not title_elem:
                return None
            
            title = clean_text(title_elem.get_text())
            
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
            
            # 提取基础信息框
            info_box = soup.select_one('.basic-info')
            if info_box:
                # 提取时间
                time_elem = info_box.find('dt', text=re.compile('时间|发生时间|年代'))
                if time_elem and time_elem.find_next_sibling('dd'):
                    time_text = time_elem.find_next_sibling('dd').get_text(strip=True)
                    data['start_date'] = self.date_parser.parse_chinese_date(time_text)
                
                # 提取地点
                location_elem = info_box.find('dt', text=re.compile('地点|发生地点'))
                if location_elem and location_elem.find_next_sibling('dd'):
                    data['location'] = clean_text(location_elem.find_next_sibling('dd').get_text())
            
            # 提取描述
            summary = soup.select_one('.lemma-summary')
            if summary:
                paragraphs = summary.find_all('div', class_='para')
                if paragraphs:
                    data['description'] = clean_text(paragraphs[0].get_text())
            
            # 创建Event实体
            event_id = generate_id("ming_event", title)
            
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
                data_source='baidu'
            )
            
            return event
        
        except Exception as e:
            self.logger.warning(f"提取事件数据时出错: {str(e)}")
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
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取人物数据
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
    
    def _extract_person_data(self, soup: BeautifulSoup, emperor_id: str) -> Optional[Person]:
        """从页面中提取人物数据"""
        try:
            # 获取人名
            title_elem = soup.select_one('.lemmaWgt-lemmaTitle-title h1')
            if not title_elem:
                return None
            
            name = clean_text(title_elem.get_text())
            
            # 提取基础信息
            alias_list = []
            birth_date = None
            death_date = None
            position = None
            person_type = PersonType.OTHER
            
            info_box = soup.select_one('.basic-info')
            if info_box:
                # 提取别名、字号
                alias_elem = info_box.find('dt', text=re.compile('别名|字号|本名'))
                if alias_elem and alias_elem.find_next_sibling('dd'):
                    alias_text = alias_elem.find_next_sibling('dd').get_text(strip=True)
                    alias_list = [a.strip() for a in re.split('[，、]', alias_text) if a.strip()]
                
                # 提取出生日期
                birth_elem = info_box.find('dt', text=re.compile('出生日期|出生时间'))
                if birth_elem and birth_elem.find_next_sibling('dd'):
                    birth_text = birth_elem.find_next_sibling('dd').get_text(strip=True)
                    birth_date = self.date_parser.parse_chinese_date(birth_text)
                
                # 提取去世日期
                death_elem = info_box.find('dt', text=re.compile('逝世日期|逝世时间'))
                if death_elem and death_elem.find_next_sibling('dd'):
                    death_text = death_elem.find_next_sibling('dd').get_text(strip=True)
                    death_date = self.date_parser.parse_chinese_date(death_text)
                
                # 提取职位
                position_elem = info_box.find('dt', text=re.compile('职业|主要成就|职务'))
                if position_elem and position_elem.find_next_sibling('dd'):
                    position = clean_text(position_elem.find_next_sibling('dd').get_text())
                    # 根据职位判断人物类型
                    person_type = self._determine_person_type(position, soup)
            
            # 提取生平
            biography = ''
            summary = soup.select_one('.lemma-summary')
            if summary:
                paragraphs = summary.find_all('div', class_='para')
                if paragraphs:
                    biography = clean_text(paragraphs[0].get_text())
            
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
                data_source='baidu'
            )
            
            return person
        
        except Exception as e:
            self.logger.warning(f"提取人物数据时出错: {str(e)}")
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
