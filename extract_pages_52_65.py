# -*- coding: utf-8 -*-
import fitz
pdf = r'e:\My_MCU_IDE\GD32F470xx_Datasheet_Rev2.2.pdf'
doc = fitz.open(pdf)
for p in range(52, 65):
    txt = doc.load_page(p).get_text('text')
    print('==== PAGE', p + 1, '====')
    for line in txt.splitlines():
        if any(k in line for k in ['Table 2-7', 'Table 2-8', 'Port A', 'Port B', 'AF0', 'AF1', 'AF2', 'AF3', 'AF4', 'AF5', 'AF6', 'AF7', 'AF8', 'AF9', 'AF10', 'AF11', 'AF12', 'AF13', 'AF14', 'AF15']):
            print(line)
