# BUPT 访学指南 — 工程完成情况

> 2026-06-14 整理

---

## 1. 项目概览

基于 VitePress 的静态文档网站，汇聚北邮历届交流访学同学的问卷经验。内容由 CSV 问卷数据 + LLM 提炼自动生成，通过 Netlify 持续部署。

---

## 2. 已完成模块

### 2.1 前端框架

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| VitePress 配置 (`config.mts`) | ✅ 完成 | 导航栏 5 项、侧边栏 4 组、本地搜索、GitHub 链接 |
| 首页 (`docs/index.md`) | ✅ 完成 | Hero + 4 个 Feature 卡片，含跳转链接 |
| 自定义主题 (`theme/index.ts`) | ✅ 完成 | 扩展默认主题，注册 KeywordBubble 组件 |
| 词云组件 (`KeywordBubble.vue`) | ✅ 完成 | ECharts + echarts-wordcloud，圆形布局，SSR-safe 延迟加载 |
| 词云数据 (`keywords.json`) | ✅ 完成 | 包含 15 个关键词及频次，JSON Schema 校验写入 |

### 2.2 文档内容（11 个页面）

| 页面 | 状态 | 内容量 |
| --- | --- | --- |
| `/` 首页 | ✅ | Hero + 4 Feature 卡片 |
| `/pre-departure/` 行前概览 | ✅ | 章节导读 + 核心提示 |
| `/pre-departure/visa-and-documents` | ✅ | 签证类型、时间线、材料清单 |
| `/pre-departure/packing-checklist` | ✅ | 证件/电子/生活三大类 + 重量提示 |
| `/academics/` 学业概览 | ✅ | 章节导读 + 核心提示 |
| `/academics/course-selection` | ✅ | 调研方法、课程搭配表、学分转换 |
| `/academics/lab-and-research` | ✅ | 首月建议、导师沟通表、常见隐患 |
| `/life-and-mindset/` 生活概览 | ✅ | 章节导读 + 核心提示 |
| `/life-and-mindset/daily-life` | ✅ | 住宿/交通/饮食/社交四维覆盖 |
| `/life-and-mindset/mental-health` | ✅ | 四阶段模型、三种困境应对、求助指南 |
| `/insights/keyword-overview` | ✅ | 词云展示 + 文字说明 |

### 2.3 ETL 数据管道

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| `extract.py` | ✅ 完成 | CSV 读取、列名别名映射、PII 正则脱敏（学号/手机/邮箱） |
| `transform.py` | ✅ 完成 | 按分类分组、LLM 调用提炼摘要、关键词频次统计 |
| `load.py` | ✅ 完成 | Markdown 写入 + JSON Schema 校验 + 日期标注 |
| `run.py` | ✅ 完成 | 三阶段管道入口，错误兜底处理 |
| `config.py` | ✅ 完成 | 路径、LLM Provider 切换、种子关键词 |
| `prompts/insight_extraction.txt` | ✅ 完成 | 核心建议/常见困难/综合总结 三段式 |
| `prompts/keyword_extraction.txt` | ✅ 完成 | JSON 数组输出，≤30 词，2-6 字 |

### 2.4 环境与部署

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| `package.json` | ✅ 完成 | VitePress 1.6.4 + Vue 3.5 + ECharts 5.5 |
| `netlify.toml` | ✅ 完成 | Node 22 构建环境、静态资源永久缓存、JSON 1 小时缓存 |
| `.env.example` | ✅ 完成 | 三个 LLM Provider 的 Key 模板 |
| `.env` | ✅ 完成 | DeepSeek API Key 已配置 |
| `.gitignore` | ✅ 完成 | 排除 CSV 原始数据、构建产物、.env |
| `requirements.txt` | ✅ 完成 | 5 个 Python 依赖（openai/pandas/dotenv/tenacity/jsonschema） |
| `README.md` | ✅ 完成 | 11 节完整维护手册，含故障排查表与上线清单 |

