# BUPT 访学指南 — 工程完成情况

> 2026-06-15 整理

---

## 1. 项目概览

基于 VitePress 的静态文档网站，汇聚北邮历届交流访学同学的问卷经验。数据以结构化 JSON 为单一数据源（SSOT），LLM 仅用于生成元数据标签，原始文本 100% 保真。前端通过 Vue 组件异步加载 JSON 并渲染为可筛选的经验卡片墙。Netlify 持续部署。

---

## 2. 已完成模块

### 2.1 前端框架

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| VitePress 配置 (`config.mts`) | ✅ 完成 | 导航栏 5 项、侧边栏 3 组、本地搜索、GitHub 链接 |
| 首页 (`docs/index.md`) | ✅ 完成 | Hero + 4 个 Feature 卡片，含跳转链接 |
| 自定义主题 (`theme/index.ts`) | ✅ 完成 | 扩展默认主题，注册 ExperienceForm、ExperienceWall 组件 |
| 经验征集表单 (`ExperienceForm.vue`) | ✅ 完成 | 双模式表单（结构化提交 / 批量灌入+附件上传），FormData POST 到 Netlify Forms，SSR-safe |
| 经验卡片墙 (`ExperienceWall.vue`) | ✅ 完成 | 客户端异步加载 `experiences.json`，标签筛选 + 响应式 CSS columns 卡片墙 |

### 2.2 文档内容（11 个页面）

| 页面 | 状态 | 内容量 |
| --- | --- | --- |
| `/` 首页 | ✅ | Hero + 4 Feature 卡片 |
| `/pre-departure/` 行前概览 | ✅ | 章节导读 + 核心提示 + ExperienceWall 卡片墙 |
| `/pre-departure/registration-and-credits` | ✅ | 跨校报到流程、学分转换前置手续、校园账号激活 |
| `/pre-departure/packing-checklist` | ✅ | 报到必备文件、电子设备、生活用品 |
| `/academics/` 学业概览 | ✅ | 章节导读 + 核心提示 + ExperienceWall 卡片墙 |
| `/academics/course-selection` | ✅ | 调研方法、课程搭配表、学分转换 |
| `/academics/lab-and-research` | ✅ | 首月建议、导师沟通表、常见隐患 |
| `/life-and-mindset/` 生活概览 | ✅ | 章节导读 + 核心提示 + ExperienceWall 卡片墙 |
| `/life-and-mindset/daily-life` | ✅ | 住宿/交通/饮食/社交四维覆盖 |
| `/life-and-mindset/mental-health` | ✅ | 四阶段模型、三种困境应对、求助指南 |
| `/contribute/` | ✅ | 经验征集表单 + Netlify Forms 提交说明 |

### 2.3 ETL 数据管道

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| `extract.py` | ✅ 完成 | CSV 读取、列名别名映射（含 Netlify Forms `content`→`response` 及中文分类→英文 key）、PII 正则脱敏 |
| `transform.py` | ✅ 完成 | 逐行 LLM 元数据提取（`tags` + `alias`），batch=20，原文不修改；失败自动降级为空元数据 |
| `load.py` | ✅ 完成 | 增量追加写入 `experiences.json`，按 MD5 id 去重；损坏 JSON 时自动重建 |
| `run.py` | ✅ 完成 | 三阶段管道入口，错误兜底处理 |
| `config.py` | ✅ 完成 | 路径、LLM Provider 切换、`EXPERIENCES_JSON_PATH` 常量 |
| `prompts/row_extraction.txt` | ✅ 完成 | 逐行提取 `tags`（2-3 词）+ `alias`（可选）JSON 数组输出 |
| `fetcher.py` | ✅ 完成 | Netlify Forms API 拉取 + 附件下载缓存，返回与 `read_all_csvs()` 同构的行列表 |
| `parser.py` | ✅ 完成 | 附件文本提取（TXT / 文本型 PDF），永不抛异常；图片/扫描 PDF 返回语义化占位符 |

### 2.4 数据存储

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| `docs/public/data/experiences.json` | ✅ 完成 | 结构化经验数据库（SSOT），每条约含 `id` / `original_text` / `category` / `tags` / `alias` / `source_file`，`meta` 含更新时间与总数 |

### 2.5 环境与部署

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| `package.json` | ✅ 完成 | VitePress 1.6.4 + Vue 3.5 |
| `netlify.toml` | ✅ 完成 | Node 22 构建环境、静态资源永久缓存 |
| `.env.example` | ✅ 完成 | 三个 LLM Provider 的 Key 模板 |
| `.env` | ✅ 完成 | DeepSeek API Key 已配置 |
| `.gitignore` | ✅ 完成 | 排除 CSV 原始数据、构建产物、`.vitepress/cache/`、`.env` |
| `requirements.txt` | ✅ 完成 | 7 个 Python 依赖（openai/pandas/dotenv/tenacity/jsonschema/pdfplumber/requests） |
| `README.md` | ✅ 完成 | 13 节完整维护手册，含 Netlify Forms 数据回收流程、故障排查表与上线清单 |

