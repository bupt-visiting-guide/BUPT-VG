# BUPT 访学指南 — 工程完成情况

> 2026-06-15 整理

---

## 1. 项目概览

基于 VitePress 的静态文档网站，汇聚北邮历届交流访学同学的问卷经验。内容由 CSV 问卷数据 + LLM 提炼自动生成，通过 Netlify 持续部署。

---

## 2. 已完成模块

### 2.1 前端框架

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| VitePress 配置 (`config.mts`) | ✅ 完成 | 导航栏 5 项、侧边栏 3 组（含 generated-insights 链接）、本地搜索、GitHub 链接 |
| 首页 (`docs/index.md`) | ✅ 完成 | Hero + 4 个 Feature 卡片，含跳转链接 |
| 自定义主题 (`theme/index.ts`) | ✅ 完成 | 扩展默认主题，注册 ExperienceForm 组件 |
| 经验征集表单 (`ExperienceForm.vue`) | ✅ 完成 | 双模式表单（结构化提交 / 批量灌入+附件上传），FormData POST 到 Netlify Forms，SSR-safe |

### 2.2 文档内容（14 个页面）

| 页面 | 状态 | 内容量 |
| --- | --- | --- |
| `/` 首页 | ✅ | Hero + 4 Feature 卡片 |
| `/pre-departure/` 行前概览 | ✅ | 章节导读 + 核心提示 + generated-insights 链接 |
| `/pre-departure/registration-and-credits` | ✅ | 跨校报到流程、学分转换前置手续、校园账号激活 |
| `/pre-departure/packing-checklist` | ✅ | 报到必备文件、电子设备、生活用品 |
| `/pre-departure/generated-insights` | ✅ | 侧边栏已链接（暂无 CSV 数据时为占位提示） |
| `/academics/` 学业概览 | ✅ | 章节导读 + 核心提示 + generated-insights 链接 |
| `/academics/course-selection` | ✅ | 调研方法、课程搭配表、学分转换 |
| `/academics/lab-and-research` | ✅ | 首月建议、导师沟通表、常见隐患 |
| `/academics/generated-insights` | ✅ | 侧边栏已链接，由 Netlify Forms 数据驱动 LLM 生成 |
| `/life-and-mindset/` 生活概览 | ✅ | 章节导读 + 核心提示 + generated-insights 链接 |
| `/life-and-mindset/daily-life` | ✅ | 住宿/交通/饮食/社交四维覆盖 |
| `/life-and-mindset/mental-health` | ✅ | 四阶段模型、三种困境应对、求助指南 |
| `/life-and-mindset/generated-insights` | ✅ | 侧边栏已链接（暂无 CSV 数据时为占位提示） |
| `/contribute/` | ✅ | 经验征集表单 + Netlify Forms 提交说明 |

### 2.3 ETL 数据管道

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| `extract.py` | ✅ 完成 | CSV 读取、列名别名映射（含 Netlify Forms `content`→`response` 及中文分类→英文 key）、PII 正则脱敏 |
| `transform.py` | ✅ 完成 | 按分类分组、LLM 调用提炼摘要（含指数退避重试） |
| `load.py` | ✅ 完成 | Markdown 写入（全量覆盖），日期标注 |
| `run.py` | ✅ 完成 | 三阶段管道入口，错误兜底处理 |
| `config.py` | ✅ 完成 | 路径、LLM Provider 切换 |
| `prompts/insight_extraction.txt` | ✅ 完成 | 核心建议/常见困难/综合总结 三段式，含系统占位符忽略指令 |
| `fetcher.py` | ✅ 完成 | Netlify Forms API 拉取 + 附件下载缓存，返回与 `read_all_csvs()` 同构的行列表 |
| `parser.py` | ✅ 完成 | 附件文本提取（TXT / 文本型 PDF），永不抛异常；图片/扫描 PDF 返回语义化占位符 |

