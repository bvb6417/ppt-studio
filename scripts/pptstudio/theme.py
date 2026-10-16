"""Theme = palette roles + font roles + type scale + geometry + style switches.

Design defaults are distilled from ~3,000 designer and redesign slides and public PPT tutorials:
  body 14-18pt (mode 16), content-page title 28-32pt, side margin ~1.9cm (0.75in), title top ~1.3cm,
  text colors = dark grays (not pure black), 1 main hue + neutrals, soft tinted shadows, 0.75-1pt hairlines.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

from . import color as C
from . import fonts as F


@dataclass
class Theme:
    name: str = 'custom'
    mode: str = 'light'                     # 'light' | 'dark'
    # ---- palette (hex without #)
    primary: str = '1F57C3'
    secondary: str = '3FA2F7'               # gradient partner / 2nd hue (analogous)
    accent: str = 'F59E0B'                  # sparing highlight (<5% of area)
    dark: str = '1F2329'                    # titles
    text: str = '3A4150'                    # body
    muted: str = '8A93A6'                   # captions, English sub-titles
    line: str = 'E3E8F0'                    # hairlines / dividers
    bg: str = 'FFFFFF'
    bg2: str = 'F3F6FB'                     # alt band / page tint
    surface: str = 'FFFFFF'                 # cards
    up: str = 'E5484D'                      # data increase (CN convention red-up)
    down: str = '12A150'
    # ---- academic-defense roles
    style: str = 'modern'                   # 'defense' (科研答辩风: NSFC/科技奖/毕业答辩) | 'modern' (设计师风)
    deep: str = ''                          # deep navy for titles / conclusion bars ('' -> shade of primary)
    emph: str = ''                          # keyword emphasis color ([[...]] markup); defense = red C00000
    yellow: str = 'F8D008'                  # emphasis text on deep bars
    panel: str = 'F0F3F8'                   # light panel fill
    panel_line: str = 'C9D6EA'              # thin panel border
    # ---- fonts (family names; resolved against installed fonts in __post_init__)
    font_title: str = 'sans'
    font_body: str = 'sans'
    font_latin: str | None = None           # None -> same as body CJK font
    font_number: str = 'number'
    font_serif: str = 'serif'
    font_display: str | None = None         # optional calligraphy/display face for cover punch words
    title_weight: str = 'bold'              # 'bold' | 'black' | 'medium'
    portable: bool = False                  # True -> only Microsoft YaHei / Arial (safe on any Windows/Office)
    # ---- type scale (pt)
    size_cover: float = 48
    size_section: float = 40
    size_title: float = 28
    size_heading: float = 18
    size_body: float = 16
    size_small: float = 13
    size_caption: float = 11
    size_min: float = 12                    # never auto-shrink body below this
    line_spacing: float = 1.25              # body paragraphs (x1.2 pitch)
    # ---- geometry (inches) on 13.333 x 7.5
    margin_x: float = 0.75
    title_y: float = 0.42
    title_h: float = 0.62
    content_top: float = 1.55
    content_bottom: float = 6.95
    gap: float = 0.24
    radius: float = 0.10
    # ---- style switches
    card_style: str = 'shadow'              # shadow | tint | outline | flat | glass
    bg_style: str = 'soft'                  # soft | plain | grid | dots | dark_glow
    title_style: str = 'plain'              # plain | en | mark
    decoration: str = 'normal'              # min | normal | rich
    icon_style: str = 'circle_grad'         # circle_grad | circle_pale | plain
    shadow_alpha: float = 0.14
    shadow_blur: float = 22
    shadow_dist: float = 5
    extras: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.deep:
            self.deep = C.shade(C.norm(self.primary), 0.22)
        if not self.emph:
            self.emph = 'C00000' if self.style == 'defense' else C.norm(self.primary)
        for k in ('primary', 'secondary', 'accent', 'dark', 'text', 'muted', 'line', 'bg', 'bg2', 'surface', 'up', 'down',
                  'deep', 'emph', 'yellow', 'panel', 'panel_line'):
            setattr(self, k, C.norm(getattr(self, k)))
        self.resolve_fonts()

    # ------------------------------------------------------------ fonts
    def resolve_fonts(self):
        p = self.portable
        self.f_body = F.pick(self.font_body, p) if self.font_body in F.STACKS else self.font_body
        self.f_title = F.pick(self.font_title, p) if self.font_title in F.STACKS else self.font_title
        self.f_latin = self.font_latin or self.f_body
        self.f_number = ('Arial' if p else F.pick(self.font_number)) if self.font_number in F.STACKS else self.font_number
        self.f_serif = F.pick(self.font_serif, p) if self.font_serif in F.STACKS else self.font_serif
        self.f_display = self.font_display
        # heavy title face if available (e.g. "Noto Sans SC Black")
        self.f_title_heavy = None
        if self.title_weight in ('black', 'medium') and not p:
            self.f_title_heavy = F.weight_family(self.f_title, self.title_weight)
        self.f_body_light = None if p else F.weight_family(self.f_body, 'light')
        self.f_body_medium = None if p else F.weight_family(self.f_body, 'medium')

    def font(self, role: str):
        """-> (ea_family, latin_family, force_bold)"""
        if role == 'title':
            if self.f_title_heavy:
                return self.f_title_heavy, self.f_title_heavy, False
            return self.f_title, self.f_title, True
        if role == 'heavy':
            heavy = None if self.portable else (F.weight_family(self.f_title, 'black') or F.weight_family(self.f_title, 'bold'))
            return (heavy, heavy, False) if heavy else (self.f_title, self.f_title, True)
        if role == 'medium':
            if self.f_body_medium:
                return self.f_body_medium, self.f_body_medium, False
            return self.f_body, self.f_latin, False
        if role == 'light':
            if self.f_body_light:
                return self.f_body_light, self.f_body_light, False
            return self.f_body, self.f_latin, False
        if role == 'number':
            return self.f_body, self.f_number, False
        if role == 'serif':
            return self.f_serif, self.f_serif, False
        if role == 'display':
            d = self.f_display or self.f_title
            return d, d, False
        return self.f_body, self.f_latin, False

    # ------------------------------------------------------------ colors
    @property
    def is_dark(self):
        return self.mode == 'dark'

    def c(self, spec) -> str:
        """Resolve a color spec: role name, derived role, or hex. Returns 'RRGGBB'.
        Derived roles: primary_dark/_light/_pale/_bg, secondary_pale, accent_pale, on_primary, white, black.
        Modifiers: 'primary+30' = tint 30%, 'primary-20' = shade 20%.
        """
        if spec is None:
            return None
        s = str(spec).strip()
        if s.startswith('#') or (len(s) in (3, 6) and all(ch in '0123456789abcdefABCDEF' for ch in s)):
            return C.norm(s)
        for op in ('+', '-'):
            if op in s[1:]:
                base, amt = s.rsplit(op, 1)
                try:
                    t = float(amt) / 100
                    b = self.c(base)
                    return C.tint(b, t) if op == '+' else C.shade(b, t)
                except ValueError:
                    pass
        roles = {
            'white': 'FFFFFF', 'black': '000000',
            'primary_dark': C.shade(self.primary, 0.28),
            'primary_light': C.tint(self.primary, 0.45),
            'primary_pale': C.tint(self.primary, 0.88) if not self.is_dark else C.mix(self.bg, self.primary, 0.22),
            'primary_bg': C.tint(self.primary, 0.95) if not self.is_dark else C.mix(self.bg, self.primary, 0.10),
            'secondary_pale': C.tint(self.secondary, 0.88) if not self.is_dark else C.mix(self.bg, self.secondary, 0.2),
            'accent_pale': C.tint(self.accent, 0.85) if not self.is_dark else C.mix(self.bg, self.accent, 0.2),
            'on_primary': C.readable(self.primary),
            'on_dark': 'FFFFFF',
            'primary_deep': self.deep,
            'panel_light': C.mix(self.panel, 'FFFFFF', 0.55),
            'emph_pale': C.tint(self.emph, 0.9),
        }
        if s in roles:
            return roles[s]
        if hasattr(self, s) and isinstance(getattr(self, s), str) and len(getattr(self, s)) == 6:
            return getattr(self, s)
        named = (self.extras or {}).get('colors', {})
        if s in named:
            return self.c(named[s])
        raise ValueError(f'unknown color role {spec!r}')

    def ramp(self, n: int):
        """n harmonious series colors for charts/categories: primary first, then secondary/tints."""
        base = [self.primary, self.secondary, C.tint(self.primary, 0.45), self.accent,
                C.shade(self.secondary, 0.25), C.tint(self.secondary, 0.5), self.muted]
        out = []
        for i in range(n):
            out.append(base[i % len(base)])
        return out

    def copy(self, **kw):
        t = copy.deepcopy(self)
        for k, v in kw.items():
            setattr(t, k, v)
        t.__post_init__()
        return t


# ---------------------------------------------------------------- presets
def _light(name, primary, secondary, accent, **kw):
    return dict(name=name, mode='light', primary=primary, secondary=secondary, accent=accent, **kw)


PRESETS = {
    # research / 科研 (light, restrained, school-color friendly)
    'academic_blue': _light('academic_blue', '1F57C3', '3FA2F7', 'F59E0B', bg2='F3F6FB'),
    'academic_navy': _light('academic_navy', '14336B', '2F7BD9', 'D9822B', bg2='F2F5FA'),
    'tsinghua_purple': _light('tsinghua_purple', '660874', 'A450B0', 'D6A02A', bg2='F7F2F8'),
    'pku_red': _light('pku_red', '8C0A10', 'C8474C', '2F5E8C', bg2='FBF4F3'),
    'academic_green': _light('academic_green', '0F7A5A', '38B28A', 'E0A32E', bg2='F2F8F5'),
    # daily / 日常 (work reports, courseware)
    'business_blue': _light('business_blue', '1E66F5', '4FA3FF', 'FF8A3D', bg2='F3F7FE'),
    'business_navy': _light('business_navy', '12356B', '2F80ED', 'F2994A', bg2='F2F5F9'),
    'gov_red': _light('gov_red', 'B81C22', 'E0584C', 'D4A64A', bg2='FBF5F1', dark='3A1F1C'),
    'eco_green': _light('eco_green', '0F8B63', '5CC08E', 'F2B134', bg2='F1F8F4'),
    'warm_orange': _light('warm_orange', 'E8611A', 'F7A04A', '1F4E79', bg2='FDF6F0'),
    'minimal_gray': _light('minimal_gray', '222831', '5B6B82', '2563EB', bg2='F4F5F7', card_style='outline'),
    # competition / 竞赛 (bolder)
    'tech_dark': dict(name='tech_dark', mode='dark', primary='2F7CFF', secondary='22D3EE', accent='FACC15',
                      dark='FFFFFF', text='D5DEEC', muted='8397B8', line='22365F', bg='07122B', bg2='0C1C40',
                      surface='0F2350', bg_style='dark_glow', card_style='glass', shadow_alpha=0.35),
    'vivid_purple': _light('vivid_purple', '5B3CF5', 'A06BFF', 'FF7A45', bg2='F5F3FF'),
    # domain
    'water': _light('water', '0B5CAD', '1AA3D6', 'F2A33A', bg2='F0F6FC', dark='14243A'),
}

# ---- 科研答辩风 (NSFC / 国省科技奖 / 毕业答辩 / 开题) — dense, navy + red emphasis
_DEF = dict(mode='light', style='defense', dark='1A1A1A', text='1F1F1F', muted='6B7489', line='D5DDEA',
            bg='FFFFFF', bg2='F0F3F8', surface='FFFFFF', size_title=26, size_body=15, size_heading=16,
            size_small=12.5, size_caption=11, size_min=10.5, line_spacing=1.15, card_style='outline',
            title_style='plain', decoration='min', font_title='sans', font_body='sans', title_weight='bold',
            margin_x=0.42, title_y=0.28, content_top=1.18, content_bottom=7.12, gap=0.16, radius=0.04)


def _def(name, primary, deep, secondary, accent='F2A33A', title_bar='slant', **kw):
    d = dict(_DEF)
    d.update(name=name, primary=primary, deep=deep, secondary=secondary, accent=accent,
             extras={'title_bar': title_bar})
    d.update(kw)
    return d


PRESETS.update({
    'nsfc_blue': _def('nsfc_blue', '124CAD', '033E9C', '3A7BD5', panel='F0F3F8', panel_line='C5D3EA'),
    'nsfc_navy': _def('nsfc_navy', '0F3A8A', '0A2A66', '2F6DC8', title_bar='bars', panel='EEF2F8'),
    'bright_blue': _def('bright_blue', '1E6FE0', '1456B8', '4FA0FF', title_bar='band', panel='EFF5FE',
                        panel_line='C7DBF7'),
    'nsfc_red': _def('nsfc_red', 'B3161E', '8A0F16', 'D9534F', accent='1F4E9E', emph='B3161E', yellow='FFE58A',
                     title_bar='bars', panel='FBF1F1', panel_line='EBC9CB'),
    'nsfc_green': _def('nsfc_green', '0B7A5A', '075A42', '2FA67E', title_bar='bars', panel='EEF7F3',
                       panel_line='C3E0D4'),
    'nsfc_purple': _def('nsfc_purple', '5B2A86', '421C66', '8A5CC0', title_bar='slant', panel='F4F0F8',
                        panel_line='D9CCE8'),
    'burgundy': _def('burgundy', '8C1D2B', '6B1420', 'B84B5A', title_bar='bars', emph='C00000', panel='F8F1F2',
                     panel_line='E5CCD0'),
    'water_nsfc': _def('water_nsfc', '0E57A8', '063F86', '1C8FD0', title_bar='slant', panel='EEF4FA',
                       panel_line='C3D5EC'),
    # colors sampled from the 2026-10 reference decks (新参考)
    'royal_blue': _def('royal_blue', '1170C6', '0B4F9E', '3A8EE0', title_bar='vband', panel='EEF5FC',
                       panel_line='C3DAF2'),                       # 国家科学技术(进步)奖
    'deep_blue': _def('deep_blue', '0A4FA0', '063A7A', '2F74C8', title_bar='photoband', panel='EEF3FA',
                      panel_line='C2D3EA'),                        # 国家重点研发计划
    'navy_deep': _def('navy_deep', '013E87', '012C63', '2D6BC4', title_bar='numbox', panel='EEF2F8',
                      panel_line='C3D0E4'),                        # 长江学者
    'cobalt': _def('cobalt', '0A36A2', '07287A', '3B67D0', title_bar='square', panel='EEF2FA',
                   panel_line='C5D0EC'),                           # 全国重点实验室 / 树叶
    'steel_blue': _def('steel_blue', '1D5CA6', '134484', '4A86CC', title_bar='thin', panel='EEF4FB',
                       panel_line='C6D7EC'),                       # 万人计划
})


# ---- 答辩风格家族 (skins): page chrome of the template families seen in NSFC / 省国奖 / 重点研发 / 毕业答辩
# decks (学术风参考图: 像素答辩·树叶答辩·百宝箱; easyslides: 亮蓝白·深蓝白·红·绿·重点研发). A skin only changes
# chrome (title bar, panel headers, cover, agenda, background, footer, ending); colors come from the theme.
SKINS = {
    'pixel': dict(label='像素答辩·国自然/省奖经典', title_bar='slant', panel_header='ribbon', cover='band',
                  agenda='vertical', deco='corner', bottom='rule', ending='band'),
    'leaf': dict(label='树叶答辩·国自然青年学生/博士项目', title_bar='bars', panel_header='pill', cover='band',
                 agenda='vertical', deco='none', bottom='rule', ending='band'),
    'baibao': dict(label='百宝箱·国自然基金答辩', title_bar='underline', panel_header='trap', cover='sky',
                   agenda='split', deco='corner', bottom='rule', ending='sky'),
    'bright': dict(label='亮蓝白·国自然申请/结题', title_bar='band', panel_header='strip', cover='left',
                   agenda='card', deco='arcs', bottom='none', ending='band'),
    'badge': dict(label='深蓝白·项目论证/科技奖', title_bar='badge', panel_header='strip', cover='award',
                  agenda='card', deco='none', bottom='band', ending='split'),
    'center': dict(label='居中标题·红色/酒红', title_bar='center', panel_header='ribbon', cover='band',
                   agenda='vertical', deco='corner', bottom='rule', ending='band'),
    'tab': dict(label='色块标签·绿色/农林生态', title_bar='tab', panel_header='tab', cover='sky', agenda='card',
                deco='none', bottom='rule', ending='sky'),
    'tech': dict(label='重点研发·蓝色科技', title_bar='lightband', panel_header='ribbon', cover='tech',
                 agenda='split', deco='dots', bottom='band', ending='split'),
    # ---- families from the 2026-10 reference set (新参考: 像素答辩 / 树叶答辩 decks)
    'jinbu': dict(label='科技进步奖·亮蓝通栏', title_bar='vband', panel_header='strip', cover='plaque',
                  agenda='vertical', deco='none', bottom='none', ending='plaque', statement='box'),
    'kexue': dict(label='科学技术奖·斜杠标题', title_bar='slash', panel_header='dash', cover='midband',
                  agenda='band', deco='none', bottom='rule', ending='midband', statement='key'),
    'zhongdian': dict(label='重点研发·深蓝图带', title_bar='photoband', panel_header='fade', cover='arc',
                      agenda='corner', deco='none', bottom='none', ending='band', statement='box'),
    'changjiang': dict(label='长江学者·编号方块', title_bar='numbox', panel_header='trap', cover='tag',
                       agenda='card', deco='none', bottom='rule', ending='sky', statement='box'),
    'lab': dict(label='重点实验室·双色方标', title_bar='square', panel_header='pale', cover='lab',
                agenda='split', deco='none', bottom='rule', ending='sky', statement='box'),
    'wanren': dict(label='万人计划·细线标题', title_bar='thin', panel_header='strip', cover='midband',
                   agenda='vertical', deco='none', bottom='none', ending='split', statement='bar', cover_pill='outline',
                   cover_texture='plain'),
    'shenbao': dict(label='重点研发申报·半圆标', title_bar='halfdisc', panel_header='notch', cover='band',
                    agenda='corner', deco='none', bottom='none', ending='band', statement='bar'),
}
# color theme that matches each skin in the references (any defense theme works with any skin)
SKIN_THEMES = {'pixel': 'nsfc_blue', 'leaf': 'nsfc_navy', 'baibao': 'water_nsfc', 'bright': 'bright_blue',
               'badge': 'nsfc_navy', 'center': 'nsfc_red', 'tab': 'nsfc_green', 'tech': 'nsfc_blue',
               'jinbu': 'royal_blue', 'kexue': 'royal_blue', 'zhongdian': 'deep_blue', 'changjiang': 'navy_deep',
               'lab': 'cobalt', 'wanren': 'steel_blue', 'shenbao': 'nsfc_blue'}


def apply_skin(theme, skin):
    """Return a copy of `theme` with the chrome settings of SKINS[skin] in its extras."""
    if not skin:
        return theme
    if skin not in SKINS:
        raise KeyError(f'unknown skin {skin!r}; skins: {", ".join(SKINS)}')
    extras = dict(theme.extras or {})
    extras.update({k: v for k, v in SKINS[skin].items() if k != 'label'})
    extras['skin'] = skin
    return theme.copy(extras=extras)


def get(name_or_theme=None, **overrides) -> Theme:
    if isinstance(name_or_theme, Theme):
        return name_or_theme.copy(**overrides) if overrides else name_or_theme
    if name_or_theme is None:
        name_or_theme = 'academic_blue'
    if isinstance(name_or_theme, dict):
        d = dict(name_or_theme)
        base = d.pop('base', None)
        if base:
            t = get(base)
            return t.copy(**d, **overrides)
        if 'primary' in d and len(d) <= 3:
            return from_color(d['primary'], **{k: v for k, v in d.items() if k != 'primary'}, **overrides)
        return Theme(**{**d, **overrides})
    if isinstance(name_or_theme, str) and name_or_theme.lstrip('#').upper() and name_or_theme not in PRESETS:
        try:
            return from_color(name_or_theme, **overrides)
        except ValueError:
            raise KeyError(f'unknown theme {name_or_theme!r}; presets: {", ".join(PRESETS)}')
    return Theme(**{**PRESETS[name_or_theme], **overrides})


def from_color(primary: str, mode='light', name=None, secondary=None, accent=None, style='modern', **kw) -> Theme:
    """Derive a full theme from one brand / school color. style='defense' -> 科研答辩风 spec with this color."""
    p = C.norm(primary)
    h, l, s = C.hls(p)
    sec = C.norm(secondary) if secondary else C.from_hls(h - 0.035, min(0.62, l + 0.18), min(1, s * 0.95 + 0.05))
    acc = C.norm(accent) if accent else C.harmonize_accent(p)
    if style == 'defense':
        d = dict(_DEF)
        d.update(name=name or 'custom_defense', primary=p, deep=C.shade(p, 0.25), secondary=sec, accent=acc,
                 panel=C.tint(p, 0.93), panel_line=C.tint(p, 0.72), extras={'title_bar': 'slant'})
        d.update(kw)
        return Theme(**d)
    if mode == 'dark':
        base = dict(PRESETS['tech_dark'])
        base.update(name=name or 'custom_dark', primary=p, secondary=sec, accent=acc)
        base.update(kw)
        return Theme(**base)
    return Theme(name=name or 'custom', mode='light', primary=p, secondary=sec, accent=acc,
                 bg2=C.tint(p, 0.955), **kw)


SCENARIO_DEFAULTS = {
    # scenario -> theme overrides for the 'modern' style family (defense themes carry their own scale)
    'research': dict(size_title=28, size_body=16, size_min=14, title_style='en', decoration='min'),
    'daily': dict(size_title=28, size_body=16, size_min=12, title_style='plain', decoration='normal'),
    'competition': dict(size_title=30, size_body=16, size_min=13, title_style='en', decoration='rich', title_weight='black'),
}
