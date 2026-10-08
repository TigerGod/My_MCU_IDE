# -*- coding: utf-8 -*-
"""Extract the GPIO alternate function tables (datasheet section 2.6.5,
Table 2-7 .. Table 2-15, Port A..I) from the GD32F470xx datasheet.

Outputs (next to this script):
  gd32f470_af_table.csv   - Port,Pin,AF0..AF15
  gd32f470_af_table.json  - {"PA0": {"AF1": ["TIMER1_CH0", "TIMER1_ETI"], ...}, ...}
"""
import csv
import json
import os
import re
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, 'GD32F470xx_Datasheet_Rev2.2.pdf')
AF_COLS = ['AF%d' % i for i in range(16)]
TITLE_RE = re.compile(r'Table 2-(\d+)\.\s*Port ([A-I]) alternate functions summary')
PIN_RE = re.compile(r'^P[A-I]\d{1,2}$')


def find_af_pages(doc):
    """Return page indexes holding AF table rows.

    Tables flow across pages (e.g. PA14/PA15 sit on the Port B title page and
    PI11 is on an untitled page), so take every page from the first table
    title onward until a page no longer yields AF rows.
    """
    titled = [i for i in range(doc.page_count)
              if TITLE_RE.search(doc.load_page(i).get_text())
              and '....' not in doc.load_page(i).get_text()]  # skip list of tables
    if not titled:
        return []
    pages = list(range(titled[0], titled[-1] + 1))
    i = titled[-1] + 1
    while i < doc.page_count and extract_page(doc.load_page(i)):
        pages.append(i)
        i += 1
    return pages


def cell_text(words, rect):
    """Rebuild a cell's text from the words whose centre is inside rect.

    Words on the same visual line are joined with a space; consecutive lines
    are concatenated directly, because the datasheet wraps signal names at
    arbitrary characters (e.g. 'TIMER1_C' + 'H0/TIMER' + '1_ETI').
    """
    inside = [w for w in words
              if rect.contains(fitz.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2))]
    inside.sort(key=lambda w: (round(w[3], 0), w[0]))
    lines, last_y = [], None
    for w in inside:
        if last_y is None or abs(w[3] - last_y) > 2:
            lines.append([w[4]])
            last_y = w[3]
        else:
            lines[-1].append(w[4])
    return ''.join(' '.join(l) for l in lines).strip()


def extract_page(page):
    words = page.get_text('words')
    rows = []
    for table in page.find_tables().tables:
        # Continuation fragments at the top of a page are detected with an
        # extra empty margin column on each side (19 cols) - drop those.
        if table.col_count not in (17, 19):
            continue
        for row in table.rows:
            cells = [c for c in row.cells if c is not None]
            cells = [cell_text(words, fitz.Rect(c)) for c in cells]
            if not cells or not PIN_RE.match(cells[0]):
                continue
            if len(cells) != 17:
                raise ValueError('%s: expected 17 columns, got %d' % (cells[0], len(cells)))
            rows.append(cells)
    return rows


def main():
    if not os.path.exists(PDF):
        sys.exit('PDF not found: %s' % PDF)
    doc = fitz.open(PDF)
    result = {}
    for page_index in find_af_pages(doc):
        rows = extract_page(doc.load_page(page_index))
        print('page %d: %s .. %s (%d pins)' % (page_index + 1, rows[0][0], rows[-1][0], len(rows)))
        for cells in rows:
            if cells[0] in result:
                raise ValueError('duplicate pin %s on page %d' % (cells[0], page_index + 1))
            result[cells[0]] = {'port': cells[0][1], 'afs': dict(zip(AF_COLS, cells[1:]))}

    csv_path = os.path.join(HERE, 'gd32f470_af_table.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['Port', 'Pin'] + AF_COLS)
        for pin, info in result.items():
            w.writerow([info['port'], pin] + [info['afs'][a] for a in AF_COLS])

    json_path = os.path.join(HERE, 'gd32f470_af_table.json')
    data = {pin: {af: [s for s in val.split('/') if s]
                  for af, val in info['afs'].items() if val}
            for pin, info in result.items()}
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print('total pins: %d' % len(result))
    print('wrote %s\nwrote %s' % (csv_path, json_path))


if __name__ == '__main__':
    main()
