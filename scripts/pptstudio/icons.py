"""Lucide icons (ISC license, 1,850+ stroke icons) -> native PowerPoint vector shapes.

Usage: icons.find('水') -> ['droplet', ...];  canvas.icon('droplet', x, y, size, color)
"""
from __future__ import annotations

import json
import os
from functools import lru_cache

from .svgpath import node_to_subpaths

_ASSET = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets', 'icons',
                      'lucide.json')

# Chinese keyword -> lucide icon names (first = best). Covers research / business / engineering vocab.
ZH = {
    '水': ['droplet', 'droplets', 'waves-horizontal'], '水资源': ['droplets', 'droplet'], '输水': ['waves-horizontal', 'droplets'],
    '管道': ['cable', 'pipette', 'waypoints'], '水库': ['dam'], '大坝': ['dam'], '水利': ['dam', 'droplets'],
    '河流': ['waves-horizontal', 'waves-ladder'], '海洋': ['waves-horizontal', 'ship'], '雨': ['cloud-rain'], '天气': ['cloud-sun'],
    '水质': ['flask-conical', 'droplet'], '泵站': ['fan', 'gauge'], '压力': ['gauge'], '流量': ['activity', 'waves-horizontal'],
    '隧洞': ['circle-dot', 'mountain'], '地质': ['mountain', 'layers'], '山': ['mountain', 'mountain-snow'],
    '冰': ['snowflake'], '温度': ['thermometer'], '能源': ['zap', 'battery-charging'], '电': ['zap', 'plug'],
    '太阳能': ['sun', 'solar-panel'], '风电': ['wind'], '环境': ['leaf', 'trees'], '生态': ['sprout', 'leaf'],
    '绿色': ['leaf', 'recycle'], '低碳': ['leaf', 'recycle'], '碳': ['factory', 'leaf'], '安全': ['shield-check', 'shield'],
    '风险': ['triangle-alert', 'shield-alert'], '预警': ['siren', 'bell-ring'], '监测': ['radar', 'activity', 'scan-eye'],
    '检测': ['scan-search', 'search'], '诊断': ['stethoscope', 'scan-search'], '传感器': ['radio', 'cpu'],
    '渗漏': ['droplets', 'scan-search'], '泄漏': ['droplets', 'triangle-alert'], '维护': ['wrench', 'hammer'],
    '工程': ['hard-hat', 'construction', 'building'], '施工': ['construction', 'hard-hat'], '建筑': ['building', 'landmark'],
    '结构': ['boxes', 'layers'], '材料': ['layers', 'package'], '设备': ['cpu', 'server'], '制造': ['factory', 'cog'],
    '工业': ['factory'], '交通': ['truck', 'train-front', 'car'], '物流': ['truck', 'package'], '城市': ['building', 'landmark'],
    '地图': ['map', 'map-pin'], '位置': ['map-pin'], '全球': ['globe', 'earth'], '国际': ['globe'], '国家': ['landmark', 'flag'],
    '政策': ['scroll-text', 'landmark'], '法规': ['scale', 'scroll-text'], '规划': ['map', 'compass', 'route'],
    '调度': ['git-branch', 'route', 'network'], '优化': ['sliders-horizontal', 'trending-up'], '控制': ['sliders-horizontal', 'gauge'],
    '智能': ['brain', 'bot', 'sparkles'], '人工智能': ['brain', 'bot'], 'AI': ['brain', 'bot', 'sparkles'],
    '算法': ['binary', 'brain-circuit', 'code'], '模型': ['box', 'boxes', 'brain-circuit'], '数据': ['database', 'chart-column'],
    '大数据': ['database', 'server'], '云': ['cloud'], '网络': ['network', 'wifi'], '数字孪生': ['copy', 'boxes'],
    '数字化': ['monitor', 'binary'], '信息化': ['monitor', 'network'], '平台': ['layout-dashboard', 'layers'],
    '系统': ['layout-dashboard', 'cpu'], '软件': ['app-window', 'code'], '代码': ['code'], '芯片': ['cpu'], '服务器': ['server'],
    '仿真': ['monitor-play', 'box'], '计算': ['calculator', 'cpu'], '实验': ['flask-conical', 'test-tube'], '研究': ['microscope', 'search'],
    '科研': ['microscope', 'flask-conical'], '论文': ['file-text', 'book-open'], '文献': ['book-open', 'library'],
    '理论': ['book-open', 'lightbulb'], '方法': ['wrench', 'workflow'], '技术': ['cpu', 'cog'], '创新': ['lightbulb', 'sparkles'],
    '想法': ['lightbulb'], '问题': ['circle-question-mark', 'triangle-alert'], '挑战': ['mountain', 'flag'], '难点': ['triangle-alert'],
    '目标': ['target', 'goal'], '任务': ['list-checks', 'clipboard-list'], '计划': ['calendar-check', 'clipboard-list'],
    '时间': ['clock', 'calendar'], '进度': ['loader', 'chart-gantt'], '里程碑': ['flag', 'milestone'], '阶段': ['milestone', 'layers'],
    '流程': ['workflow', 'git-branch'], '步骤': ['footprints', 'list-ordered'], '结果': ['circle-check', 'award'],
    '成果': ['award', 'trophy'], '奖项': ['trophy', 'award'], '荣誉': ['award', 'medal'], '专利': ['badge-check', 'file-badge'],
    '证书': ['file-badge', 'badge-check'], '质量': ['badge-check', 'gem'], '标准': ['ruler', 'badge-check'],
    '分析': ['chart-column', 'chart-pie', 'search'], '统计': ['chart-column'], '增长': ['trending-up', 'chart-line'],
    '下降': ['trending-down'], '趋势': ['chart-line', 'trending-up'], '对比': ['arrow-left-right', 'scale'], '比较': ['scale'],
    '市场': ['store', 'chart-pie'], '用户': ['users', 'user'], '客户': ['users', 'handshake'], '团队': ['users', 'user-round-check'],
    '人才': ['graduation-cap', 'user-star'], '教育': ['graduation-cap', 'school'], '学校': ['school', 'graduation-cap'],
    '教学': ['presentation', 'book-open'], '培训': ['presentation', 'graduation-cap'], '学生': ['graduation-cap', 'user'],
    '老师': ['user-round', 'presentation'], '合作': ['handshake'], '沟通': ['messages-square', 'message-circle'],
    '管理': ['clipboard-list', 'briefcase'], '商业': ['briefcase', 'store'], '财务': ['wallet', 'banknote'], '资金': ['banknote', 'coins'],
    '成本': ['coins', 'piggy-bank'], '收入': ['hand-coins', 'banknote'], '投资': ['chart-line', 'coins'], '价格': ['tag'],
    '产品': ['package', 'box'], '服务': ['headset', 'hand-helping'], '运营': ['settings', 'activity'], '推广': ['megaphone'],
    '品牌': ['star', 'badge'], '竞争': ['swords', 'trophy'], '优势': ['thumbs-up', 'star'], '机遇': ['sunrise', 'sparkles'],
    '前景': ['telescope', 'sunrise'], '未来': ['rocket', 'telescope'], '展望': ['telescope', 'eye'], '发展': ['trending-up', 'rocket'],
    '方向': ['compass', 'navigation'], '战略': ['chess-knight', 'compass'], '决策': ['git-branch', 'scale'], '健康': ['heart-pulse'],
    '医疗': ['stethoscope', 'hospital'], '生物': ['dna', 'microscope'], '基因': ['dna'], '化学': ['flask-conical', 'atom'],
    '物理': ['atom', 'magnet'], '数学': ['sigma', 'calculator'], '公式': ['sigma'], '图表': ['chart-column', 'chart-pie'],
    '文档': ['file-text'], '报告': ['file-chart-column', 'file-text'], '总结': ['clipboard-check', 'list-checks'],
    '结论': ['circle-check', 'flag'], '建议': ['message-square-text', 'lightbulb'], '会议': ['presentation', 'users'],
    '联系': ['phone', 'mail'], '邮箱': ['mail'], '电话': ['phone'], '网站': ['globe', 'link'], '二维码': ['qr-code'],
    '感谢': ['heart', 'face-slightly-smiling'], '问答': ['messages-square', 'circle-question-mark'], '开始': ['play', 'rocket'], '家': ['house'],
    '农业': ['wheat', 'sprout'], '食品': ['utensils', 'apple'], '汽车': ['car'], '火车': ['train-front'], '飞机': ['plane'],
    '船': ['ship'], '桥': ['bridge'], '道路': ['route', 'milestone'], '电池': ['battery-charging'], '光': ['sun', 'lightbulb'],
    '声音': ['volume-2', 'audio-waveform'], '振动': ['audio-waveform', 'activity'], '信号': ['radio', 'signal'],
    '光纤': ['cable', 'waypoints'], '无人机': ['drone'], '机器人': ['bot'], '相机': ['camera'], '视频': ['video'],
    '图片': ['image'], '设置': ['settings'], '工具': ['wrench', 'hammer'], '搜索': ['search'], '锁': ['lock'], '隐私': ['lock-keyhole'],
    '时钟': ['clock'], '日历': ['calendar'], '书': ['book-open'], '灯泡': ['lightbulb'], '火箭': ['rocket'], '奖杯': ['trophy'],
    '旗帜': ['flag'], '星': ['star'], '心': ['heart'], '检查': ['circle-check', 'list-checks'], '警告': ['triangle-alert'],
    '链接': ['link'], '分享': ['share-2'], '下载': ['download'], '上传': ['upload'], '循环': ['refresh-cw', 'repeat'],
    '层级': ['layers', 'network'], '组织': ['network', 'users'], '架构': ['network', 'boxes'], '模块': ['blocks', 'boxes'],
}


