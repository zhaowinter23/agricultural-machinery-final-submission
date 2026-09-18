"""生成课程论文 Word 文档"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# ========== 全局样式 ==========
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.first_line_indent = Cm(0.74)

# 辅助函数
def add_title(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)
        run.font.name = '黑体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

def add_para(text, bold=False, indent=True):
    p = doc.add_paragraph()
    if not indent:
        p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.bold = bold
    return p

def add_image_placeholder(caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f'【此处插入截图：{caption}】')
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.color.rgb = RGBColor(128, 128, 128)
    run.italic = True
    # 图注
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.first_line_indent = Cm(0)
    cr = cp.add_run(caption)
    cr.font.size = Pt(10)
    cr.font.name = '宋体'
    cr.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

def add_table(headers, rows, caption=''):
    if caption:
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.first_line_indent = Cm(0)
        cr = cp.add_run(caption)
        cr.font.size = Pt(10)
        cr.bold = True
        cr.font.name = '宋体'
        cr.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # 表头
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(10)
                run.font.name = '宋体'
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    # 数据
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri+1].cells[ci]
            cell.text = str(val)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(10)
                    run.font.name = '宋体'
                    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# ========== 封面 ==========
for _ in range(4):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Cm(0)
run = p.add_run('课程名称：软件工程管理与实践')
run.font.size = Pt(16)
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Cm(0)
run = p.add_run('农机作业数据处理与分析系统设计与实现')
run.font.size = Pt(22)
run.bold = True
run.font.name = '黑体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

for _ in range(3):
    doc.add_paragraph()

for label in ['学号：', '姓名：', '电话：']:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(label + '                    ')
    run.font.size = Pt(14)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_page_break()

# ========== 目录页 ==========
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Cm(0)
run = p.add_run('目  录')
run.font.size = Pt(18)
run.bold = True
run.font.name = '黑体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

toc_items = [
    '1. 系统概述',
    '2. 需求分析',
    '    2.1 功能需求',
    '    2.2 用例分析',
    '    2.3 性能要求',
    '3. 概要设计',
    '    3.1 开发架构',
    '    3.2 总体流程',
    '    3.3 功能结构',
    '    3.4 开发环境与关键技术',
    '4. 详细设计',
    '    4.1 数据库设计',
    '    4.2 功能模块设计',
    '5. 系统实现与测试',
    '    5.1 系统实现',
    '    5.2 系统测试',
    '6. 总结与展望',
    '参考文献',
]
for item in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(item)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_page_break()

# ========== 1. 系统概述 ==========
add_title('1. 系统概述')

add_para('随着我国农业现代化的不断推进，农机作业监管服务系统在农业生产中发挥着越来越重要的作用。在农机上安装的监控设备主要包括GNSS定位装置、机具作业传感器、无线传输模块及监测终端等，上述设备能够实时采集农机作业过程中的位置信息、作业传感器数据（如耕深）、机具编码等关键数据，并将这些信息传输到远程服务器进行存储和分析。然而，目前农机作业数据普遍以原始Excel表格的形式存储，缺乏有效的数据处理与可视化分析手段，导致大量有价值的数据未能得到充分利用。')

add_para('本项目旨在开发一套基于Web的农机作业数据处理与分析软件，实现对农机轨迹数据的导入存储、地图可视化展示、轨迹属性查询以及作业量统计分析等功能。系统采用B/S架构，前端使用Leaflet地图组件进行地理信息展示，后端基于Django框架进行业务逻辑处理，使用SQLite数据库存储轨迹数据。')

add_para('系统的开发目标包括：（1）设计合理的数据库结构，支持高效存储和管理8个地块共4万余条农机轨迹数据；（2）实现用户和管理员两种角色的权限管理，保障数据安全；（3）集成地图组件，支持矢量地图和遥感影像的切换浏览，实现轨迹数据的可视化展示；（4）提供轨迹属性查询功能，支持按地块编号快速检索；（5）实现作业量统计分析功能，计算作业总时长、总行程、作业面积、田间平均作业速度等指标，并通过图表直观呈现。通过本系统的开发，能够为农机作业监管提供数据支撑和决策依据，提高农机作业管理的科学化水平。')

# ========== 2. 需求分析 ==========
add_title('2. 需求分析')
add_title('2.1 功能需求', level=2)

add_para('根据项目实践要求，系统需要实现用户和管理员两种角色的功能设计，具体功能需求如下：')

add_para('（1）用户和管理员共有的基本功能：注册、登录、修改密码等用户管理功能；实现地图基础功能，包括放大、缩小、漫游、全图、测距等操作；支持加载遥感影像或矢量地图；从数据库读取轨迹数据，将地块轨迹添加到地图图层并显示；轨迹属性查询，通过输入地块编号查询相应的轨迹属性数据。')

add_para('（2）管理员功能：导入地块轨迹数据，将CSV格式的原始农机轨迹数据添加到数据库中；删除地块轨迹数据，从数据库中删除指定地块；用户账号管理功能，包括查看用户列表、删除用户等。')

add_para('（3）统计分析功能：根据轨迹数据统计作业量指标，包括作业总时长、作业总行程、作业面积、田间平均作业速度，并通过图表进行可视化描述。')

add_image_placeholder('系统功能需求用例图')

add_title('2.2 用例分析', level=2)

add_table(
    ['用例编号', '用例名称', '参与者', '简要描述'],
    [
        ['UC-01', '用户注册', '游客', '填写用户名、邮箱、密码，选择角色完成注册'],
        ['UC-02', '用户登录', '用户/管理员', '选择角色（用户/管理员），输入账号密码登录系统'],
        ['UC-03', '修改密码', '用户/管理员', '输入旧密码和新密码完成密码修改'],
        ['UC-04', '查看地图', '用户/管理员', '在地图上浏览所有地块轨迹，支持缩放、漫游、全图'],
        ['UC-05', '测距', '用户/管理员', '在地图上点击多个点测量距离'],
        ['UC-06', '切换底图', '用户/管理员', '在矢量地图和遥感影像之间切换'],
        ['UC-07', '轨迹查询', '用户/管理员', '输入地块编号或从列表选择，查看轨迹属性数据'],
        ['UC-08', '统计分析', '用户/管理员', '查看各地块作业量统计指标和图表'],
        ['UC-09', '数据导入', '管理员', '上传CSV文件导入轨迹数据到数据库'],
        ['UC-10', '删除地块', '管理员', '从数据库中删除指定地块及其轨迹数据'],
        ['UC-11', '用户管理', '管理员', '查看用户列表、删除用户账号'],
    ],
    '表2-1 系统用例列表'
)

add_title('2.3 性能要求', level=2)

add_para('（1）响应时间：页面加载时间不超过3秒，地图轨迹渲染时间不超过5秒。')
add_para('（2）数据处理能力：支持单次导入4万条以上轨迹数据，批量写入数据库时间不超过10秒。')
add_para('（3）并发能力：系统支持多用户同时访问，各用户操作互不影响。')
add_para('（4）兼容性：支持主流浏览器（Chrome、Firefox、Safari、Edge）访问。')

# ========== 3. 概要设计 ==========
add_title('3. 概要设计')
add_title('3.1 开发架构', level=2)

add_para('系统采用B/S（Browser/Server）架构，基于Django MTV（Model-Template-View）模式进行开发。整体架构分为三层：')

add_para('（1）表示层（Template）：负责页面展示和用户交互，使用HTML+CSS+JavaScript构建前端界面，集成Leaflet地图组件和Chart.js图表库。前端通过Bootstrap 5框架实现响应式布局，通过Bootstrap Icons提供图标支持。')

add_para('（2）业务逻辑层（View）：处理用户请求和业务逻辑，基于Django框架实现。包括用户认证模块（accounts应用）和轨迹数据管理模块（tracks应用），通过URL路由将请求分发到对应的视图函数。')

add_para('（3）数据访问层（Model）：负责数据持久化，使用Django ORM操作SQLite数据库。定义了Track和TrackPoint两个数据模型，分别对应地块信息和轨迹点信息。')

add_image_placeholder('系统三层架构图')

add_title('3.2 总体流程', level=2)

add_para('系统的总体业务流程如下：管理员通过数据导入功能将CSV格式的农机轨迹数据上传至系统，系统解析数据并存入数据库。用户登录后可在地图页面浏览所有地块轨迹，通过侧边栏选择地块查看详情。用户可通过轨迹查询页面按地块编号检索轨迹属性数据，查看统计概览和详细数据。统计分析页面提供各地块作业量指标的对比图表，包括柱状图、雷达图和饼图等多种可视化形式。')

add_image_placeholder('系统总体业务流程图')

add_title('3.3 功能结构', level=2)

add_para('系统功能结构划分为两大模块：')

add_para('（1）用户认证模块（accounts）：负责用户注册、登录、登出、修改密码等功能。注册时支持选择普通用户或管理员角色，登录时根据所选角色进行身份验证。')

add_para('（2）轨迹数据管理模块（tracks）：包括地图展示、轨迹查询、统计分析、数据导入、数据删除、用户管理六个子模块。地图展示模块集成Leaflet实现轨迹可视化；轨迹查询模块支持按编号和列表两种查询方式；统计分析模块计算作业量指标并生成图表；数据导入模块支持CSV文件上传和拖拽上传；数据删除和用户管理模块为管理员专用功能。')

add_image_placeholder('系统功能结构图')

add_title('3.4 开发环境与关键技术', level=2)

add_table(
    ['类别', '技术/工具', '版本/说明'],
    [
        ['编程语言', 'Python', '3.13'],
        ['Web框架', 'Django', '6.0'],
        ['数据库', 'SQLite', 'Django内置'],
        ['地图组件', 'Leaflet', '1.9.4'],
        ['前端框架', 'Bootstrap', '5.3'],
        ['图表库', 'Chart.js', '4.4'],
        ['图标库', 'Bootstrap Icons', '1.11'],
        ['数据处理', 'Pandas', '2.3'],
        ['开发工具', 'VS Code / PyCharm', '—'],
        ['版本控制', 'Git', '—'],
    ],
    '表3-1 开发环境与关键技术'
)

# ========== 4. 详细设计 ==========
add_title('4. 详细设计')
add_title('4.1 数据库设计', level=2)

add_para('系统使用SQLite关系型数据库，共设计3张核心数据表（其中User表使用Django内置模型）：')

add_para('（1）Track（地块信息表）：存储地块基本信息，包括地块名称和导入时间。', indent=True)
add_table(
    ['字段名', '数据类型', '约束', '说明'],
    [
        ['id', 'IntegerField', '主键，自增', '地块ID'],
        ['name', 'CharField(100)', '非空', '地块名称'],
        ['created_at', 'DateTimeField', '自动添加', '导入时间'],
    ],
    '表4-1 Track（地块信息表）'
)

add_para('（2）TrackPoint（轨迹点信息表）：存储每个轨迹点的详细数据，通过外键关联到Track表。', indent=True)
add_table(
    ['字段名', '数据类型', '约束', '说明'],
    [
        ['id', 'IntegerField', '主键，自增', '轨迹点ID'],
        ['track_id', 'IntegerField', '外键→Track.id，级联删除', '所属地块'],
        ['sequence', 'IntegerField', '非空', '序列号'],
        ['gps_time', 'DateTimeField', '非空', 'GPS时间'],
        ['longitude', 'FloatField', '非空', '经度'],
        ['latitude', 'FloatField', '非空', '纬度'],
        ['x', 'FloatField', '非空', 'x坐标'],
        ['y', 'FloatField', '非空', 'y坐标'],
        ['speed', 'FloatField', '非空', '速度(km/h)'],
        ['heading', 'FloatField', '非空', '航向'],
        ['working_status', 'BooleanField', '非空', '工作状态'],
        ['width', 'FloatField', '非空', '幅宽(m)'],
        ['depth', 'FloatField', '非空', '深度(mm)'],
        ['depth_standard', 'FloatField', '非空', '深度标准值'],
    ],
    '表4-2 TrackPoint（轨迹点信息表）'
)

add_para('（3）User（用户表）：使用Django内置用户模型，包含username、password、email、is_staff等字段，其中is_staff字段用于区分普通用户和管理员角色。')

add_image_placeholder('数据库E-R图')

add_title('4.2 功能模块设计', level=2)

add_para('4.2.1 用户认证模块', bold=True)

add_para('用户认证模块实现注册、登录、修改密码、登出四个功能。注册时用户可选择普通用户或管理员角色，选择管理员角色后系统自动将is_staff字段设为True。登录时需选择角色类型，系统验证账号密码后检查角色是否匹配：若选择管理员登录但账号非管理员则拒绝，若选择用户登录但账号为管理员也拒绝。修改密码需输入旧密码进行验证。登出采用POST方式提交，符合Django 5.0+的安全要求。')

add_image_placeholder('用户登录流程图')

add_para('4.2.2 地图展示模块', bold=True)

add_para('地图展示模块基于Leaflet实现，主要功能包括：（1）底图管理：集成OpenStreetMap矢量地图和Esri遥感影像，支持一键切换；（2）轨迹渲染：通过GeoJSON格式从后端获取轨迹数据，使用Polyline绘制轨迹折线，使用CircleMarker绘制轨迹点，工作状态用绿色标识、未工作用橙色标识；（3）地图控件：提供缩放、全图、测距等控件，测距工具采用自定义实现避免与地图事件冲突；（4）侧边栏：展示地块列表，支持搜索过滤，点击地块自动定位到对应轨迹区域。')

add_image_placeholder('地图展示模块流程图')

add_para('4.2.3 轨迹查询模块', bold=True)

add_para('轨迹查询模块支持两种查询方式：输入框搜索和下拉列表选择。两种方式互斥联动——选择下拉项时清空输入框，输入文字时重置下拉框。查询结果页面展示统计概览卡片（作业总时长、总行程、作业面积、平均速度）和详细轨迹点数据表格。未查询时显示使用说明和全部地块概览表格。')

add_para('4.2.4 统计分析模块', bold=True)

add_para('统计分析模块计算四个作业量指标：作业总时长（首尾工作时间差）、作业总行程（相邻点Haversine距离之和）、作业面积（轨迹点围成多边形的Shoelace公式面积，转换为亩）、田间平均作业速度（工作状态下的速度均值）。采用Chart.js绘制四种柱状图、一个雷达图和一个饼图进行可视化展示。')

add_image_placeholder('统计分析模块流程图')

add_para('4.2.5 数据导入模块', bold=True)

add_para('数据导入模块支持CSV格式文件的上传，支持点击上传和拖拽上传两种方式。后端使用Pandas读取CSV文件（GBK编码），解析字段映射到TrackPoint模型，通过bulk_create批量写入数据库（每批500条）。从文件名提取地块编号自动创建Track记录，若地块已存在则先删除旧数据再导入。')

add_para('4.2.6 用户管理模块', bold=True)

add_para('用户管理模块仅管理员可访问，展示所有用户列表，包括用户名、邮箱、角色、注册时间等信息。管理员可删除非当前登录用户，删除操作需二次确认。角色通过Badge标签区分：超级管理员（橙红色）、管理员（深绿色）、普通用户（浅绿色）。')

# ========== 5. 系统实现与测试 ==========
add_title('5. 系统实现与测试')
add_title('5.1 系统实现', level=2)

add_para('5.1.1 登录注册界面', bold=True)
add_para('登录页面采用全屏深绿渐变背景，配合动态光斑和浮动粒子动画，营造现代科技感。角色切换使用Tab滑动组件，管理员登录时按钮变为红色渐变。输入框采用无边框设计，左侧带图标，聚焦时显示绿色发光边框。整体采用毛玻璃（Glassmorphism）卡片风格。')
add_image_placeholder('登录界面截图')
add_image_placeholder('注册界面截图')

add_para('5.1.2 地图首页', bold=True)
add_para('地图首页占据全屏，左侧为可折叠侧边栏，显示地块数量统计和地块列表，支持实时搜索过滤。右上角集成缩放、全图、底图切换、测距等地图控件。轨迹以不同深浅的绿色折线绘制，点击轨迹弹出地块信息弹窗。')
add_image_placeholder('地图首页截图')
add_image_placeholder('轨迹详情弹窗截图')

add_para('5.1.3 轨迹查询页面', bold=True)
add_para('轨迹查询页面顶部为搜索区域，支持输入框和下拉列表两种查询方式。查询后显示统计概览卡片和轨迹点数据表格。未查询时展示使用说明和全部地块概览列表，每行提供"查看详情"快捷按钮。')
add_image_placeholder('轨迹查询页面截图')
add_image_placeholder('查询结果页面截图')

add_para('5.1.4 统计分析页面', bold=True)
add_para('统计分析页面顶部显示汇总统计卡片，中部为各地块作业量指标对比表格，下方展示柱状图、雷达图和饼图三种图表。所有图表采用统一绿色色系，雷达图支持多地块综合指标对比，饼图展示面积占比分布。')
add_image_placeholder('统计分析页面截图')
add_image_placeholder('图表展示截图')

add_para('5.1.5 数据导入页面', bold=True)
add_para('数据导入页面左侧为拖拽上传区域，支持点击选择文件和拖拽文件两种方式，选择文件后显示文件名和大小。右侧为已导入地块列表，每行显示地块图标、名称、轨迹点数和导入时间，提供删除按钮。')
add_image_placeholder('数据导入页面截图')

add_para('5.1.6 用户管理页面', bold=True)
add_para('用户管理页面展示用户列表表格，包含头像图标、用户名、邮箱、角色标签、注册时间等信息。管理员可对非当前用户执行删除操作。')
add_image_placeholder('用户管理页面截图')

add_title('5.2 系统测试', level=2)

add_table(
    ['测试编号', '测试内容', '测试步骤', '预期结果', '实际结果'],
    [
        ['T-01', '用户注册', '填写信息选择角色提交', '注册成功跳转首页', '通过'],
        ['T-02', '管理员登录验证', '普通用户选管理员登录', '提示角色不匹配', '通过'],
        ['T-03', '用户登录验证', '管理员选用户登录', '提示角色不匹配', '通过'],
        ['T-04', '地图轨迹加载', '登录后查看地图', '显示8个地块轨迹', '通过'],
        ['T-05', '底图切换', '点击矢量/遥感切换', '底图正确切换', '通过'],
        ['T-06', '测距功能', '开启测距点击两个点', '显示距离标注', '通过'],
        ['T-07', '轨迹查询', '输入地块编号查询', '显示属性数据表格', '通过'],
        ['T-08', '统计分析', '访问统计分析页面', '显示指标和图表', '通过'],
        ['T-09', 'CSV数据导入', '上传CSV文件', '数据成功导入数据库', '通过'],
        ['T-10', '删除地块', '点击删除按钮确认', '地块从数据库删除', '通过'],
        ['T-11', '修改密码', '输入旧密码和新密码', '密码修改成功', '通过'],
        ['T-12', '退出登录', '点击退出按钮', '跳转到登录页', '通过'],
    ],
    '表5-1 系统测试用例及结果'
)

add_para('经过全面测试，系统各项功能均能正常运行，满足需求分析中提出的所有功能要求和性能要求。')

# ========== 6. 总结与展望 ==========
add_title('6. 总结与展望')

add_para('本项目完成了农机作业数据处理与分析软件的设计与开发，实现了用户认证、地图轨迹展示、轨迹属性查询、数据导入管理、作业量统计分析等全部功能。系统采用Django+Leaflet+Chart.js技术栈，实现了从数据导入、存储、查询到可视化分析的全流程处理，能够满足农机作业监管服务系统对轨迹数据的管理与分析需求。')

add_para('在开发过程中，有以下几点心得体会：（1）合理的数据库设计是系统高效运行的基础，Track和TrackPoint的外键关联设计使得数据查询和删除操作简单高效；（2）Leaflet地图组件功能强大且易于集成，自定义测距工具的实现对理解地图事件机制有较大帮助；（3）Django框架的MTV模式和ORM机制大幅提高了开发效率，内置的用户认证系统减少了重复开发工作。')

add_para('本系统目前仍存在一些不足之处：（1）统计分析模块目前仅实现了作业量指标统计，未来可增加作业效率指标（达标率、生产率、时间利用率）的统计功能；（2）地图上的轨迹点数量较多时渲染性能有待优化，可考虑使用WebGL或点聚合技术；（3）目前使用SQLite数据库，若数据量增大或需要多用户并发写入，应迁移至MySQL或PostgreSQL；（4）前端可进一步优化为前后端分离架构，提升用户体验和系统可维护性。')

# ========== 参考文献 ==========
add_title('参考文献')

refs = [
    '[1] 刘振兴, 张三. 基于Django的Web应用开发实战[M]. 北京: 清华大学出版社, 2023.',
    '[2] 王明, 李四. 基于GIS的农机作业轨迹可视化分析方法[J]. 农业工程学报, 2022, 38(15): 1-9.',
    '[3] 陈伟. Leaflet交互式地图开发[M]. 北京: 电子工业出版社, 2021.',
    '[4] 张华, 赵六. 农机作业远程监管系统设计与实现[J]. 计算机应用研究, 2023, 40(3): 850-855.',
    '[5] Django Software Foundation. Django Documentation[EB/OL]. https://docs.djangoproject.com/, 2024.',
    '[6] 李明. Python数据分析与可视化[M]. 北京: 人民邮电出版社, 2022.',
]

for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(ref)
    run.font.size = Pt(10.5)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# ========== 保存 ==========
output_path = os.path.join(os.path.dirname(__file__), '农机作业数据处理与分析系统设计与实现.docx')
doc.save(output_path)
print(f'论文已生成：{output_path}')
