"""Vektorski (QPainter) crteži poprečnih preseka za GUI.

Zamenjuju rasterske slike iz foldera Graphics. Crteži se iscrtavaju u
logičkom koordinatnom sistemu (dimenzije odgovaraju originalnim slikama)
i skaliraju se na veličinu widget-a uz očuvanje srazmere, pa su oštri
na bilo kojoj rezoluciji i prate boje sistemske teme (svetla/tamna).
"""
import math
import re

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QFont, QFontMetricsF, QPainterPath, QPalette
from PyQt6.QtWidgets import QWidget, QSizePolicy


class _SectionDrawing(QWidget):
    """Osnovna klasa: statičan, read-only crtež preseka."""

    LOGICAL_W = 100
    LOGICAL_H = 100
    FONT_SIZE = 20   # veličina teksta u logičkim jedinicama
    MARGIN = 12      # unutrašnja margina okvira u pikselima ekrana

    def __init__(self, min_w=400, min_h=500, parent=None):
        super().__init__(parent)
        self.setMinimumSize(min_w, min_h)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._p = None
        self._pen_w = 1.3
        self._cosmetic = True

    # ------------------------------------------------------------------
    # Qt
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        pal = self.palette()
        self.fg = pal.color(QPalette.ColorRole.WindowText)
        self._pen_w = 1.3

        # Okvir
        frame = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.setPen(QPen(pal.color(QPalette.ColorRole.Mid), 2))
        p.setBrush(pal.color(QPalette.ColorRole.Window))
        p.drawRoundedRect(frame, 8, 8)

        self._paint_logical(p, frame.adjusted(self.MARGIN, self.MARGIN, -self.MARGIN, -self.MARGIN))
        p.end()

    def _paint_logical(self, p, target):
        """Skalira logičke koordinate na pravougaonik `target` i crta."""
        s = min(target.width() / self.LOGICAL_W, target.height() / self.LOGICAL_H)
        p.save()
        p.translate(target.left() + (target.width() - self.LOGICAL_W * s) / 2,
                    target.top() + (target.height() - self.LOGICAL_H * s) / 2)
        p.scale(s, s)
        self._p = p
        self._set_pen()
        p.setBrush(Qt.BrushStyle.NoBrush)
        self.draw()
        self._p = None
        p.restore()

    def save_image(self, path, width_mm=80):
        """Snima crtež u fajl (crno na belom), za izveštaje.

        .pdf -> vektorski crtež (QPdfWriter), ostalo (.png) -> raster 300 dpi.
        """
        from PyQt6.QtCore import QMarginsF, QSizeF
        from PyQt6.QtGui import QColor, QImage, QPageLayout, QPageSize, QPdfWriter

        dpi = 300
        height_mm = width_mm * self.LOGICAL_H / self.LOGICAL_W
        w_px = round(width_mm / 25.4 * dpi)
        h_px = round(height_mm / 25.4 * dpi)
        self.fg = QColor('black')
        # Pri izvozu: obična (ne-kozmetička) olovka debljine 0.25 mm,
        # izražena u logičkim jedinicama crteža.
        self._cosmetic = False
        self._pen_w = 0.25 / width_mm * self.LOGICAL_W

        if str(path).lower().endswith('.pdf'):
            writer = QPdfWriter(str(path))
            writer.setResolution(dpi)
            writer.setPageLayout(QPageLayout(
                QPageSize(QSizeF(width_mm, height_mm), QPageSize.Unit.Millimeter),
                QPageLayout.Orientation.Portrait, QMarginsF(0, 0, 0, 0)))
            p = QPainter(writer)
            target = QRectF(0, 0, writer.width(), writer.height())
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            self._paint_logical(p, target)
            p.end()
        else:
            img = QImage(w_px, h_px, QImage.Format.Format_RGB32)
            img.setDotsPerMeterX(round(dpi / 0.0254))
            img.setDotsPerMeterY(round(dpi / 0.0254))
            img.fill(QColor('white'))
            p = QPainter(img)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            self._paint_logical(p, QRectF(0, 0, w_px, h_px))
            p.end()
            if not img.save(str(path)):
                raise OSError(f'Nije moguće snimiti sliku: {path}')
        self._pen_w = 1.3
        self._cosmetic = True

    def draw(self):
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Pomoćne funkcije za crtanje
    # ------------------------------------------------------------------
    def _set_pen(self, width=None):
        pen = QPen(self.fg, width or self._pen_w)
        pen.setCosmetic(self._cosmetic)  # na ekranu debljina ne zavisi od skaliranja
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self._p.setPen(pen)

    def line(self, x1, y1, x2, y2):
        self._p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def box(self, x1, y1, x2, y2):
        self._p.setBrush(Qt.BrushStyle.NoBrush)
        self._p.drawRect(QRectF(QPointF(x1, y1), QPointF(x2, y2)))

    def polygon(self, pts):
        path = QPainterPath(QPointF(*pts[0]))
        for pt in pts[1:]:
            path.lineTo(QPointF(*pt))
        path.closeSubpath()
        self._p.setBrush(Qt.BrushStyle.NoBrush)
        self._p.drawPath(path)

    def bar(self, x, y, r):
        """Šipka armature (popunjen krug)."""
        self._p.setBrush(self.fg)
        self._p.drawEllipse(QPointF(x, y), r, r)
        self._p.setBrush(Qt.BrushStyle.NoBrush)

    def circle(self, x, y, r):
        self._p.setBrush(Qt.BrushStyle.NoBrush)
        self._p.drawEllipse(QPointF(x, y), r, r)

    def circle_cross(self, x, y, r):
        """Sila upravna na ravan crteža (⊗)."""
        self.circle(x, y, r)
        d = r / math.sqrt(2)
        self.line(x - d, y - d, x + d, y + d)
        self.line(x - d, y + d, x + d, y - d)

    def hatched_rect(self, x1, y1, x2, y2, step=6):
        self.box(x1, y1, x2, y2)
        p = self._p
        p.save()
        p.setClipRect(QRectF(QPointF(x1, y1), QPointF(x2, y2)))
        h = y2 - y1
        x = x1 - h
        while x < x2:
            self.line(x, y2, x + h, y1)
            x += step
        p.restore()

    def moment_arc(self, cx, cy, r, head=None):
        """Luk momenta sa desne strane centra; strelica na gornjem kraju pokazuje ulevo."""
        head = head or r * 0.22
        self._p.setBrush(Qt.BrushStyle.NoBrush)
        self._p.drawArc(QRectF(cx - r, cy - r, 2 * r, 2 * r), 90 * 16, -180 * 16)
        tip_x, tip_y = cx, cy - r
        self.line(tip_x, tip_y, tip_x + head, tip_y - head * 0.75)
        self.line(tip_x, tip_y, tip_x + head, tip_y + head * 0.75)

    # --- tekst sa indeksima: "b_{i+1}", "h_0" ---------------------------
    @staticmethod
    def _parse(text):
        parts = []
        for m in re.finditer(r"_\{([^}]*)\}|_(.)|([^_]+)", text):
            if m.group(1) is not None:
                parts.append((m.group(1), True))
            elif m.group(2) is not None:
                parts.append((m.group(2), True))
            else:
                parts.append((m.group(3), False))
        return parts

    def text(self, x, y, text, size=None, angle=0, valign="bottom"):
        """Tekst centriran horizontalno na (x, y).

        valign="bottom": tekst stoji iznad tačke (za kotne linije),
        valign="top": tekst je ispod tačke, valign="center": centriran.
        angle=-90 rotira tekst tako da se čita odozdo nagore, a "iznad"
        tada znači levo od tačke.
        """
        p = self._p
        size = size or self.FONT_SIZE
        main_font = QFont("Arial")
        main_font.setPixelSize(max(1, round(size)))
        sub_font = QFont(main_font)
        sub_font.setPixelSize(max(1, round(size * 0.68)))
        fm_main, fm_sub = QFontMetricsF(main_font), QFontMetricsF(sub_font)

        parts = self._parse(text)
        total = sum((fm_sub if sub else fm_main).horizontalAdvance(t) for t, sub in parts)
        sub_drop = size * 0.28
        gap = size * 0.18

        if valign == "bottom":
            base = -gap - fm_main.descent() - (sub_drop if any(s for _, s in parts) else 0) * 0.5
        elif valign == "top":
            base = gap + fm_main.ascent() * 0.8
        else:
            base = fm_main.ascent() * 0.4

        p.save()
        p.translate(x, y)
        if angle:
            p.rotate(angle)
        cx = -total / 2
        for t, sub in parts:
            p.setFont(sub_font if sub else main_font)
            p.drawText(QPointF(cx, base + (sub_drop if sub else 0)), t)
            cx += (fm_sub if sub else fm_main).horizontalAdvance(t)
        p.restore()

    # --- kotne linije ----------------------------------------------------
    def _tick(self, x, y, horizontal):
        t = self.FONT_SIZE * 0.35
        self.line(x - t, y + t, x + t, y - t)          # kosa crta
        e = self.FONT_SIZE * 0.55
        if horizontal:
            self.line(x, y - e, x, y + e)
        else:
            self.line(x - e, y, x + e, y)

    def hdim(self, y, xs, labels=(), size=None):
        """Horizontalni lanac kota na visini y, sa podelama u tačkama xs."""
        over = self.FONT_SIZE * 0.6
        self.line(min(xs) - over, y, max(xs) + over, y)
        for x in xs:
            self._tick(x, y, horizontal=True)
        for (a, b), lab in zip(zip(xs, xs[1:]), labels):
            if lab:
                self.text((a + b) / 2, y, lab, size)

    def vdim(self, x, ys, labels=(), size=None):
        """Vertikalni lanac kota na x, tekst levo od linije (rotiran)."""
        over = self.FONT_SIZE * 0.6
        self.line(x, min(ys) - over, x, max(ys) + over)
        for y in ys:
            self._tick(x, y, horizontal=False)
        for (a, b), lab in zip(zip(ys, ys[1:]), labels):
            if lab:
                self.text(x, (a + b) / 2, lab, size, angle=-90)


