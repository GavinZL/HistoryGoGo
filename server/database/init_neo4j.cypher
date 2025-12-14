// HistoryGogo Neo4j图数据库初始化脚本
// 用于创建节点和关系的约束和索引

// ========================================
// 创建唯一性约束
// ========================================

// 朝代节点约束
CREATE CONSTRAINT dynasty_id_unique IF NOT EXISTS
FOR (d:Dynasty) REQUIRE d.id IS UNIQUE;

// 皇帝节点约束
CREATE CONSTRAINT emperor_id_unique IF NOT EXISTS
FOR (e:Emperor) REQUIRE e.id IS UNIQUE;

// 事件节点约束
CREATE CONSTRAINT event_id_unique IF NOT EXISTS
FOR (ev:Event) REQUIRE ev.id IS UNIQUE;

// 人物节点约束
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

// 作品节点约束
CREATE CONSTRAINT work_id_unique IF NOT EXISTS
FOR (w:Work) REQUIRE w.id IS UNIQUE;

// ========================================
// 创建索引以优化查询性能
// ========================================

// 朝代索引
CREATE INDEX dynasty_name_index IF NOT EXISTS
FOR (d:Dynasty) ON (d.name);

// 皇帝索引
CREATE INDEX emperor_name_index IF NOT EXISTS
FOR (e:Emperor) ON (e.name);

CREATE INDEX emperor_order_index IF NOT EXISTS
FOR (e:Emperor) ON (e.dynasty_order);

// 事件索引
CREATE INDEX event_title_index IF NOT EXISTS
FOR (ev:Event) ON (ev.title);

CREATE INDEX event_type_index IF NOT EXISTS
FOR (ev:Event) ON (ev.event_type);

CREATE INDEX event_date_index IF NOT EXISTS
FOR (ev:Event) ON (ev.start_date);

// 人物索引
CREATE INDEX person_name_index IF NOT EXISTS
FOR (p:Person) ON (p.name);

CREATE INDEX person_type_index IF NOT EXISTS
FOR (p:Person) ON (p.person_type);

// ========================================
// 示例：创建明朝节点
// ========================================

// 创建明朝节点（示例）
MERGE (d:Dynasty {id: 'ming'})
SET d.name = '明朝',
    d.start_year = 1368,
    d.end_year = 1644,
    d.capital = '北京',
    d.founder = '朱元璋',
    d.description = '明朝（1368年-1644年）是中国历史上最后一个由汉族建立的大一统王朝，共传十六帝，享国276年。';

// ========================================
// 关系类型说明
// ========================================

// 以下是将要使用的关系类型：
// 1. BELONGS_TO - 归属关系（皇帝/事件/人物 → 朝代）
// 2. RULED_BY - 统治关系（朝代 → 皇帝）
// 3. SUCCEEDED_BY - 皇位继承（皇帝 → 皇帝）
// 4. OCCURRED_DURING - 事件发生在某皇帝时期（事件 → 皇帝）
// 5. PARTICIPATED_IN - 人物参与事件（人物 → 事件）
// 6. SERVED_UNDER - 侍奉关系（人物 → 皇帝）
// 7. TEACHER_STUDENT - 师生关系（老师 → 学生）
// 8. FAMILY - 家族关系（人物 ←→ 人物）
// 9. COLLEAGUE - 同僚关系（人物 ←→ 人物）
// 10. FRIEND - 友谊关系（人物 ←→ 人物）
// 11. ENEMY - 敌对关系（人物 ←→ 人物）
// 12. CREATED - 创作关系（人物 → 作品）
