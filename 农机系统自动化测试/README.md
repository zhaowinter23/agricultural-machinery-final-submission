# 农机作业量统计分析系统 —— 自动化测试工程

独立于主系统（`../agricultural-machinery-system/`）的自动化测试工程。

## 架构：

测试代码物理隔离，但能 import 主系统，靠三点：

1. **`pytest.ini` 的 `pythonpath`** → 在 pytest-django 极早期扫描 settings 之前，把 `../agricultural-machinery-system`（同级的主系统目录）与 `.` 加入 `sys.path`。pytest 的 pythonpath 按空白拆分、且软链接在 Windows 解压后会失效，因此主系统目录采用无空格命名、直接相对定位，任何平台开箱即用。
2. **`conftest.py`** → 再做一道 sys.path 保险（同样定位到同级主系统目录）。
3. **`test_settings.py`** → `from agricultural_machinery.settings import *` 继承主系统全部配置，仅把测试数据库 `test_db.sqlite3` 指向本目录；主系统目录不沾任何测试产物。

`conftest.py` 同时设置 `DJANGO_ALLOW_ASYNC_UNSAFE=true`（解决 pytest-playwright 异步循环与 pytest-django 同步建库的冲突，仅测试环境），并提供共享 fixtures（合成数据工厂、测试用户）。

## 安装

```bash
pip3 install -r requirements.txt
python3 -m playwright install chromium
```

> 还需主系统能被 import：其运行时依赖（Django、pandas、openpyxl 等）需已安装。

## 运行

```bash
python3 -m pytest                         # 跑全部（单元+集成+E2E）
python3 -m pytest -m "not e2e"            # 跳过 E2E（快，无需浏览器）
python3 -m pytest -m e2e                  # 只跑 E2E
python3 -m pytest --cov                   # 带覆盖率
python3 -m pytest unit/test_services.py   # 只跑某文件
python3 -m pytest -k area                 # 按名字筛选用例
```

## 目录结构

```
农机系统自动化测试/
├── pytest.ini              # 配置：DJANGO_SETTINGS_MODULE、pythonpath、markers
├── test_settings.py        # 继承主系统 settings，覆盖 DB 到本目录
├── conftest.py             # sys.path + 共享 fixtures（track_factory/用户）+ 异步开关
├── .coveragerc             # 覆盖率配置
├── unit/                   # 单元测试
│   ├── test_smoke.py       # 架构冒烟
│   └── test_services.py    # 计算引擎公式正确性（12 例，含参数化+边界）
├── integration/            # 集成测试（Django test client）
│   ├── test_auth_permissions.py  # 登录流程 + 权限隔离（6 例）
│   ├── test_import.py            # 防重复导入回归（2 例）
│   └── test_views.py             # geojson/导出/查询分页/API/统计页（6 例）
└── e2e/                    # 端到端测试（Playwright + live_server）
    ├── seed_data.py        # 数据播种与登录辅助
    ├── test_login_flow.py
    ├── test_statistics_page.py
    ├── test_query_page.py
    └── test_map_page.py    # 地图点地块→信息面板（依赖 Leaflet CDN，需联网）
```

## 分层与用例数

| 层 | 测什么 | 工具 | 用例 |
|---|---|---|---|
| 单元 | 计算引擎公式、关机停歇清洗、边界 | pytest + 合成数据工厂 | 14 |
| 集成 | 视图/权限/登录/导入/API | pytest + Django test client | 14 |
| E2E | 登录流、统计页、查询、地图交互 | Playwright + live_server | 4 |

共 **32 例**，约 19 秒跑完。

## 覆盖率（主系统代码）

| 文件 | 覆盖率 |
|---|---|
| tracks/services.py（计算引擎） | 98% |
| tracks/models.py | 97% |
| tracks/views.py | 70% |
| accounts/views.py | 51%（注册/改密未测） |
| **整体** | **77%** |

## 核心设计原则

1. **期望值手算自规格**：公式测试的期望值按 PPT/PDF 官方公式手算，绝不跑实现拿值——避免"用实现验证实现"。
2. **合成数据工厂**：`track_factory` 造 3~5 个点的小数据，不依赖生产库 4 万点——快、可控、可手算。
3. **测试即回归**：防重复导入、角色登录、geojson 的 gps_ts 等真实缺陷都锁成了用例。
4. **测什么就隔离什么**：测权限用 `force_login` 跳登录，测登录才走表单；E2E 用 `live_server` 走真实 HTTP。
5. **变异测试驱动补用例**：曾对计算引擎注入 7 个变异体，首轮变异得分 57%，定位 3 处断言盲区（working_distance/idle_time/segments），补断言后升至 100%。

## 已知限制

- E2E 地图用例依赖 Leaflet（CDN），需联网；无网会超时失败。
- `accounts/views.py` 的注册、改密流程尚未覆盖（可后续补）。