class InteractionDiagramDrawing(_SectionDrawing):
    """Pravougaoni presek sa armaturom As1/As2 (dijagram interakcije)."""

    LOGICAL_W = 345
    LOGICAL_H = 756
    FONT_SIZE = 22

    def draw(self):
        x1, x2, y1, y2 = 75, 162, 10, 707
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        d2, d1 = 97, 620

        self.box(x1, y1, x2, y2)

        # Armatura
        self.hatched_rect(92, d2 - 8, 145, d2 + 9)
        self.text(cx, d2 - 8, "As2")
        self.hatched_rect(92, d1 - 8, 145, d1 + 9)
        self.text(cx, d1 - 8, "As1")

        # Opterećenje
        self.circle(cx, cy, 6)
        self.line(cx + 6, cy, 327, cy)
        self.text(290, cy, "NEd, MEd", valign="top")
        self.moment_arc(cx, cy, 62, head=15)

        # Kote
        self.vdim(28, [y1, y2], ["h"])
        self.vdim(226, [y1, d2, d1, y2], ["d2", "h-d1-d2", "d1"])
        self.hdim(740, [x1, x2], ["b"])


class ColumnBracingDrawing(_SectionDrawing):
    """Kvadratni presek stuba sa uzengijama (utezanje stuba)."""

    LOGICAL_W = 784
    LOGICAL_H = 784
    FONT_SIZE = 44

    def draw(self):
        X1, X2, Y1, Y2 = 107, 537, 103, 533       # spoljna ivica preseka
        x1, xm, x2 = 140, 322, 504                 # ose šipki
        y1, ym, y2 = 136, 318, 500

        self.box(X1, Y1, X2, Y2)
        self.box(x1, y1, x2, y2)
        self.polygon([(xm, y1), (x2, ym), (xm, y2), (x1, ym)])

        for x in (x1, xm, x2):
            for y in (y1, ym, y2):
                if (x, y) != (xm, ym):
                    self.bar(x, y, 7)

        self.circle_cross(xm, ym, 15)
        self.text(xm, ym - 22, "NEd", size=50)

        # Kote
        self.hdim(55, [x1, xm, x2], ["b_{i+1}", "b_i"])
        self.hdim(592, [x1, xm, x2], ["b_1", "b_2"])
        self.hdim(680, [X1, x1, x2, X2], ["4", "b_0", "4"], size=38)
        self.hdim(740, [X1, X2], ["b"])

        self.vdim(57, [y1, ym, y2], ["b_{n-1}", "b_n"])
        self.vdim(598, [Y1, y1, ym, y2, Y2], ["4", "b_{i-1}", "b_3", "4"], size=38)
        self.vdim(690, [y1, y2], ["h_0"])
        self.vdim(752, [Y1, Y2], ["h"])


