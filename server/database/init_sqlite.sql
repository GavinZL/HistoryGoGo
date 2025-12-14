-- HistoryGogo SQLite数据库初始化脚本
-- 创建历史时间轴数据库表结构

-- 朝代表
CREATE TABLE IF NOT EXISTS dynasties (
    dynasty_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL,
    capital TEXT,
    founder TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 皇帝表
CREATE TABLE IF NOT EXISTS emperors (
    emperor_id TEXT PRIMARY KEY,
    dynasty_id TEXT NOT NULL,
    name TEXT NOT NULL,
    temple_name TEXT,
    reign_title TEXT,
    birth_date DATE,
    death_date DATE,
    reign_start DATE NOT NULL,
    reign_end DATE,
    reign_duration INTEGER,
    dynasty_order INTEGER NOT NULL,
    biography TEXT,
    achievements TEXT,
    portrait_url TEXT,
    data_source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dynasty_id) REFERENCES dynasties(dynasty_id)
);

-- 事件表
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    dynasty_id TEXT NOT NULL,
    emperor_id TEXT,
    title TEXT NOT NULL,
    event_type TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    location TEXT,
    description TEXT,
    significance TEXT,
    casualty TEXT,
    result TEXT,
    data_source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dynasty_id) REFERENCES dynasties(dynasty_id),
    FOREIGN KEY (emperor_id) REFERENCES emperors(emperor_id)
);

-- 人物表
CREATE TABLE IF NOT EXISTS persons (
    person_id TEXT PRIMARY KEY,
    dynasty_id TEXT NOT NULL,
    name TEXT NOT NULL,
    alias TEXT,  -- JSON数组
    birth_date DATE,
    death_date DATE,
    person_type TEXT NOT NULL,
    position TEXT,
    biography TEXT,
    style TEXT,
    contributions TEXT,
    portrait_url TEXT,
    data_source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dynasty_id) REFERENCES dynasties(dynasty_id)
);

-- 作品表
CREATE TABLE IF NOT EXISTS works (
    work_id TEXT PRIMARY KEY,
    person_id TEXT NOT NULL,
    title TEXT NOT NULL,
    work_type TEXT,
    creation_date DATE,
    description TEXT,
    content TEXT,
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(person_id)
);

-- 事件人物关联表
CREATE TABLE IF NOT EXISTS event_person_relation (
    relation_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    person_id TEXT NOT NULL,
    role TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (person_id) REFERENCES persons(person_id),
    UNIQUE(event_id, person_id)
);

-- 人物关系表
CREATE TABLE IF NOT EXISTS person_relations (
    relation_id TEXT PRIMARY KEY,
    person_id_from TEXT NOT NULL,
    person_id_to TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id_from) REFERENCES persons(person_id),
    FOREIGN KEY (person_id_to) REFERENCES persons(person_id),
    UNIQUE(person_id_from, person_id_to, relation_type)
);

-- 创建索引以优化查询性能

-- 皇帝表索引
CREATE INDEX IF NOT EXISTS idx_emperors_dynasty_id ON emperors(dynasty_id);
CREATE INDEX IF NOT EXISTS idx_emperors_reign_dates ON emperors(reign_start, reign_end);
CREATE INDEX IF NOT EXISTS idx_emperors_order ON emperors(dynasty_order);

-- 事件表索引
CREATE INDEX IF NOT EXISTS idx_events_dynasty_id ON events(dynasty_id);
CREATE INDEX IF NOT EXISTS idx_events_emperor_id ON events(emperor_id);
CREATE INDEX IF NOT EXISTS idx_events_start_date ON events(start_date);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

-- 人物表索引
CREATE INDEX IF NOT EXISTS idx_persons_dynasty_id ON persons(dynasty_id);
CREATE INDEX IF NOT EXISTS idx_persons_type ON persons(person_type);
CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);

-- 作品表索引
CREATE INDEX IF NOT EXISTS idx_works_person_id ON works(person_id);

-- 关联表索引
CREATE INDEX IF NOT EXISTS idx_event_person_event_id ON event_person_relation(event_id);
CREATE INDEX IF NOT EXISTS idx_event_person_person_id ON event_person_relation(person_id);
CREATE INDEX IF NOT EXISTS idx_person_relations_from ON person_relations(person_id_from);
CREATE INDEX IF NOT EXISTS idx_person_relations_to ON person_relations(person_id_to);

-- 插入明朝基础数据
INSERT OR REPLACE INTO dynasties (dynasty_id, name, start_year, end_year, capital, founder, description)
VALUES (
    'ming',
    '明朝',
    1368,
    1644,
    '北京',
    '朱元璋',
    '明朝（1368年-1644年）是中国历史上最后一个由汉族建立的大一统王朝，共传十六帝，享国276年。'
);
