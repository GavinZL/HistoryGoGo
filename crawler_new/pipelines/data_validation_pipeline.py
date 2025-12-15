"""
数据验证 Pipeline
验证千问提取的数据是否符合要求
"""

from crawler_new.models.items import ExtractedDataItem


class DataValidationPipeline:
    """数据验证Pipeline"""
    
    def process_item(self, item, spider):
        """处理 Item"""
        # 只处理 ExtractedDataItem
        if not isinstance(item, ExtractedDataItem):
            return item
        
        try:
            data_type = item['data_type']
            extracted_data = item['extracted_data']
            
            if data_type == 'emperor':
                self._validate_emperor_data(extracted_data, spider)
            elif data_type == 'event':
                self._validate_event_data(extracted_data, spider)
            elif data_type == 'person':
                self._validate_person_data(extracted_data, spider)
            
            spider.logger.info(f"✅ 数据验证通过: {item['html_item']['page_id']}")
            
        except Exception as e:
            spider.logger.warning(f"⚠️  数据验证失败: {item['html_item']['page_id']}, 错误: {str(e)}")
        
        return item
    
    def _validate_emperor_data(self, extracted_data: dict, spider):
        """验证皇帝数据"""
        emperor_info = extracted_data.get('emperor_info', {})
        
        # 检查必填字段
        required_fields = ['皇帝']
        for field in required_fields:
            if not emperor_info.get(field):
                raise ValueError(f"缺少必填字段: {field}")
        
        # 检查事迹数据
        events = extracted_data.get('events', [])
        spider.logger.debug(f"   皇帝: {emperor_info.get('皇帝')}, 事迹数: {len(events)}")
    
    def _validate_event_data(self, extracted_data: dict, spider):
        """验证事件数据（待实现）"""
        pass
    
    def _validate_person_data(self, extracted_data: dict, spider):
        """验证人物数据（待实现）"""
        pass
