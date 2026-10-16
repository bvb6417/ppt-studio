"""Smoke test / starting point: a 10-page NSFC-style deck with placeholders (no images needed).

    python examples/quickstart.py [out.pptx]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'scripts'))
from pptstudio import Deck  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith('.pptx') else \
    os.path.join(HERE, 'quickstart_out', '项目答辩示例.pptx')

d = Deck('nsfc_blue')                      # 科研答辩风; try 'nsfc_red', '#660874' + style='defense', or 'business_blue'
d.meta(title='复杂系统XXX机理与调控方法研究', author='XXX', unit='XXX大学 XXX学院', lab='XXX重点实验室',
       project='国家自然科学基金面上项目 答辩')
d.set_sections(['立项依据', '研究方案', '创新与基础'])

d.cover()
d.agenda()
d.section(1)
d.panels('国家重大需求', statement='XXX领域面临[[“卡脖子”]]难题，亟需突破[[关键科学问题]]',
         panels=[{'header': '需求一', 'chart': {'kind': 'column', 'categories': ['2022', '2023', '2024', '2025'],
                                             'series': {'市场规模(亿元)': [120, 168, 230, 310]}, 'highlight': -1}},
                 {'header': '需求二', 'placeholder': '图：替换为你的图片', 'caption': '图1 XXX示意',
                  'points': ['要点一，[[关键词]]', '要点二']}],
         conclusion='一句话结论：本项目瞄准XXX核心难题', conclusion_style='yellow', source='数据来源：示例数据')
d.problems('关键科学问题', lead='拟解决两大[[关键科学问题]]', items=[
    {'label': '问题一', 'question': '如何揭示XXX的[[演化机理]]？', 'placeholder': '图', 'caption': '图2 示意',
     'tag': '研究目标', 'points': ['目标一，[[关键词]]', '目标二']},
    {'label': '问题二', 'question': '如何实现XXX的[[精准调控]]？', 'placeholder': '图', 'caption': '图3 示意',
     'tag': '研究目标', 'points': ['目标一', '目标二']}])
d.section(2)
d.route('技术路线', target='[[科学目标：]]揭示XXX机理，构建XXX方法', top='课题3：系统集成与示范（集成）',
        labels=('机理揭示', '方法构建'),
        questions=[{'title': '关键科学问题二', 'focus': 'XXX调控'}, {'title': '关键科学问题一', 'focus': 'XXX机理'}],
        topics=[['课题2：XXX方法[[（调控）]]'], ['课题1：XXX机理[[（机理）]]']])
d.section(3)
d.innovations('特色与创新', subtitle='从“单一环节”到“系统协同”', items=[
    {'tag': '理论创新', 'text': '建立XXX[[多场耦合]]理论模型'}, {'tag': '方法创新', 'text': '提出[[物理+数据]]融合方法'},
    {'tag': '应用创新', 'text': '构建XXX[[一体化平台]]'}], footer='为XXX提供[[理论支撑]]')
d.schedule('研究计划', periods=['2026', '2027', '2028'], sub_periods=['上半年', '下半年'], tasks=[
    {'name': '研究内容一', 'desc': '机理研究', 'span': (0, 3), 'label': '理论与试验'},
    {'name': '研究内容二', 'desc': '方法构建', 'span': (2, 5), 'label': '算法开发'},
    {'name': '研究内容三', 'desc': '示范应用', 'span': (4, 6), 'label': '工程验证'}])
d.ending()
print(d.save(out, render='--no-render' not in sys.argv))
