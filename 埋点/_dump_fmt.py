import sys
import openpyxl

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = r"c:\Users\Administrator\Documents\GitHub\code_aiken\埋点\埋点需求-复古相机.xlsx"
wb = openpyxl.load_workbook(path)

for ws in wb.worksheets:
    print("=" * 100)
    print(f"SHEET: {ws.title}  dims={ws.dimensions}  freeze={ws.freeze_panes}")
    print("-- col widths --")
    for k, v in sorted(ws.column_dimensions.items()):
        if v.width:
            print(f"   {k}: w={v.width:.1f}")
    print("-- row heights --")
    for k, v in sorted(ws.row_dimensions.items()):
        if v.height:
            print(f"   {k}: h={v.height:.1f}")
    print("-- merged --")
    print("   ", sorted(str(r) for r in ws.merged_cells.ranges))
    print("-- styled cells in first 4 rows --")
    for row in ws.iter_rows(min_row=1, max_row=4):
        for c in row:
            if c.value is None and not c.has_style:
                continue
            f, fill, b, al = c.font, c.fill, c.border, c.alignment
            fcolor = None
            try:
                fcolor = f.color.rgb if f.color and f.color.type == "rgb" else None
            except Exception:
                pass
            bg = None
            try:
                bg = fill.start_color.rgb if fill.start_color and fill.start_color.type == "rgb" else None
            except Exception:
                pass
            val = repr(c.value)
            if len(val) > 60:
                val = val[:60] + "..."
            print(f"   {c.coordinate}: {val} | font={f.name},{f.size},bold={f.bold},color={fcolor} | fill={fill.fill_type},{bg} | align={al.horizontal},{al.vertical},wrap={al.wrap_text} | border=t{b.top.style},b{b.bottom.style},l{b.left.style},r{b.right.style}")
