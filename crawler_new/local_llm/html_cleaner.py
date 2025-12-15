"""
HTML 清理处理模块
专门负责从Wikipedia HTML中提取结构化内容
保留目录结构和人物/事件链接
"""
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass


@dataclass
class CleanedContent:
    """清理后的内容结构"""
    text: str  # 清理后的纯文本
    toc: List[Dict[str, str]]  # 目录结构
    links: List[Dict[str, str]]  # 人物/事件链接


class WikipediaHTMLCleaner:
    """Wikipedia HTML 清理器"""
    
    # 需要截断的章节ID列表
    STOP_SECTION_IDS = [
        '评价', '評價', '家族成员', '家族成員', '轶事典故', 
        '相关争议', '影视作品', '文学作品', '注释', '参考文献', '外部链接'
    ]
    
    # 需要移除的页面元素class
    UNWANTED_CLASSES = [
        'ambox', 'mbox-small', 'navbox', 'vertical-navbox', 
        'sistersitebox', 'metadata', 'topicon', 'noprint'
    ]
    
    def clean(self, html_content: str) -> CleanedContent:
        """
        清理HTML内容，提取文本、目录和链接
        
        Args:
            html_content: 原始HTML内容
            
        Returns:
            CleanedContent: 包含文本、目录和链接的清理结果
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 1. 移除无关标签
        self._remove_unwanted_tags(soup)
        
        # 2. 获取主要内容区域
        main_content = soup.find('div', class_='mw-parser-output')
        if not main_content:
            return CleanedContent(
                text=soup.get_text(separator=' ', strip=True),
                toc=[],
                links=[]
            )
        
        # 3. 提取目录结构（在删除之前）
        toc = self._extract_toc(main_content)
        
        # 4. 提取人物/事件链接（在清理之前）
        links = self._extract_links(main_content)
        
        # 5. 移除页面提示框等无关内容
        self._remove_unwanted_elements(main_content)
        
        # 6. 移除参考引用标记（sup标签）
        self._remove_references(main_content)
        
        # 7. 截断到指定章节
        self._truncate_at_stop_section(main_content)
        
        # 8. 提取并清理文本
        text = self._extract_clean_text(main_content)
        
        return CleanedContent(
            text=text,
            toc=toc,
            links=links
        )
    
    def _remove_unwanted_tags(self, soup: BeautifulSoup):
        """移除脚本、样式等无关标签"""
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
    
    def _extract_toc(self, main_content: Tag) -> List[Dict[str, str]]:
        """
        提取目录结构
        
        Returns:
            目录列表，每项包含: level, id, title
        """
        toc = []
        
        # 查找所有标题标签
        for heading in main_content.find_all(['h2', 'h3', 'h4']):
            heading_span = heading.find('span', class_='mw-headline')
            if heading_span:
                section_id = heading_span.get('id', '')
                section_title = heading_span.get_text(strip=True)
                
                # 确定层级
                level = int(heading.name[1])  # h2->2, h3->3, h4->4
                
                toc.append({
                    'level': level,
                    'id': section_id,
                    'title': section_title
                })
        
        return toc
    
    def _extract_links(self, main_content: Tag) -> List[Dict[str, str]]:
        """
        提取人物/事件链接
        
        Returns:
            链接列表，每项包含: text, href, type
        """
        links = []
        
        # 查找所有链接
        for link in main_content.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 只保留Wikipedia内部链接（/wiki/开头）
            if href.startswith('/wiki/') and text:
                # 判断链接类型
                link_type = self._classify_link(href, text)
                
                # 过滤掉一些无关链接
                if link_type != 'ignore':
                    links.append({
                        'text': text,
                        'href': href,
                        'type': link_type,
                        'full_url': f'https://zh.wikipedia.org{href}'
                    })
        
        return links
    
    def _classify_link(self, href: str, text: str) -> str:
        """
        分类链接类型
        
        Returns:
            'person' - 人物
            'event' - 事件
            'place' - 地点
            'dynasty' - 朝代/年号
            'other' - 其他
            'ignore' - 忽略
        """
        # 忽略的链接模式
        ignore_patterns = [
            'Wikipedia:', 'Help:', 'Special:', 'Category:', 
            'Template:', 'Portal:', 'File:', 'Image:'
        ]
        for pattern in ignore_patterns:
            if pattern in href:
                return 'ignore'
        
        # 简单的分类逻辑（可以后续优化）
        # 人物：通常是人名
        if any(char in text for char in ['帝', '王', '公', '侯', '将', '相', '氏']):
            return 'person'
        
        # 事件：包含特定关键词
        if any(keyword in text for keyword in ['之战', '之役', '起义', '变法', '改革', '运动']):
            return 'event'
        
        # 地点：包含地名关键词
        if any(keyword in text for keyword in ['省', '府', '州', '县', '京', '都']):
            return 'place'
        
        # 朝代/年号
        if any(keyword in text for keyword in ['朝', '年', '元年', '世']):
            return 'dynasty'
        
        return 'other'
    
    def _remove_unwanted_elements(self, main_content: Tag):
        """移除页面提示框等无关内容（保留目录div）"""
        for unwanted_class in self.UNWANTED_CLASSES:
            for element in main_content.find_all(class_=lambda x: x and unwanted_class in x):
                element.decompose()
    
    def _remove_references(self, main_content: Tag):
        """移除参考引用标记（sup标签）"""
        for sup_tag in main_content.find_all('sup'):
            sup_tag.decompose()
    
    def _truncate_at_stop_section(self, main_content: Tag):
        """在指定章节处截断内容"""
        end_marker = None
        
        for heading in main_content.find_all(['h2', 'h3']):
            heading_span = heading.find('span', class_='mw-headline')
            if heading_span:
                heading_id = heading_span.get('id', '')
                if heading_id in self.STOP_SECTION_IDS:
                    end_marker = heading
                    break
        
        if end_marker:
            # 移除该标记及其后的所有内容
            section_to_remove = end_marker.find_parent('section')
            if section_to_remove and section_to_remove != main_content:
                section_to_remove.decompose()
            else:
                # 移除该heading及其后续所有兄弟节点
                for sibling in list(end_marker.find_next_siblings()):
                    sibling.decompose()
                end_marker.decompose()
    
    def _extract_clean_text(self, main_content: Tag) -> str:
        """提取并清理文本"""
        # 使用空格作为分隔符提取文本
        text = main_content.get_text(separator=' ', strip=True)
        
        # 清理多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除残留的引用标记
        text = re.sub(r'\[\d+\]', '', text)
        
        # 移除残留的编辑标记
        text = re.sub(r'\[编辑\]', '', text)
        text = re.sub(r'\[編輯\]', '', text)
        
        return text.strip()


class HTMLCleanerFactory:
    """HTML清理器工厂"""
    
    @staticmethod
    def create_cleaner(data_source: str = 'wikipedia') -> WikipediaHTMLCleaner:
        """
        创建HTML清理器
        
        Args:
            data_source: 数据源类型，目前仅支持'wikipedia'
            
        Returns:
            对应的清理器实例
        """
        if data_source.lower() == 'wikipedia':
            return WikipediaHTMLCleaner()
        else:
            raise ValueError(f"不支持的数据源: {data_source}")
