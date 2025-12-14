# HistoryGogo API 使用说明

## API服务启动

```bash
cd /Users/master/Documents/AI-Project/HistoryGogo/server
source venv/bin/activate
python main.py
```

服务将在 `http://localhost:8000` 启动

## API文档

启动服务后，可以访问以下地址查看自动生成的API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API端点概览

### 1. 朝代API (`/api/v1/dynasties`)

- **GET /api/v1/dynasties** - 获取朝代列表
  - 参数：`skip` (跳过数量), `limit` (限制数量)
  
- **GET /api/v1/dynasties/{dynasty_id}** - 获取朝代详情
  - 示例：`/api/v1/dynasties/ming`

### 2. 皇帝API (`/api/v1/emperors`)

- **GET /api/v1/emperors** - 获取皇帝列表
  - 参数：
    - `dynasty_id` (按朝代筛选)
    - `skip` (跳过数量)
    - `limit` (限制数量)
  - 示例：`/api/v1/emperors?dynasty_id=ming&limit=10`

- **GET /api/v1/emperors/{emperor_id}** - 获取皇帝详情
  - 示例：`/api/v1/emperors/ming_taizu`

### 3. 事件API (`/api/v1/events`)

- **GET /api/v1/events** - 获取事件列表
  - 参数：
    - `dynasty_id` (按朝代筛选)
    - `emperor_id` (按皇帝筛选)
    - `event_type` (按事件类型筛选)
    - `skip` (跳过数量)
    - `limit` (限制数量)
  - 示例：`/api/v1/events?dynasty_id=ming&event_type=战争&limit=20`

- **GET /api/v1/events/{event_id}** - 获取事件详情
  - 返回完整的事件信息，包括相关人物、伤亡情况、历史意义等

### 4. 人物API (`/api/v1/persons`)

- **GET /api/v1/persons** - 获取人物列表
  - 参数：
    - `person_type` (按人物类型筛选：文臣、武将、诗人等)
    - `dynasty_id` (按朝代筛选)
    - `skip` (跳过数量)
    - `limit` (限制数量)
  - 示例：`/api/v1/persons?person_type=文臣&dynasty_id=ming&limit=20`

- **GET /api/v1/persons/{person_id}** - 获取人物详情
  - 返回完整的人物信息，包括作品列表、参与事件、相关皇帝等

### 5. 时间轴API (`/api/v1/timeline`)

- **GET /api/v1/timeline/{dynasty_id}** - 获取指定朝代的时间轴
  - 示例：`/api/v1/timeline/ming`
  - 返回按年份组织的历史事件和在位皇帝信息

### 6. 搜索API (`/api/v1/search`)

- **GET /api/v1/search** - 全局搜索
  - 参数：
    - `q` (必填) - 搜索关键词
    - `search_type` - 搜索类型：emperor/event/person/all
    - `dynasty_id` - 限定朝代
    - `limit` - 每个类型的结果数量限制
  - 示例：`/api/v1/search?q=朱元璋&search_type=all`
  - 返回：匹配的皇帝、事件、人物列表

- **GET /api/v1/search/suggest** - 搜索建议
  - 参数：
    - `q` (必填) - 搜索关键词前缀
    - `limit` - 建议数量（默认5）
  - 示例：`/api/v1/search/suggest?q=朱`
  - 返回：搜索建议列表

### 7. 统计API (`/api/v1/statistics`)

- **GET /api/v1/statistics/overview** - 获取整体统计数据
  - 返回：朝代、皇帝、事件、人物、作品总数

- **GET /api/v1/statistics/dynasty/{dynasty_id}** - 获取朝代统计
  - 示例：`/api/v1/statistics/dynasty/ming`
  - 返回：皇帝数量、平均在位时长、事件分类统计、人物分类统计

- **GET /api/v1/statistics/emperor/{emperor_id}** - 获取皇帝统计
  - 示例：`/api/v1/statistics/emperor/ming_taizu`
  - 返回：在位时长、相关事件统计、主要事件列表

- **GET /api/v1/statistics/trends/timeline** - 获取时间线趋势
  - 参数：`dynasty_id`
  - 示例：`/api/v1/statistics/trends/timeline?dynasty_id=ming`
  - 返回：每年事件数量，用于可视化趋势图

- **GET /api/v1/statistics/rankings/emperors** - 获取皇帝排名
  - 参数：
    - `metric` - 排名指标：reign_duration/event_count
    - `limit` - 排名数量（默认10）
  - 示例：`/api/v1/statistics/rankings/emperors?metric=reign_duration&limit=10`

### 8. 关系图谱API (`/api/v1/relations`) - 基于Neo4j

- **GET /api/v1/relations/person/{person_id}** - 获取人物关系图谱
  - 参数：
    - `depth` - 关系深度（1-3层，默认2）
    - `relation_types` - 关系类型过滤，逗号分隔
    - `max_nodes` - 最大节点数（默认50）
  - 示例：`/api/v1/relations/person/zheng_he?depth=2&max_nodes=50`
  - 返回：节点列表、边列表（用于图谱可视化）

- **GET /api/v1/relations/path** - 查找两人关系路径
  - 参数：
    - `from_person_id` (必填) - 起始人物ID
    - `to_person_id` (必填) - 目标人物ID
    - `max_depth` - 最大搜索深度（默认5）
  - 示例：`/api/v1/relations/path?from_person_id=person_a&to_person_id=person_b`
  - 返回：最短关系路径

- **GET /api/v1/relations/event/{event_id}/participants** - 获取事件参与者
  - 示例：`/api/v1/relations/event/jingnan_zhiyi/participants`
  - 返回：参与该事件的所有人物

