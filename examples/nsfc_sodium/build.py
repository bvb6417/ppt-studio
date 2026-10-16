"""示例：国家自然科学基金面上项目 申请答辩（科研答辩风 · 亮蓝白皮肤）。

虚构项目“高倍率钠离子电池硬碳负极的储钠机理与孔结构调控”，16 页，几乎全部直接调用 skill 版式：
cover / agenda / section / panels / bands / problems / band_cards / process_matrix / figure_text / versus /
schedule / innovations / ending。所有数据均为示例数据，图为 matplotlib 示意图（make_figs.py）。

Run:  python make_figs.py        (figs/*.png)
      python build.py            -> out/国自然申请答辩_示例.pptx + out/国自然申请答辩_示例_preview/
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts'))
from pptstudio import Deck                          # noqa: E402

FIG = lambda n: os.path.join(HERE, 'figs', n)       # noqa: E731
OUT = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith('.pptx') else \
    os.path.join(HERE, 'out', '国自然申请答辩_示例.pptx')
NOTE = '注：示例项目与示例数据，仅用于版式演示'

if not os.path.exists(FIG('cover_art.png')):
    import make_figs                                 # noqa: F401
    for f in (make_figs.mechanism, make_figs.gcd, make_figs.cycle, make_figs.pore, make_figs.dft, make_figs.insitu,
              make_figs.cover_art):
        f()

d = Deck('bright_blue', skin='bright')
d.meta(title='高倍率钠离子电池硬碳负极的\n储钠机理与孔结构调控', author='张三',
       unit='示例大学 材料科学与工程学院', lab='示例省 新能源材料重点实验室',
       project='国家自然科学基金面上项目 · 申请答辩（示例）', date='2026年10月')
d.set_sections(['立项依据', '研究内容与方案', '研究基础与创新'])

# ------------------------------------------------------------------ 封面 / 目录
d.cover(image=FIG('cover_art.png'), notes='开场：一句话说明项目要解决什么问题——硬碳负极“容量、倍率、首效”难以兼顾。')
d.agenda(descs=['国家需求、研究现状与关键科学问题', '研究目标、研究内容与技术路线', '前期基础、研究计划与特色创新'])

# ------------------------------------------------------------------ 1 立项依据
d.section(1, variant='number', desc=['新型储能对负极材料的需求', '硬碳储钠机理的研究现状与不足', '两个关键科学问题'])
d.panels('国家重大需求',
         statement='新型储能规模化发展亟需[[低成本、高安全]]电池，钠资源丰富、分布广，钠离子电池是锂电的重要补充',
         panels=[{'header': '新型储能需求快速增长',
                  'chart': {'kind': 'column', 'categories': ['2022', '2023', '2024', '2025', '2026'],
                            'series': {'新增储能装机（GWh，示例）': [16, 35, 62, 98, 140]}, 'highlight': -1,
                            'number_format': '0', 'gap': 80},
                  'image_h': 0.62,
                  'points': ['储能装机年均增速超过 [[60%]]', '对电池[[成本与安全性]]提出更高要求']},
                 {'header': '钠电瓶颈在于负极',
                  'table': {'columns': ['负极材料', '储钠容量', '主要问题'],
                            'rows': [['石墨', '≈35 mAh/g', '钠几乎无法嵌入'], ['软碳', '≈200 mAh/g', '容量偏低'],
                                     ['硬碳', '≈300 mAh/g', '[[倍率与首效不足]]']]},
                  'stats': [{'value': '≈300', 'unit': 'mAh/g', 'label': '硬碳可逆容量'},
                            {'value': '<80', 'unit': '%', 'label': '首圈库伦效率'},
                            {'value': '<50', 'unit': '%', 'label': '2 C 容量保持率'}]}],
         conclusion='根源在于硬碳储钠机理不清、闭孔结构难以定向调控', conclusion_style='yellow',
         source=NOTE, notes='两条线：储能需求（为什么要做钠电）+ 负极瓶颈（为什么要做硬碳）。')

d.bands('国内外研究现状', bands=[
    {'word': '国外', 'label': '储钠机理研究', 'cols': [
        {'title': '“嵌入—吸附”模型', 'points': ['斜坡区对应层间嵌入', '平台区对应微孔吸附']},
        {'title': '“吸附—嵌入—填孔”模型', 'points': ['斜坡区对应缺陷吸附', '平台区对应[[闭孔填充]]']}]},
    {'word': '国内', 'label': '材料结构调控', 'cols': [
        {'title': '前驱体与碳化工艺', 'points': ['生物质、树脂、沥青等前驱体', '高温碳化提升平台容量']},
        {'title': '孔结构工程', 'points': ['造孔剂与模板法构筑闭孔', '孔径与孔入口[[难以精准控制]]']}]}],
    conclusion='不足：平台区储钠位点与闭孔结构的[[定量关系]]尚未建立，孔结构“可设计”程度低',
    source=NOTE)

d.problems('关键科学问题', lead='项目拟解决两个[[关键科学问题]]', items=[
    {'label': '问题一', 'question': '平台区的钠以何种形态储存于闭孔之中？', 'image': FIG('insitu.png'),
     'caption': '图1 原位 XRD（示意）', 'tag': '研究目标',
     'points': ['阐明“吸附—嵌入—填孔”[[序贯储钠]]机制', '确定准金属钠团簇的[[形成条件]]',
                '量化各储钠阶段的容量贡献']},
    {'label': '问题二', 'question': '闭孔结构如何决定平台容量与倍率性能？', 'image': FIG('pore.png'),
     'caption': '图2 闭孔体积—平台容量（示意）', 'tag': '研究目标',
     'points': ['建立[[闭孔体积—平台容量]]定量关系', '揭示孔入口尺寸对倍率性能的影响',
                '提出孔结构[[定向调控]]策略']}],
    notes='每个问题：一句问句 + 一张证据图 + 两条研究目标。')

# ------------------------------------------------------------------ 2 研究内容与方案
d.section(2, variant='number', desc=['研究目标与三项研究内容', '矩阵式技术路线', '储钠机理研究方案'])
d.band_cards('研究目标与研究内容',
             headline='揭示硬碳[[闭孔储钠]]机理，建立“孔结构—储钠—性能”构效关系',
             text='围绕“看清机理、调准结构、做出器件”三个环节，设置三项相互衔接的研究内容。',
             kpis=[{'value': '350', 'unit': 'mAh/g', 'label': '可逆容量目标'},
                   {'value': '90', 'unit': '%', 'label': '首圈库伦效率'}],
             cards=[{'title': '研究内容一', 'icon': 'microscope', 'tag': '机理',
                     'points': ['原位表征储钠全过程', '缺陷位点[[吸附能]]计算', '三段储钠模型构建']},
                    {'title': '研究内容二', 'icon': 'layers', 'tag': '结构',
                     'points': ['前驱体交联度调控', '闭孔尺寸与入口构筑', '[[孔结构—容量]]构效关系']},
                    {'title': '研究内容三', 'icon': 'battery-charging', 'tag': '器件',
                     'points': ['高倍率电极设计', '软包电池验证', '低温与[[长循环]]评价']}],
             notes='拦腰版式：色带写总目标 + 两个量化指标，三张卡片对应三项研究内容。')

d.process_matrix('技术路线', steps=['材料制备', '结构表征', '机理解析', '构效关系', '器件验证'],
                 rows=['机理', '结构', '器件'],
                 phases=[('基础研究', 0, 2), ('应用验证', 3, 4)],
                 cells=[[{'title': '梯度闭孔样品', 'text': '闭孔体积 0.03–0.14\ncm³/g 系列'},
                         {'title': '原位 XRD / Raman', 'text': '层间距与 D/G 峰\n随电位演化'},
                         {'title': '三段储钠模型', 'text': '吸附—嵌入—填孔\n序贯机制'},
                         {'title': '容量贡献拆分', 'text': '斜坡区 / 平台区\n定量归属'}, None],
                        [{'title': '前驱体调控', 'text': '交联度 / 碳化温度\n双变量设计'},
                         {'title': 'SAXS / 气体吸附', 'text': '闭孔体积与\n孔入口尺寸'},
                         {'title': 'DFT 计算', 'text': '缺陷位点\n钠吸附能'},
                         {'title': '构效关系', 'text': '闭孔体积—\n平台容量'}, None],
                        [None, None, None, {'title': '电极设计', 'text': '孔道、粒径与\n压实密度'},
                         {'title': '软包电池', 'text': '1 Ah 级\n低温与长循环'}]],
                 arrows=[(0, 0, 0, 1), (0, 1, 0, 2), (0, 2, 0, 3), (1, 0, 1, 1), (1, 1, 1, 2), (1, 2, 1, 3),
                         (1, 3, 2, 3), (2, 3, 2, 4)],
                 notes_row=['结构可控', '孔隙可测', '机理清楚', '规律可用', '性能达标'],
                 notes='矩阵式技术路线：横向是研究步骤，纵向是机理/结构/器件三条线，箭头表示数据流向。')

d.figure_text('储钠机理研究方案', image=FIG('mechanism.png'), caption='图3 硬碳“吸附—嵌入—填孔”储钠机理（示意）',
              statement='以[[原位表征 + 第一性原理计算]]联合解析三段储钠过程',
              blocks=[{'tag': '原位\n表征', 'title': '原位 XRD / Raman',
                       'text': '追踪 (002) 晶面间距与 D/G 峰随电位的[[演化规律]]'},
                      {'tag': '理论\n计算', 'title': '缺陷位点吸附能',
                       'text': '计算空位、N/O 掺杂位点的钠[[吸附能]]分布'},
                      {'tag': '模型\n构建', 'title': '三段储钠模型',
                       'text': '定量划分[[斜坡区与平台区]]的容量贡献'}],
              frac=0.55)

# ------------------------------------------------------------------ 3 研究基础与创新
d.section(3, variant='number', desc=['前期研究基础与性能对比', '研究计划与进度安排', '特色与创新'])
d.panels('前期研究基础',
         statement='申请人已制备系列硬碳材料，初步实现[[平台容量]]与[[循环寿命]]同步提升',
         panels=[{'header': '充放电曲线', 'image': FIG('gcd.png'), 'caption': '图4 HC-3 恒流充放电曲线（示意）',
                  'points': ['平台容量占比达 [[66%]]']},
                 {'header': '循环稳定性', 'image': FIG('cycle.png'), 'caption': '图5 2 C 循环 1000 次（示意）',
                  'points': ['容量保持率 [[92.6%]]']},
                 {'header': '吸附能计算', 'image': FIG('dft.png'), 'caption': '图6 缺陷位点钠吸附能（示意）',
                  'points': ['空位吸附能最低 [[−1.15 eV]]']}],
         conclusion='前期工作验证了“闭孔调控提升平台容量”的技术思路，项目具备良好实施基础',
         source=NOTE)

d.versus('与商业硬碳的性能对比', statement='HC-3 在[[可逆容量]]与[[倍率性能]]上明显优于商业硬碳（示例数据）',
         ours={'name': 'HC-3（本项目）', 'sub': '闭孔定向调控', 'badge': '综合最优',
               'rows': [('可逆容量', '372 mAh/g'), ('首圈库伦效率', '88.5%'), ('2 C 容量保持', '81%'),
                        ('1000 次循环保持率', '92.6%')]},
         others=[{'name': '商业硬碳 A', 'sub': '生物质前驱体',
                  'rows': [('可逆容量', '305 mAh/g'), ('首圈库伦效率', '82.0%'), ('2 C 容量保持', '52%'),
                           ('1000 次循环保持率', '74.3%')]},
                 {'name': '商业硬碳 B', 'sub': '树脂前驱体',
                  'rows': [('可逆容量', '326 mAh/g'), ('首圈库伦效率', '84.6%'), ('2 C 容量保持', '47%'),
                           ('1000 次循环保持率', '68.9%')]}],
         source=NOTE)

d.schedule('研究计划与进度安排', periods=['2027', '2028', '2029', '2030'], sub_periods=['上半年', '下半年'], tasks=[
    {'name': '研究内容一', 'desc': '储钠机理', 'span': (0, 4), 'label': '原位表征与吸附能计算'},
    {'name': '研究内容二', 'desc': '孔结构调控', 'span': (1, 6), 'label': '闭孔构筑与构效关系'},
    {'name': '研究内容三', 'desc': '器件验证', 'span': (4, 8), 'label': '电极设计与软包电池验证'},
    {'name': '总结与验收', 'desc': '成果凝练', 'span': (6, 8), 'label': '论文、专利与结题'}],
    statement='三项研究内容[[循序推进、相互衔接]]，2030 年完成软包电池验证')

d.innovations('特色与创新', subtitle='从“经验试错”到“机理指导”的硬碳负极设计', items=[
    {'tag': '机理创新', 'text': '提出“吸附—嵌入—填孔”[[序贯储钠]]机制，定量区分斜坡区与平台区的容量来源'},
    {'tag': '方法创新', 'text': '建立[[闭孔体积—平台容量]]定量关系，实现孔结构的可设计、可预测'},
    {'tag': '技术创新', 'text': '发展交联度调控的闭孔定向构筑方法，兼顾[[高容量与高倍率]]'}],
    footer='为高比能、低成本钠离子电池负极提供[[理论依据]]与材料方案',
    image=FIG('mechanism.png'), caption='图7 三段储钠机理（示意）')

d.ending()

if __name__ == '__main__':
    path = d.save(OUT, render='--no-render' not in sys.argv)
    print('saved', path)