@lru_cache(maxsize=1)
def _data():
    with open(_ASSET, encoding='utf-8') as f:
        return json.load(f)


def exists(name: str) -> bool:
    return name in _data()


def names():
    return list(_data().keys())


def find(keyword: str, limit=8):
    """Search icons by Chinese keyword (ZH map) or English name/tag substring."""
    d = _data()
    out = []
    kw = keyword.strip()
    for k, v in ZH.items():
        if kw == k or (len(kw) >= 2 and kw in k) or (len(k) >= 2 and k in kw):
            out += [n for n in v if n in d]
    kl = kw.lower()
    for n, rec in d.items():
        if kl == n or kl in n.split('-'):
            out.append(n)
    for n, rec in d.items():
        if any(kl == t.lower() for t in rec['t']):
            out.append(n)
    for n, rec in d.items():
        if kl in n or any(kl in t.lower() for t in rec['t']):
            out.append(n)
    seen, res = set(), []
    for n in out:
        if n not in seen:
            seen.add(n); res.append(n)
    return res[:limit]


def resolve(name_or_kw: str) -> str:
    """Accept an exact lucide name, or a keyword (zh/en) -> best icon name. Falls back to 'circle-dot'."""
    if exists(name_or_kw):
        return name_or_kw
    r = find(name_or_kw, 1)
    return r[0] if r else 'circle-dot'


@lru_cache(maxsize=512)
def subpaths(name: str):
    """-> (list of subpath dicts, set of filled indices)"""
    rec = _data()[name]
    subs, filled = [], set()
    for tag, attrs in rec['n']:
        sp = node_to_subpaths(tag, attrs)
        if attrs.get('fill') and attrs.get('fill') != 'none':
            filled.update(range(len(subs), len(subs) + len(sp)))
        subs.extend(sp)
    return subs, frozenset(filled)
