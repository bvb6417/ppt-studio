"""PowerPoint COM helpers (Windows + Microsoft PowerPoint): render PNG previews, contact sheets, PDF export,
real-layout overflow check/fix, font embedding. All functions open their own PowerPoint instance.
"""
from __future__ import annotations

import os
import glob
import time


def _app():
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    app = win32com.client.DispatchEx('PowerPoint.Application')
    try:
        app.DisplayAlerts = 1  # ppAlertsNone
    except Exception:
        pass
    return app


def _open(app, path, readonly=True):
    # Open(FileName, ReadOnly, Untitled, WithWindow)
    return app.Presentations.Open(os.path.abspath(path), readonly, False, False)


def export_png(pptx, outdir=None, width=1600, slides=None):
    """Export slides as PNG. slides: iterable of 1-based indices (default all). Returns list of paths."""
    outdir = outdir or os.path.splitext(os.path.abspath(pptx))[0] + '_preview'
    os.makedirs(outdir, exist_ok=True)
    if slides is None:
        for f in glob.glob(os.path.join(outdir, 'slide*.png')):
            try:
                os.remove(f)
            except OSError:
                pass
    app = _app()
    pres = _open(app, pptx)
    try:
        h = int(width * pres.PageSetup.SlideHeight / pres.PageSetup.SlideWidth)
        idx = list(slides) if slides else range(1, pres.Slides.Count + 1)
        out = []
        for i in idx:
            p = os.path.join(os.path.abspath(outdir), f'slide{i:02d}.png')
            pres.Slides(i).Export(p, 'PNG', width, h)
            out.append(p)
        return out
    finally:
        pres.Close()
        app.Quit()


def contact_sheet(pngs, out, cols=4, thumb_w=480, labels=None):
    """Grid of slide thumbnails. labels: optional list of captions (default = file names)."""
    from PIL import Image, ImageDraw, ImageFont
    th = int(thumb_w * 9 / 16)
    pad, lab = 6, 22 if labels else 18
    rows = (len(pngs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (thumb_w + pad) + pad, rows * (th + pad + lab) + pad), (70, 70, 70))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('msyh.ttc', 14)
    except Exception:
        font = ImageFont.load_default()
    for k, f in enumerate(pngs):
        r, c = divmod(k, cols)
        x, y = pad + c * (thumb_w + pad), pad + r * (th + pad + lab)
        im = Image.open(f).convert('RGB')
        im.thumbnail((thumb_w, th))
        sheet.paste(im, (x, y + lab))
        cap = labels[k] if labels and k < len(labels) else os.path.splitext(os.path.basename(f))[0]
        d.text((x + 2, y + 1), cap, fill=(255, 220, 120), font=font)
    sheet.save(out, quality=85)
    return out


def to_pdf(pptx, out=None):
    out = out or os.path.splitext(os.path.abspath(pptx))[0] + '.pdf'
    app = _app()
    pres = _open(app, pptx)
    try:
        pres.SaveAs(os.path.abspath(out), 32)  # ppSaveAsPDF
    finally:
        pres.Close()
        app.Quit()
    return out


def check_overflow(pptx, tol_pt=2.0):
    """Measure every text box with PowerPoint's own layout engine.
    Returns list of dicts: slide, name, text, box_h, text_h, box_w, text_w (points)."""
    app = _app()
    pres = _open(app, pptx)
    issues = []
    try:
        for si in range(1, pres.Slides.Count + 1):
            sl = pres.Slides(si)
            for sh in _iter_shapes(sl.Shapes):
                try:
                    if not sh.HasTextFrame or not sh.TextFrame2.HasText:
                        continue
                except Exception:
                    continue
                tf = sh.TextFrame2
                tr = tf.TextRange
                box_h = sh.Height - tf.MarginTop - tf.MarginBottom
                box_w = sh.Width - tf.MarginLeft - tf.MarginRight
                th, tw = tr.BoundHeight, tr.BoundWidth
                rot = (sh.Rotation or 0) % 180
                if 1 < rot < 179:
                    if abs(rot - 90) > 1:      # oblique text (e.g. labels along a ring): bounds are page-aligned
                        continue
                    th, tw = tw, th            # 90° / 270°: page-aligned bounds are swapped
                wrap = tf.WordWrap
                over_h = th - box_h
                over_w = (tw - box_w) if not wrap else 0
                if over_h > tol_pt or over_w > tol_pt:
                    issues.append(dict(slide=si, name=sh.Name, text=tr.Text[:40].replace('\r', ' / '),
                                       box_h=round(box_h, 1), text_h=round(th, 1), box_w=round(box_w, 1),
                                       text_w=round(tw, 1), size=round(tr.Font.Size, 1)))
    finally:
        pres.Close()
        app.Quit()
    return issues


def fix_overflow(pptx, out=None, min_size=9.0, step=0.5, tol_pt=1.5, skip_prefixes=('deco:',)):
    """Shrink font size of overflowing text boxes until they fit (PowerPoint layout). Saves to out (default in place).
    Returns number of shapes adjusted."""
    app = _app()
    pres = _open(app, pptx, readonly=False)
    n = 0
    try:
        for si in range(1, pres.Slides.Count + 1):
            for sh in _iter_shapes(pres.Slides(si).Shapes):
                try:
                    if not sh.HasTextFrame or not sh.TextFrame2.HasText:
                        continue
                except Exception:
                    continue
                if any(sh.Name.startswith(p) for p in skip_prefixes):
                    continue
                tf = sh.TextFrame2
                tr = tf.TextRange
                box_h = sh.Height - tf.MarginTop - tf.MarginBottom
                box_w = sh.Width - tf.MarginLeft - tf.MarginRight
                changed = False
                for _ in range(40):
                    over = tr.BoundHeight - box_h > tol_pt or (not tf.WordWrap and tr.BoundWidth - box_w > tol_pt)
                    if not over:
                        break
                    # shrink every run proportionally
                    ok = False
                    for k in range(1, tr.Runs().Count + 1):
                        r = tr.Runs(k)
                        if r.Font.Size - step >= min_size:
                            r.Font.Size = r.Font.Size - step
                            ok = True
                    if not ok:
                        break
                    changed = True
                n += changed
        out = os.path.abspath(out or pptx)
        if os.path.abspath(out) == os.path.abspath(pptx):
            pres.Save()
        else:
            pres.SaveAs(out)
    finally:
        pres.Close()
        app.Quit()
    return n


def embed_fonts(pptx, out=None):
    """Re-save with TrueType fonts embedded (only fonts whose license allows embedding; variable fonts may not)."""
    app = _app()
    pres = _open(app, pptx, readonly=False)
    out = os.path.abspath(out or pptx)
    try:
        # SaveAs(FileName, FileFormat=ppSaveAsOpenXMLPresentation(24), EmbedTrueTypeFonts=msoTrue(-1))
        pres.SaveAs(out, 24, -1)
    finally:
        pres.Close()
        app.Quit()
    return out


def _iter_shapes(shapes):
    for i in range(1, shapes.Count + 1):
        sh = shapes(i)
        try:
            if sh.Type == 6:  # msoGroup
                for j in range(1, sh.GroupItems.Count + 1):
                    yield sh.GroupItems(j)
                continue
        except Exception:
            pass
        yield sh
