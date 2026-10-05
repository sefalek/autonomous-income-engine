from __future__ import annotations
import json
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook

def slug(value:str)->str:
    return re.sub(r'[^a-zA-Z0-9]+','-',value.lower()).strip('-')[:70] or 'product'

def write_pdf(path:Path,spec:dict)->None:
    styles=getSampleStyleSheet()
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40)
    story=[Paragraph(spec['title'],styles['Title']),Spacer(1,14),Paragraph('Quick-start guide',styles['Heading2']),Paragraph(spec['problem'],styles['BodyText']),Spacer(1,10),Paragraph('Who this is for',styles['Heading2']),Paragraph(spec['target_customer'],styles['BodyText']),Spacer(1,10),Paragraph('Included',styles['Heading2'])]
    data=[[str(i+1),item] for i,item in enumerate(spec.get('deliverables',[]))]
    table=Table(data,colWidths=[35,440])
    table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story += [table,Spacer(1,14),Paragraph('Implementation checklist',styles['Heading2'])]
    for n in range(1,11):
        story += [Paragraph(f'Step {n}: Complete the relevant action for your workflow.',styles['BodyText']),Spacer(1,5)]
    doc.build(story)

def write_xlsx(path:Path)->None:
    wb=Workbook(); ws=wb.active; ws.title='Tracker'
    ws.append(['Task','Owner','Status','Due date','Notes'])
    for i in range(1,21): ws.append([f'Task {i}','','Not started','',''])
    ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions
    for col,width in {'A':36,'B':20,'C':18,'D':16,'E':40}.items(): ws.column_dimensions[col].width=width
    wb.save(path)

def build_product(spec:dict,out_root:str='dist')->Path:
    folder=Path(out_root)/slug(spec['title']); folder.mkdir(parents=True,exist_ok=True)
    (folder/'product-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'README.md').write_text(f"# {spec['title']}\n\n{spec['sales_angle']}\n\nSuggested price: ${spec['price_usd']}\n\nTarget: {spec['target_customer']}\n",encoding='utf-8')
    write_pdf(folder/'quick-start-guide.pdf',spec); write_xlsx(folder/'tracking-template.xlsx')
    return folder