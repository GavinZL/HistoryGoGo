"""
数据验证管道
验证数据的完整性、准确性和逻辑性
"""

from typing import Any
from datetime import date
from crawler.models.entities import Emperor, Event, Person


class DataValidationPipeline:
    """数据验证管道"""
    
    # 明朝时间范围
    MING_START_YEAR = 1368
    MING_END_YEAR = 1644
    
    def __init__(self):
        self.stats = {
            'validated': 0,
            'passed': 0,
            'warnings': 0,
            'errors': 0,
            'dropped': 0
        }
        self.validation_issues = []
    
    def open_spider(self, spider):
        """爬虫启动时调用"""
        spider.logger.info("✅ 数据验证管道已启动")
    
    def process_item(self, item: Any, spider):
        """验证数据项"""
        self.stats['validated'] += 1
        
        try:
            if isinstance(item, Emperor):
                is_valid, issues = self._validate_emperor(item)
            elif isinstance(item, Event):
                is_valid, issues = self._validate_event(item)
            elif isinstance(item, Person):
                is_valid, issues = self._validate_person(item)
            else:
                spider.logger.warning(f"未知的数据类型: {type(item)}")
                return item
            
            # 记录验证问题
            if issues:
                for issue in issues:
                    self.validation_issues.append({
                        'type': type(item).__name__,
                        'id': getattr(item, f"{type(item).__name__.lower()}_id", 'unknown'),
                        'issue': issue
                    })
                    if issue['severity'] == 'error':
                        self.stats['errors'] += 1
                    else:
                        self.stats['warnings'] += 1
                    
                    spider.logger.log(
                        40 if issue['severity'] == 'error' else 30,
                        f"[验证{issue['severity']}] {issue['field']}: {issue['message']}"
                    )
            
            # 如果有严重错误，丢弃数据
            if not is_valid:
                self.stats['dropped'] += 1
                item_name = getattr(item, 'name', None) or getattr(item, 'title', 'unknown')
                spider.logger.error(f"❌ 数据验证失败，丢弃数据: {type(item).__name__} - {item_name}")
                return None
            
            self.stats['passed'] += 1
            return item
        
        except Exception as e:
            self.stats['errors'] += 1
            spider.logger.error(f"数据验证异常: {str(e)}")
            return item
    
    def _validate_emperor(self, emperor: Emperor) -> tuple[bool, list]:
        """验证皇帝数据"""
        issues = []
        
        # 必填字段检查
        if not emperor.emperor_id:
            issues.append({'field': 'emperor_id', 'message': 'ID不能为空', 'severity': 'error'})
        
        if not emperor.name:
            issues.append({'field': 'name', 'message': '姓名不能为空', 'severity': 'error'})
        
        if not emperor.reign_start:
            issues.append({'field': 'reign_start', 'message': '在位开始时间不能为空', 'severity': 'error'})
        
        if emperor.dynasty_order is None or emperor.dynasty_order < 1:
            issues.append({'field': 'dynasty_order', 'message': '朝代顺序无效', 'severity': 'error'})
        
        # 时间逻辑验证
        if emperor.birth_date and emperor.death_date:
            if emperor.birth_date >= emperor.death_date:
                issues.append({
                    'field': 'birth_date/death_date',
                    'message': f'出生日期({emperor.birth_date})应早于去世日期({emperor.death_date})',
                    'severity': 'error'
                })
        
        if emperor.birth_date and emperor.reign_start:
            age_at_reign = (emperor.reign_start - emperor.birth_date).days // 365
            if age_at_reign < 0:
                issues.append({
                    'field': 'birth_date/reign_start',
                    'message': f'出生日期({emperor.birth_date})应早于登基日期({emperor.reign_start})',
                    'severity': 'error'
                })
            elif age_at_reign < 5:
                issues.append({
                    'field': 'birth_date/reign_start',
                    'message': f'登基年龄({age_at_reign}岁)过小，可能有误',
                    'severity': 'warning'
                })
            elif age_at_reign > 100:
                issues.append({
                    'field': 'birth_date/reign_start',
                    'message': f'登基年龄({age_at_reign}岁)过大，可能有误',
                    'severity': 'warning'
                })
        
        if emperor.reign_start and emperor.reign_end:
            if emperor.reign_start > emperor.reign_end:
                issues.append({
                    'field': 'reign_start/reign_end',
                    'message': f'在位开始({emperor.reign_start})应早于在位结束({emperor.reign_end})',
                    'severity': 'error'
                })
        
        # 日期范围验证（明朝时间范围）
        if emperor.reign_start:
            if emperor.reign_start.year < self.MING_START_YEAR or emperor.reign_start.year > self.MING_END_YEAR:
                issues.append({
                    'field': 'reign_start',
                    'message': f'在位开始年份({emperor.reign_start.year})超出明朝范围({self.MING_START_YEAR}-{self.MING_END_YEAR})',
                    'severity': 'warning'
                })
        
        # 数据完整性检查
        if not emperor.biography:
            issues.append({'field': 'biography', 'message': '缺少生平简介', 'severity': 'warning'})
        
        if not emperor.temple_name and not emperor.reign_title:
            issues.append({'field': 'temple_name/reign_title', 'message': '庙号和年号都缺失', 'severity': 'warning'})
        
        # 判断是否有严重错误
        has_errors = any(issue['severity'] == 'error' for issue in issues)
        
        return (not has_errors, issues)
    
    def _validate_event(self, event: Event) -> tuple[bool, list]:
        """验证事件数据"""
        issues = []
        
        # 必填字段检查
        if not event.event_id:
            issues.append({'field': 'event_id', 'message': 'ID不能为空', 'severity': 'error'})
        
        if not event.title:
            issues.append({'field': 'title', 'message': '标题不能为空', 'severity': 'error'})
        
        if not event.start_date:
            issues.append({'field': 'start_date', 'message': '开始日期不能为空', 'severity': 'error'})
        
        # 时间逻辑验证
        if event.start_date and event.end_date:
            if event.start_date > event.end_date:
                issues.append({
                    'field': 'start_date/end_date',
                    'message': f'开始日期({event.start_date})应早于或等于结束日期({event.end_date})',
                    'severity': 'error'
                })
        
        # 日期范围验证
        if event.start_date:
            if event.start_date.year < self.MING_START_YEAR or event.start_date.year > self.MING_END_YEAR + 10:
                issues.append({
                    'field': 'start_date',
                    'message': f'事件年份({event.start_date.year})可能超出明朝范围',
                    'severity': 'warning'
                })
        
        # 数据完整性检查
        if not event.description:
            issues.append({'field': 'description', 'message': '缺少事件描述', 'severity': 'warning'})
        
        if not event.emperor_id:
            issues.append({'field': 'emperor_id', 'message': '缺少关联皇帝', 'severity': 'warning'})
        
        # 判断是否有严重错误
        has_errors = any(issue['severity'] == 'error' for issue in issues)
        
        return (not has_errors, issues)
    
    def _validate_person(self, person: Person) -> tuple[bool, list]:
        """验证人物数据"""
        issues = []
        
        # 必填字段检查
        if not person.person_id:
            issues.append({'field': 'person_id', 'message': 'ID不能为空', 'severity': 'error'})
        
        if not person.name:
            issues.append({'field': 'name', 'message': '姓名不能为空', 'severity': 'error'})
        
        # 时间逻辑验证
        if person.birth_date and person.death_date:
            if person.birth_date >= person.death_date:
                issues.append({
                    'field': 'birth_date/death_date',
                    'message': f'出生日期({person.birth_date})应早于去世日期({person.death_date})',
                    'severity': 'error'
                })
            
            lifespan = (person.death_date - person.birth_date).days // 365
            if lifespan > 120:
                issues.append({
                    'field': 'birth_date/death_date',
                    'message': f'寿命({lifespan}岁)过长，可能有误',
                    'severity': 'warning'
                })
        
        # 日期范围验证
        if person.birth_date:
            if person.birth_date.year < self.MING_START_YEAR - 100 or person.birth_date.year > self.MING_END_YEAR + 50:
                issues.append({
                    'field': 'birth_date',
                    'message': f'出生年份({person.birth_date.year})可能超出合理范围',
                    'severity': 'warning'
                })
        
        # 数据完整性检查
        if not person.biography:
            issues.append({'field': 'biography', 'message': '缺少生平简介', 'severity': 'warning'})
        
        if not person.position:
            issues.append({'field': 'position', 'message': '缺少职位信息', 'severity': 'warning'})
        
        # 判断是否有严重错误
        has_errors = any(issue['severity'] == 'error' for issue in issues)
        
        return (not has_errors, issues)
    
    def close_spider(self, spider):
        """爬虫关闭时输出统计信息"""
        spider.logger.info("\n" + "="*80)
        spider.logger.info("✅ 数据验证统计")
        spider.logger.info("="*80)
        spider.logger.info(
            f"验证={self.stats['validated']}, "
            f"通过={self.stats['passed']}, 警告={self.stats['warnings']}, "
            f"错误={self.stats['errors']}, 丢弃={self.stats['dropped']}"
        )
        
        # 计算通过率
        if self.stats['validated'] > 0:
            pass_rate = (self.stats['passed'] / self.stats['validated']) * 100
            spider.logger.info(f"验证通过率: {pass_rate:.2f}%")
        
        # 输出验证问题汇总
        if self.validation_issues:
            spider.logger.info(f"\n共发现 {len(self.validation_issues)} 个验证问题")
            
            # 按严重程度分组
            error_issues = [i for i in self.validation_issues if i['issue']['severity'] == 'error']
            warning_issues = [i for i in self.validation_issues if i['issue']['severity'] == 'warning']
            
            if error_issues:
                spider.logger.error(f"\n严重错误 ({len(error_issues)}个):")
                for issue in error_issues[:10]:  # 只显示前10个
                    spider.logger.error(f"  - {issue['type']} {issue['id']}: {issue['issue']['message']}")
                if len(error_issues) > 10:
                    spider.logger.error(f"  ... 还有 {len(error_issues) - 10} 个错误未显示")
            
            if warning_issues:
                spider.logger.warning(f"\n警告 ({len(warning_issues)}个):")
                for issue in warning_issues[:10]:  # 只显示前10个
                    spider.logger.warning(f"  - {issue['type']} {issue['id']}: {issue['issue']['message']}")
                if len(warning_issues) > 10:
                    spider.logger.warning(f"  ... 还有 {len(warning_issues) - 10} 个警告未显示")
        else:
            spider.logger.info("✅ 所有数据验证均通过！")
        
        spider.logger.info("="*80 + "\n")