class WallBracingDrawing(_SectionDrawing):
    """Presek zida sa utegnutim krajevima (utezanje zida)."""

    LOGICAL_W = 321
    LOGICAL_H = 775
    FONT_SIZE = 19

    def _zone(self, ys, tie_rows):
        x1, x2 = 85, 137
        self.line(x1, ys[0], x1, ys[-1])
        self.line(x2, ys[0], x2, ys[-1])
        for i in tie_rows:
            self.line(x1, ys[i], x2, ys[i])
        for y in ys:
            self.bar(x1, y, 3)
            self.bar(x2, y, 3)

    def draw(self):
        X1, X2, Y1, Y2 = 68, 152, 38, 705
        x1, x2 = 85, 137
        cx, cy = (X1 + X2) / 2, (Y1 + Y2) / 2

        self.box(X1, Y1, X2, Y2)

        top = [52, 89, 126, 163, 202]
        bot = [541, 578, 615, 652, 690]
        self._zone(top, tie_rows=(0, 1, 3, 4))
        self._zone(bot, tie_rows=(0, 1, 3, 4))

        # Opterećenje
        self.circle_cross(cx, cy, 6)
        self.line(cx + 6, cy, 305, cy)
        self.text(255, cy, "NEd, MEd", valign="top")
        self.moment_arc(cx, cy, 68, head=15)

        # Kote
        self.hdim(24, [x1, x2], ["b_i"])
        self.hdim(228, [x1, x2], ["b_n"])
        self.vdim(50, [52, 89, 163, 202], ["b_{i+1}", "b_{n-2}", "b_{n-1}"])
        self.vdim(183, [52, 89, 163, 202], ["b_3", "b_2", "b_1"])
        self.vdim(20, [Y1, Y2], ["h"])
        self.vdim(180, [bot[0], bot[-1]], ["h_0"])
        self.hdim(727, [X1, x1, x2, X2], ["4", "b_0", "4"], size=16)
        self.hdim(765, [X1, X2], ["b"])