---

## 3. 待补充事项

### 3.1 问卷数据

| 位置 | 状态 | 说明 |
| --- | --- | --- |
| `data/raw/` | ⬜ 空目录（仅 .gitkeep） | 需放入问卷 CSV 后运行 ETL 管道；数据来源：历届问卷导出 或 Netlify Forms 导出 |
| `docs/public/data/experiences.json` | ✅ 已存在 | 当前为空（0 条记录），放入 CSV 运行 ETL 后自动填充 |

> **数据更新流程**：放入 CSV → 运行 `.venv/Scripts/python scripts/etl/run.py` → 脚本对每条原文调用 LLM 提取 tags/alias → 追加写入 `experiences.json`（MD5 去重）→ 推送后前端卡片墙自动更新。

### 3.2 建议后续增强

| 事项 | 说明 |
| --- | --- |
| `ExperienceWall.vue` 错误状态 | fetch 失败时与控制台空数据共用"暂无数据"，建议增加独立错误提示 |
| 多模态附件处理 | `parser.py` 暂不支持图片/扫描 PDF，参见 README §13.6 Roadmap |

---

## 4. 项目统计

| 维度 | 数量 |
| --- | --- |
| 手写文档页面 | 11 个 |
| Vue 前端组件 | 2 个（ExperienceForm.vue、ExperienceWall.vue） |
| ETL Python 脚本 | 7 个 |
| LLM 提示词模板 | 1 个（row_extraction.txt） |
| JSON 数据存储 | 1 个（experiences.json，SSOT） |
| 内容分类 | 3 个（行前/学业/生活） |
| 总代码行数（估） | ~1,300 行（含 Python + Vue + TS） |

---

## 5. 快速启动命令

```bash
# 本地开发
npm run docs:dev                    # 启动热更新服务器 → http://localhost:5173

# 内容更新（放入 CSV 后）
.venv/Scripts/python scripts/etl/run.py  # CSV → LLM 逐行标签提取 → experiences.json
npm run docs:dev                         # 本地预览确认

# 部署
npm run docs:build                  # 构建生产版本
npm run docs:preview                # 本地预览构建产物
git add docs/ && git commit -m "..." && git push  # 推送自动部署
```

---

## 6. 项目架构图

### 数据采集三通道

```
┌─ 通道 A：批量导入 ─────────────────────────┐
│  问卷 CSV → data/raw/*.csv                  │
└────────────────────┬────────────────────────┘
                     │
┌─ 通道 B：在线征集 ─────────────────────────┐
│  访问者 → /contribute/ (ExperienceForm)     │
│      │                                      │
│      │ POST form-name=experience-...        │
│      ▼                                      │
│  Netlify Forms 面板 → Export to CSV         │
│      │                                      │
│      ▼                                      │
│  data/raw/netlify-forms.csv                 │
└────────────────────┬────────────────────────┘
                     │
┌─ 通道 C：API 直拉 ─────────────────────────┐
│  Netlify API ← fetcher.py                   │
│      │                                      │
│      ▼  download_attachment()               │
│  .vitepress/cache/attachments/              │
│      │                                      │
│      ▼  parser.py（TXT / PDF 文本提取）      │
│  rows (同构 list[dict])                     │
└────────────────────┬────────────────────────┘
                     │
                     ▼  extract.py（CSV 读取 + PII 脱敏 + 字段映射）
                     │
                     ▼  transform.py（LLM 逐行提取 tags + alias）
                     │
                     ▼  load.py（追加去重写入 experiences.json）
                     │
                     └──▶ docs/public/data/experiences.json
                               │
                               ▼  ExperienceWall.vue（客户端 fetch + 筛选卡片墙）
```

### 文件结构

```
docs/                           .vitepress/
  index.md                         config.mts     ← 导航/侧边栏/搜索
  pre-departure/                   theme/
    index.md (手写 + 组件)           index.ts      ← 注册 ExperienceForm、ExperienceWall
    registration-and-credits.md      components/
    packing-checklist.md               ExperienceForm.vue  ← 经验征集
  academics/                           ExperienceWall.vue   ← 卡片墙
    index.md (手写 + 组件)
    course-selection.md
    lab-and-research.md
  life-and-mindset/
    index.md (手写 + 组件)
    daily-life.md
    mental-health.md
  contribute/
    index.md (手写 + 组件 + Netlify 静态桩)
  public/data/
    experiences.json (JSON SSOT，ETL 增量写入)
```

---

*本文件为项目完成状态的快照记录，后续更新数据、部署上线时请相应更新。*