### 2.4 环境与部署

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| `package.json` | ✅ 完成 | VitePress 1.6.4 + Vue 3.5 |
| `netlify.toml` | ✅ 完成 | Node 22 构建环境、静态资源永久缓存 |
| `.env.example` | ✅ 完成 | 三个 LLM Provider 的 Key 模板 |
| `.env` | ✅ 完成 | DeepSeek API Key 已配置 |
| `.gitignore` | ✅ 完成 | 排除 CSV 原始数据、构建产物、.env |
| `requirements.txt` | ✅ 完成 | 7 个 Python 依赖（openai/pandas/dotenv/tenacity/jsonschema/pdfplumber/requests） |
| `README.md` | ✅ 完成 | 13 节完整维护手册，含 Netlify Forms 数据回收流程、故障排查表与上线清单 |

---

## 3. 待补充事项

### 3.1 问卷数据

| 位置 | 状态 | 说明 |
| --- | --- | --- |
| `data/raw/` | ⬜ 空目录（仅 .gitkeep） | 需放入问卷 CSV 后运行 ETL 管道；数据来源：历届问卷导出 或 Netlify Forms 导出 |

> **注意**：generated-insights.md 由 CSV 数据驱动 LLM 生成，放入新 CSV 后运行 `.venv/Scripts/python scripts/etl/run.py`（或 `.venv/bin/python`）即可覆盖更新。

### 3.2 未生成的内容

| 文件 | 状态 | 触发方式 |
| --- | --- | --- |
| `docs/pre-departure/generated-insights.md` | ⬜ 占位文件 | `.venv/Scripts/python scripts/etl/run.py`（需对应分类的 CSV 数据） |
| `docs/academics/generated-insights.md` | ✅ 已生成 | 由 1 条 Netlify Forms 批量提交数据驱动 LLM 生成 |
| `docs/life-and-mindset/generated-insights.md` | ⬜ 占位文件 | `.venv/Scripts/python scripts/etl/run.py`（需对应分类的 CSV 数据） |

---

## 4. 项目统计

| 维度 | 数量 |
| --- | --- |
| 手写文档页面 | 14 个 |
| LLM 自动生成页面 | 3 个（1 个已生成，2 个占位待数据） |
| ETL 脚本 | 7 个 Python 文件 |
| LLM 提示词 | 1 个模板 |
| 前端组件 | 1 个（ExperienceForm.vue） |
| 内容分类 | 3 个（行前/学业/生活） |
| 总代码行数（估） | ~1,100 行（含 Python + Vue + TS） |

---

## 5. 快速启动命令

```bash
# 本地开发
npm run docs:dev                    # 启动热更新服务器 → http://localhost:5173

# 内容更新（放入 CSV 后）
.venv/Scripts/python scripts/etl/run.py  # CSV → LLM 提炼 → Markdown
npm run docs:dev                         # 本地预览确认

# 部署
npm run docs:build                  # 构建生产版本
npm run docs:preview                # 本地预览构建产物
git add docs/ && git commit -m "..." && git push  # 推送自动部署
```

---

## 6. 项目架构图

### 数据采集双通道

```
┌─ 通道 A：批量导入 ─────────────────────┐
│                                         │
│  问卷 CSV → data/raw/*.csv              │
│                                         │
└────────────────────┬────────────────────┘
                     │
┌─ 通道 B：在线征集 ─────────────────────┐
│                                         │
│  访问者 → /contribute/ (ExperienceForm) │
│      │                                  │
│      │ POST form-name=experience-...    │
│      ▼                                  │
│  Netlify Forms 面板 → Export to CSV     │
│      │                                  │
│      ▼                                  │
│  data/raw/netlify-forms.csv             │
│                                         │
└────────────────────┬────────────────────┘
                     │
                     ▼  extract.py（读取 + PII 脱敏 + 字段映射）
                     │
                     ▼  transform.py（LLM 提炼摘要）
                     │
                     ▼  load.py（写入 Markdown）
                     │
                     └──▶ docs/{category}/generated-insights.md  （3 个分类的 LLM 总结）
```

### 文件结构

```
docs/                        .vitepress/
  index.md                      config.mts    ← 导航/侧边栏/搜索
  pre-departure/                theme/
    index.md (手写)               index.ts     ← 注册 ExperienceForm
    registration-and-credits.md    components/
    packing-checklist.md            ExperienceForm.vue ← 经验征集
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
  contribute/
    index.md (手写 + 组件 + Netlify 静态桩)
```

---

*本文件为项目完成状态的快照记录，后续更新数据、部署上线时请相应更新。*