- **GET /api/v1/relations/emperor/{emperor_id}/ministers** - 获取皇帝臣子
  - 示例：`/api/v1/relations/emperor/ming_taizu/ministers`
  - 返回：侍奉该皇帝的所有臣子

- **GET /api/v1/relations/test** - 测试Neo4j连接
  - 返回：Neo4j连接状态

## API测试

运行测试脚本：

```bash
# 确保API服务正在运行
python test_api.py
```

测试脚本会自动测试所有API端点，并显示测试结果。

## 使用示例

### curl 示例

```bash
# 获取朝代列表
curl http://localhost:8000/api/v1/dynasties

# 获取明朝的所有皇帝
curl "http://localhost:8000/api/v1/emperors?dynasty_id=ming"

# 获取明朝的战争事件
curl "http://localhost:8000/api/v1/events?dynasty_id=ming&event_type=战争"

# 获取明朝的文臣
curl "http://localhost:8000/api/v1/persons?dynasty_id=ming&person_type=文臣"

# 获取明朝时间轴
curl http://localhost:8000/api/v1/timeline/ming

# 全局搜索
curl "http://localhost:8000/api/v1/search?q=朱元璋"

# 搜索建议
curl "http://localhost:8000/api/v1/search/suggest?q=朱"

# 获取整体统计
curl http://localhost:8000/api/v1/statistics/overview

# 获取明朝统计
curl http://localhost:8000/api/v1/statistics/dynasty/ming

# 获取人物关系图谱
curl "http://localhost:8000/api/v1/relations/person/zheng_he?depth=2"

# 查找关系路径
curl "http://localhost:8000/api/v1/relations/path?from_person_id=person_a&to_person_id=person_b"

# 测试Neo4j连接
curl http://localhost:8000/api/v1/relations/test
```

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 获取朝代列表
response = requests.get(f"{BASE_URL}/dynasties")
dynasties = response.json()

# 获取明朝皇帝
response = requests.get(f"{BASE_URL}/emperors", params={"dynasty_id": "ming"})
emperors = response.json()

# 获取事件详情
response = requests.get(f"{BASE_URL}/events/event_id_123")
event = response.json()

# 获取明朝时间轴
response = requests.get(f"{BASE_URL}/timeline/ming")
timeline = response.json()

# 全局搜索
response = requests.get(f"{BASE_URL}/search", params={"q": "朱元璋", "search_type": "all"})
search_results = response.json()

# 获取统计数据
response = requests.get(f"{BASE_URL}/statistics/overview")
stats = response.json()

# 获取朝代统计
response = requests.get(f"{BASE_URL}/statistics/dynasty/ming")
dynasty_stats = response.json()

# 获取人物关系图谱
response = requests.get(f"{BASE_URL}/relations/person/zheng_he", params={"depth": 2})
relations = response.json()

# 查找关系路径
response = requests.get(f"{BASE_URL}/relations/path", params={
    "from_person_id": "person_a",
    "to_person_id": "person_b"
})
path = response.json()
```

## 数据模型

### 事件类型
- 战争
- 政变
- 改革
- 外交
- 文化
- 科技
- 自然灾害
- 其他

### 人物类型
- 皇帝
- 文臣
- 武将
- 诗人
- 画家
- 书法家
- 科学家
- 其他

## 技术栈

- **框架**: FastAPI
- **数据验证**: Pydantic 2.4+
- **数据库**: SQLite
- **服务器**: Uvicorn
- **文档**: OpenAPI/Swagger

## 项目结构

```
server/
├── main.py              # API服务入口
├── api/                 # API路由
│   ├── dynasties.py     # 朝代API
│   ├── emperors.py      # 皇帝API
│   ├── events.py        # 事件API ✅ 完整实现
│   ├── persons.py       # 人物API ✅ 完整实现
│   ├── timeline.py      # 时间轴API ✅ 完整实现
│   ├── search.py        # 搜索API ✨ 新增
│   ├── statistics.py    # 统计API ✨ 新增
│   └── relations.py     # 关系API ✨ 新增
├── schemas/             # Pydantic Schema
│   ├── dynasty.py       # 朝代Schema
│   ├── emperor.py       # 皇帝Schema
│   ├── event.py         # 事件Schema ✅ 完整实现
│   ├── person.py        # 人物Schema ✅ 完整实现
│   └── timeline.py      # 时间轴Schema ✅ 完整实现
├── database/            # 数据库相关
│   ├── sqlite_manager.py
│   ├── neo4j_manager.py  # Neo4j管理器 ✨ 新增
│   └── dependencies.py
└── test_api.py          # API测试脚本 ✅ 完整实现
```

## 注意事项

1. 确保数据库文件 `history.db` 存在且包含数据
2. API默认端口为8000，可在 `main.py` 中修改
3. 所有列表接口默认分页大小为20，最大100
4. 时间轴API可能返回大量数据，请根据需要调整前端处理逻辑
5. **Neo4j功能**：关系图谱API需要Neo4j数据库运行，如未Neo4j未启动，相关接口将返回提示信息

## 下一步开发建议

### 已完成功能 ✅
1. ✅ 全文搜索功能
2. ✅ 数据统计功能
3. ✅ 关系图谱查询（Neo4j）
4. ✅ 完整的API文档

### 待实现功能
1. 实现数据缓存机制（Redis）
2. 添加用户认证和权限管理
3. 添加API限流和监控
4. 性能优化和压力测试
5. Docker容器化部署