---

## 3. 待补充事项

### 3.1 占位符更新

| 位置 | 占位符 | 应替换为 |
| --- | --- | --- |
| `.vitepress/config.mts:62` | `YOUR_ORG/bupt-visiting-guide` | 实际的 GitHub 组织/用户名 |
| `.vitepress/config.mts:67` | `YOUR_ORG/bupt-visiting-guide/edit/main` | 实际的 GitHub 编辑链接 |

### 3.2 问卷数据

| 位置 | 状态 | 说明 |
| --- | --- | --- |
| `data/raw/` | ⬜ 空目录（仅 .gitkeep） | 需要放入真实问卷 CSV 后运行 ETL 管道 |

> **注意**：`keywords.json` 中当前 15 个关键词的频次来自种子关键词在空数据上的直接计数（种子里有 "交流项目"、"绩点"、"实验室" 等词，但现数据无法验证来源），放 CSV 后重新跑 `python scripts/etl/run.py` 即可覆盖为真实数据。

### 3.3 未生成的内容

`generated-insights.md` 文件尚未生成（需 CSV 数据驱动 LLM 调用后自动写入）：

| 文件 | 状态 | 触发方式 |
| --- | --- | --- |
| `docs/pre-departure/generated-insights.md` | ⬜ 待生成 | `python scripts/etl/run.py` |
| `docs/academics/generated-insights.md` | ⬜ 待生成 | `python scripts/etl/run.py` |
| `docs/life-and-mindset/generated-insights.md` | ⬜ 待生成 | `python scripts/etl/run.py` |

---

## 4. 项目统计

| 维度 | 数量 |
| --- | --- |
| 手写文档页面 | 11 个 |
| LLM 自动生成页面 | 3 个（待 CSV 数据驱动） |
| ETL 脚本 | 5 个 Python 文件 |
| LLM 提示词 | 2 个模板 |
| 前端组件 | 1 个（KeywordBubble.vue） |
| 种子关键词 | 15 个 |
| 内容分类 | 3 个（行前/学业/生活） |
| 总代码行数（估） | ~600 行（含 Python + Vue + TS） |

---

## 5. 快速启动命令

```bash
# 本地开发
npm run docs:dev                    # 启动热更新服务器 → http://localhost:5173

# 内容更新（放入 CSV 后）
python scripts/etl/run.py           # CSV → LLM 提炼 → Markdown + JSON
npm run docs:dev                    # 本地预览确认

# 部署
npm run docs:build                  # 构建生产版本
npm run docs:preview                # 本地预览构建产物
git add docs/ && git commit -m "..." && git push  # 推送自动部署
```

---

## 6. 项目架构图

```
data/raw/*.csv
    │  extract.py（读取 + PII 脱敏）
    ▼
    │  transform.py（LLM 提炼摘要 + 关键词频次统计）
    ▼
    ├──▶ docs/{category}/generated-insights.md  （3 个分类的 LLM 总结）
    └──▶ docs/public/data/keywords.json         （词云数据源）
              │
              ▼  KeywordBubble.vue（ECharts 渲染）
```

```
docs/                        .vitepress/
  index.md                      config.mts    ← 导航/侧边栏/搜索
  pre-departure/                theme/
    index.md (手写)               index.ts     ← 注册 KeywordBubble
    visa-and-documents.md         components/
    packing-checklist.md            KeywordBubble.vue  ← 词云
    generated-insights.md (LLM)
  academics/                   
    index.md (手写)
    course-selection.md
    lab-and-research.md
    generated-insights.md (LLM)
  life-and-mindset/
    index.md (手写)
    daily-life.md
    mental-health.md
    generated-insights.md (LLM)
  insights/
    keyword-overview.md (手写 + 组件)
  public/data/
    keywords.json (ETL 自动生成)
```

---

*本文件为项目完成状态的快照记录，后续更新数据、部署上线时请相应更新。*
