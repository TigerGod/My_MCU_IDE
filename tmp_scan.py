# -*- coding: utf-8 -*-
import os
pdf = r'e:\My_MCU_IDE\GD32F470xx_Datasheet_Rev2.2.pdf'
print('exists', os.path.exists(pdf))
try:
    import fitz
    doc = fitz.open(pdf)
    print('pages', doc.page_count)
    for i in range(min(doc.page_count, 250)):
        txt = doc.load_page(i).get_text('text')
        if '2.6' in txt or 'AF' in txt or 'alternate' in txt.lower() or '重映射' in txt:
            print('---PAGE', i+1, '---')
            for line in txt.splitlines():
                if '2.6' in line or 'AF' in line or 'alternate' in line.lower() or '重映射' in line:
                    print(line)
except Exception as e:
    print(type(e).__name__, e)