class CompositeBendingDrawing(_SectionDrawing):
    """Složeno savijanje: T-presek (gore) i pravougaoni presek (dole)."""

    LOGICAL_W = 380
    LOGICAL_H = 1030
    FONT_SIZE = 22

    CX = 135          # osa simetrije oba preseka
    DIM_L = 26        # kota h
    DIM_R = 262       # kote d2, h-d1-d2, d1

    def _armatura_i_opterecenje(self, x1, x2, y1, y2, d2, d1):
        cx, cy = self.CX, (y1 + y2) / 2
        self.hatched_rect(x1, d2 - 8, x2, d2 + 9)
        self.text(cx, d2 - 8, "As2")
        self.hatched_rect(x1, d1 - 8, x2, d1 + 9)
        self.text(cx, d1 - 8, "As1")

        self.circle(cx, cy, 6)
        self.line(cx + 6, cy, 362, cy)
        self.text(318, cy, "NEd, MEd", valign="top")
        self.moment_arc(cx, cy, 62, head=15)

        self.vdim(self.DIM_L, [y1, y2], ["h"])
        self.vdim(self.DIM_R, [y1, d2, d1, y2], ["d2", "h-d1-d2", "d1"])

    def _t_presek(self, oy):
        bx1, bx2 = 45, 225          # flanša (b)
        wx1, wx2 = 100, 170         # rebro (b rebra)
        y1, yf, y2 = oy + 50, oy + 160, oy + 450
        self.polygon([(bx1, y1), (bx2, y1), (bx2, yf), (wx2, yf),
                      (wx2, y2), (wx1, y2), (wx1, yf), (bx1, yf)])
        self.hdim(oy + 28, [bx1, bx2], ["b_{eff}"])
        self.hdim(y2 + 25, [wx1, wx2])
        self.text(self.CX, y2 + 25, "b_{rebra}", valign="top")
        self._armatura_i_opterecenje(wx1 + 9, wx2 - 9, y1, y2, y1 + 50, y2 - 50)

    def _pravougaoni_presek(self, oy):
        x1, x2 = 82, 188            # b = b rebra
        y1, y2 = oy, oy + 400
        self.box(x1, y1, x2, y2)
        self.hdim(y2 + 25, [x1, x2])
        self.text(self.CX, y2 + 25, "b = b_{rebra}", valign="top")
        self._armatura_i_opterecenje(x1 + 27, x2 - 27, y1, y2, y1 + 80, y2 - 80)

    def draw(self):
        self._t_presek(0)
        self._pravougaoni_presek(580)


