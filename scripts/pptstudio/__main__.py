"""pptstudio command line.

  python -m pptstudio render  deck.pptx [--width 1600] [--slides 1,4,7]   PNG previews + contact sheet (PowerPoint)
  python -m pptstudio check   deck.pptx [--com]                           static QA (+ PowerPoint overflow check)
  python -m pptstudio fix     deck.pptx                                   shrink overflowing text (PowerPoint)
  python -m pptstudio pdf     deck.pptx                                   export PDF (PowerPoint)
  python -m pptstudio embed   deck.pptx                                   re-save with embedded fonts
  python -m pptstudio icons   水 / pipe / droplet                         search icon names
  python -m pptstudio fonts                                               installed font stacks
  python -m pptstudio themes                                              theme presets + 答辩风格家族 (skins)
  python -m pptstudio analyze ref.pptx [--json out.json]                  design DNA of a reference deck
  python -m pptstudio gallery [--style defense|modern] [--out gallery.pptx]  one page per layout
  python -m pptstudio gallery --style showcase --out <dir> [--sheets <dir>] [--skins a,b]  sample talk per skin
"""
from __future__ import annotations

import argparse
import json
import os
import sys


def main(argv=None):
    ap = argparse.ArgumentParser(prog='pptstudio')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('render'); p.add_argument('pptx'); p.add_argument('--width', type=int, default=1600)
    p.add_argument('--slides', default=None); p.add_argument('--out', default=None)
    p = sub.add_parser('check'); p.add_argument('pptx'); p.add_argument('--com', action='store_true')
    p = sub.add_parser('fix'); p.add_argument('pptx'); p.add_argument('--out', default=None)
    p = sub.add_parser('pdf'); p.add_argument('pptx')
    p = sub.add_parser('embed'); p.add_argument('pptx'); p.add_argument('--out', default=None)
    p = sub.add_parser('icons'); p.add_argument('keyword'); p.add_argument('--n', type=int, default=12)
    sub.add_parser('fonts')
    sub.add_parser('themes')
    p = sub.add_parser('analyze'); p.add_argument('pptx'); p.add_argument('--json', default=None)
    p = sub.add_parser('gallery'); p.add_argument('--style', default='defense'); p.add_argument('--out', default=None)
    p.add_argument('--theme', default=None); p.add_argument('--sheets', default=None, help='prefix for labeled sheets')
    p.add_argument('--skins', default=None, help='showcase only: comma-separated skin names (default: all)')
    a = ap.parse_args(argv)

    if a.cmd == 'render':
        from . import render as R
        slides = [int(x) for x in a.slides.split(',')] if a.slides else None
        out = a.out or os.path.splitext(os.path.abspath(a.pptx))[0] + '_preview'
        pngs = R.export_png(a.pptx, out, width=a.width, slides=slides)
        if not slides:
            print('contact sheet:', R.contact_sheet(pngs, os.path.join(out, 'contact_sheet.jpg')))
        for x in pngs:
            print(x)
    elif a.cmd == 'check':
        from . import qa
        rep = qa.check(a.pptx)
        print(qa.format_report(rep))
        if a.com:
            from . import render as R
            iss = R.check_overflow(a.pptx)
            print(f'PowerPoint overflow check: {len(iss)} issue(s)')
            for i in iss:
                print('  slide {slide:02d} {name}: text {text_h}x{text_w}pt in box {box_h}x{box_w}pt  "{text}"'.format(**i))
    elif a.cmd == 'fix':
        from . import render as R
        print('adjusted', R.fix_overflow(a.pptx, a.out), 'text boxes')
    elif a.cmd == 'pdf':
        from . import render as R
        print(R.to_pdf(a.pptx))
    elif a.cmd == 'embed':
        from . import render as R
        print(R.embed_fonts(a.pptx, a.out))
    elif a.cmd == 'icons':
        from . import icons
        print('\n'.join(icons.find(a.keyword, a.n)) or '(no match)')
    elif a.cmd == 'fonts':
        from . import fonts
        print(fonts.available_report())
    elif a.cmd == 'themes':
        from . import theme as TH
        for k, v in TH.PRESETS.items():
            print(f"{k:16s} style={v.get('style', 'modern'):8s} primary=#{v['primary']}  deep=#{v.get('deep', '') or '-'}"
                  f"  title_bar={v.get('extras', {}).get('title_bar', '-')}")
        print('\nskins (defense page-chrome families, Deck(theme, skin=...)):')
        for k, v in TH.SKINS.items():
            print(f"{k:8s} {v['label']:24s} title_bar={v['title_bar']:9s} header={v['panel_header']:6s} "
                  f"cover={v['cover']:6s} agenda={v['agenda']:8s} suggested theme={TH.SKIN_THEMES[k]}")
    elif a.cmd == 'analyze':
        from .analyze import analyze
        res = analyze(a.pptx)
        if a.json:
            json.dump(res, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
            print('written', a.json)
        st = res['stats']
        for k in ('font_ea', 'font_latin', 'slide_max_size', 'slide_body_size', 'text_color', 'fill', 'geom', 'effects'):
            items = list(st.get(k, {}).items())[:10]
            print(f'{k:16s}', ', '.join(f'{kk}:{vv}' for kk, vv in items))
        print('theme fonts', res.get('theme_fonts'))
        print('theme colors', res.get('theme_colors'))
    elif a.cmd == 'gallery':
        if a.style == 'showcase':
            from .gallery import build_showcase
            od = a.out or os.path.abspath('showcase')
            os.makedirs(od, exist_ok=True)
            print(build_showcase(od, sheets_dir=a.sheets, skins=a.skins.split(',') if a.skins else None))
        else:
            from .gallery import build_gallery
            print(build_gallery(a.style, a.out, a.theme, a.sheets))


if __name__ == '__main__':
    sys.exit(main())
