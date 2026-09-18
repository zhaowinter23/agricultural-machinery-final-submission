# 农机作业数据处理与分析系统

基于 **Django** 的农机 GPS 轨迹数据分析系统：地图可视化、轨迹查询、作业量统计分析与图表展示。

> 软件工程管理与实践课 · 企业实训项目（最终答辩提交包）

---

## 💻 运行环境要求

| 项目 | 要求 |
|---|---|
| Python | **3.10 及以上**（3.10 ~ 3.13 均可，推荐 3.12+） |
| 操作系统 | Windows / macOS 均可 |
| 其他 | 浏览器需能联网（页面样式与图表库来自 CDN） |

##  如何运行

> 以下步骤 **Windows 和 Mac 分开写**，只看你自己系统的那一列。

### 第 1 步：安装 Python

如果电脑上已经装过 Python 3.10+，跳过这一步。

- **Windows**：打开 https://www.python.org/downloads/ 下载最新版安装包，
  运行时 **务必勾选底部的 `Add python.exe to PATH`** ⚠️，然后一路 Next
- **Mac**：同一下载地址，下载 macOS 版安装包，一路继续即可

验证：打开命令行（Windows 按 `Win + R` 输入 `cmd` 回车；Mac 打开「终端」），输入：

```
python --version
```

显示 `Python 3.1x.x` 即成功（Mac 上如果 `python` 不行就试 `python3`）。

### 第 2 步：找到代码文件夹

1. 解压收到的作业压缩包（建议解压路径里不要有特殊符号），例如解压到 `D:\农机系统\`
2. 解压后能看到主系统、自动化测试工程、答辩 PPT 和提交说明；本系统的全部代码在其中的 **`agricultural-machinery-system`** 文件夹里

### 第 3 步：在项目文件夹打开命令行

- **Windows**：打开刚解压出的 `agricultural-machinery-system` 文件夹，
  点击上方的地址栏，输入 `cmd` 后按回车 —— 会弹出一个黑窗口，路径正好是项目目录
- **Mac**：打开「终端」，输入 `cd ` （注意有个空格），把项目文件夹拖进终端窗口，按回车

### 第 4 步：创建并激活虚拟环境

虚拟环境是一个独立的 Python 小房间，避免污染系统环境，**每次运行前都要激活**。

- **Windows**：

  ```
  python -m venv venv
  venv\Scripts\activate
  ```

- **Mac**：

  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

激活成功的标志：命令行开头出现 `(venv)` 字样。

### 第 5 步：安装依赖

复制粘贴这一整条命令（已配置国内清华镜像源，下载很快）：

```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> Mac 上如果提示 `pip` 不存在，改用 `pip3 install ...`。

等待安装完成（约 1~2 分钟），最后显示 `Successfully installed ...` 即可。

### 第 6 步：启动系统

```
python manage.py runserver
```

看到下面的输出就说明启动成功：

```
Starting development server at http://127.0.0.1:8000/
```

### 第 7 步：打开浏览器使用 🎉

访问 **http://127.0.0.1:8000** ，用以下默认账号登录：

| 角色 | 用户名 | 密码 | 登录页选择 |
|---|---|---|---|
| 管理员 | `admin` | `admin123` | 管理员登录（可导入/删除数据、管理用户） |
| 普通用户 | `user` | `user123` | 用户登录（查看地图、查询、统计） |

也可以自己点「注册」创建新账号。

> ⚠️ **关闭系统**：在命令行窗口按 `Ctrl + C`。
> **下次再运行**：重复第 3 步（打开命令行）→ 第 4 步（激活虚拟环境）→ 第 6 步（启动）即可，
> 不需要再安装依赖。

## 📊 数据说明

- 仓库**自带数据库** `db.sqlite3`，已导入全部 **8 个地块、43,753 个轨迹点**，下载后开箱即用
- 原始 CSV 数据位于 `单个地块轨迹数据-8个地块/单个地块轨迹数据-8个地块/csv/`（GBK 编码）
- 如需从原始 CSV 重新导入数据（清空重建）：

  ```
  python import_data.py
  ```

- 重置默认账号（admin / user 密码）：

  ```
  python manage.py init_accounts
  ```

## ❓ 常见问题

| 报错/现象 | 原因与解决 |
|---|---|
| `'python' 不是内部或外部命令` | 安装 Python 时没勾选 `Add to PATH`，重新安装并勾选；Mac 用户改用 `python3` |
| `pip` 下载极慢/超时 | 用第 5 步带 `-i https://pypi.tuna.tsinghua.edu.cn/simple` 的完整命令 |
| `Error: That port is already in use` | 8000 端口被占用（多半是上次启动没关），改成 `python manage.py runserver 8001`，浏览器访问 `http://127.0.0.1:8001` |
| `externally-managed-environment` | 没激活虚拟环境就直接 pip 了，回到第 4 步先激活 `(venv)` |
| 页面能开但没有样式 | 电脑需要联网（Bootstrap/Chart.js 走 CDN）；校园网屏蔽外网时会出现 |
| `ModuleNotFoundError: No module named 'django'` | 忘了激活虚拟环境，或没做第 5 步装依赖 |
| 命令行关了系统就打不开 | 正常，runserver 是前台进程，重新启动即可（见第 6 步末尾说明） |

## 📁 项目结构

```
agricultural-machinery-system/
├── manage.py                  # Django 管理入口
├── requirements.txt           # Python 依赖清单
├── import_data.py             # CSV 批量导入脚本
├── generate_paper.py          # 课程论文 Word 生成脚本（可选）
├── db.sqlite3                 # SQLite 数据库（自带全部数据）
├── agricultural_machinery/    # Django 项目配置（settings/urls/wsgi）
├── accounts/                  # 用户应用：注册/登录/改密码
├── tracks/                    # 核心业务应用
│   ├── models.py              #   Track（地块）/ TrackPoint（轨迹点）模型
│   ├── services.py            #   作业量统计计算引擎（官方公式实现）
│   ├── views.py               #   视图：地图/查询/统计/分析/导入/用户管理
│   └── management/commands/init_accounts.py   # 默认账号初始化
├── templates/                 # 页面模板（Bootstrap 5）
├── static/css/                # 自定义样式
├── deploy/                    # 云端部署（PythonAnywhere）WSGI 配置模板
├── docs/                      # 课程文档：第一阶段展示PPT.pptx、第一阶段课程论文.doc
└── 单个地块轨迹数据-8个地块/    # 原始数据（csv 入库，遥感图/xlsx 不入库）
```