class InteractionCurveDrawing(_SectionDrawing):
    """Stilizovan dijagram interakcije (sličica kartice u glavnom prozoru).

    Tačke su izračunate modelom DijagramInterakcije za primer:
    fck = 30 MPa, b/h = 30/50 cm, d1 = d2 = 5 cm, As1 = As2 (k = 50 %).
    Unutrašnja linija je ω = 0, spoljašnja ω = 0.5; tačke redom odgovaraju
    stanjima dilatacija 2/2, 3.5/0, 3.5/-2.174, 3.5/-10, 3.5/-20, 3.5/-40 ‰.
    """

    LOGICAL_W = 380
    LOGICAL_H = 232
    FONT_SIZE = 20

    UNUTRASNJA = [(1.0, 0.0), (0.81, 0.068), (0.45, 0.121), (0.189, 0.076), (0.109, 0.048), (0.059, 0.028)]
    SPOLJASNJA = [(1.5, 0.0), (1.1, 0.152), (0.45, 0.321), (0.169, 0.268), (-0.039, 0.189), (-0.345, 0.066)]

    NI = (-0.45, 1.6)      # opseg ν
    MI = (0.0, 0.34)       # opseg μ
    X = (30, 350)
    Y = (190, 18)

    def _tacka(self, ni, mi):
        x = self.X[0] + (ni - self.NI[0]) / (self.NI[1] - self.NI[0]) * (self.X[1] - self.X[0])
        y = self.Y[0] + (mi - self.MI[0]) / (self.MI[1] - self.MI[0]) * (self.Y[1] - self.Y[0])
        return QPointF(x, y)

    def _kriva(self, tacke):
        """Glatka kriva kroz tačke (Catmull-Rom spline)."""
        pts = [self._tacka(*t) for t in tacke]
        path = QPainterPath(pts[0])
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1, p2 = pts[i], pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else p2
            path.cubicTo(p1 + (p2 - p0) / 6, p2 - (p3 - p1) / 6, p2)
        self._p.setBrush(Qt.BrushStyle.NoBrush)
        self._p.drawPath(path)

    def draw(self):
        # Ose ν i μ
        o = self._tacka(0, 0)
        self.line(self.X[0] - 10, o.y(), self.X[1] + 18, o.y())
        self.line(o.x(), o.y() + 8, o.x(), self.Y[1] - 6)
        h = 7
        self.line(self.X[1] + 18, o.y(), self.X[1] + 18 - h, o.y() - h * 0.6)
        self.line(self.X[1] + 18, o.y(), self.X[1] + 18 - h, o.y() + h * 0.6)
        self.line(o.x(), self.Y[1] - 6, o.x() - h * 0.6, self.Y[1] - 6 + h)
        self.line(o.x(), self.Y[1] - 6, o.x() + h * 0.6, self.Y[1] - 6 + h)
        self.text(self.X[1] + 12, o.y() + 4, "ν_{Ed}", valign="top")
        self.text(o.x() - 22, self.Y[1] + 4, "μ_{Ed}", valign="center")

        self._kriva(self.UNUTRASNJA)
        self._set_pen(self._pen_w * 2)
        self._kriva(self.SPOLJASNJA)
        self._set_pen()


class ShearDrawing(_SectionDrawing):
    """Pravougaoni presek sa uzengijom i silom smicanja VEd iznad preseka."""

    LOGICAL_W = 345
    LOGICAL_H = 640
    FONT_SIZE = 22

    def draw(self):
        x1, x2, y1, y2 = 95, 235, 150, 560
        cx = (x1 + x2) / 2
        c = 16                                  # zaštitni sloj do uzengije
        yd = y2 - 52                            # osa zategnute armature (d1)

        self.box(x1, y1, x2, y2)

        # Uzengija sa kukom
        self._p.setBrush(Qt.BrushStyle.NoBrush)
        self._p.drawRoundedRect(QRectF(x1 + c, y1 + c, x2 - x1 - 2 * c, y2 - y1 - 2 * c), 8, 8)
        bx, by = x1 + c + 12, y1 + c + 12      # šipka u uglu, oko nje se savija kuka
        self.line(bx + 4, by - 8, bx + 22, by + 10)
        self.line(bx - 8, by + 4, bx + 10, by + 22)

        # Montažna (gore) i zategnuta podužna armatura Asl (dole)
        r = 7
        for x in (x1 + c + 12, x2 - c - 12):
            self.bar(x, y1 + c + 12, r * 0.8)
        for x in (x1 + c + 12, cx, x2 - c - 12):
            self.bar(x, yd, r)
        self.text(cx, yd - 12, "Asl")
        self.text(cx, (y1 + y2) / 2, "m, φ", valign="center")

        # Sila smicanja VEd iznad preseka
        top, tip = 20, y1 - 12
        self.line(cx, top, cx, tip)
        h = 14
        self._p.setBrush(self.fg)
        from PyQt6.QtGui import QPolygonF
        self._p.drawPolygon(QPolygonF([QPointF(cx, tip), QPointF(cx - h * 0.5, tip - h),
                                       QPointF(cx + h * 0.5, tip - h)]))
        self._p.setBrush(Qt.BrushStyle.NoBrush)
        self.text(cx + 44, (top + tip) / 2, "VEd", valign="center")

        # Kote
        self.vdim(48, [y1, y2], ["h"])
        self.vdim(285, [y1, yd, y2], ["d", "d1"])
        self.hdim(600, [x1, x2], ["b"])
