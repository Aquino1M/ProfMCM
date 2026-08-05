from __future__ import annotations
import json, re, shutil, zipfile, html
from pathlib import Path
from collections import OrderedDict
from typing import List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image as RLImage, ListFlowable, ListItem, HRFlowable
)

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

ROOT = Path('/mnt/data/metodo_milionario_curso')
INDEX = ROOT / 'index.html'
ASSET_DIR = ROOT / 'assets' / 'illustrations_png'
ASSET_DIR.mkdir(parents=True, exist_ok=True)
(ROOT / 'materiais_modulos').mkdir(parents=True, exist_ok=True)
(ROOT / 'materiais_professor').mkdir(parents=True, exist_ok=True)

# New generated image sources
IMAGE_SOURCES = OrderedDict([
    ('Módulo 0', '/mnt/data/ghostwriter_images/generated/a_stylized_futuristic_dark_tech_workspace_scene_1_batch_1.png'),
    ('Módulo 1', '/mnt/data/ghostwriter_images/generated/a_high_detail_futuristic_digital_illustration_co_2_batch_2.png'),
    ('Módulo 2', '/mnt/data/ghostwriter_images/generated/wide_cinematic_digital_illustration_of_a_video_edi_3_batch_3.png'),
    ('Módulo 3', '/mnt/data/ghostwriter_images/generated/wide_cinematic_digital_illustration_of_a_modern_vi_4_batch_4.png'),
    ('Módulo 4', '/mnt/data/ghostwriter_images/generated/a_detailed_cinematic_futuristic_digital_illustra_5_batch_5.png'),
    ('Módulo 5', '/mnt/data/ghostwriter_images/generated/a_high_tech_digital_workspace_illustration_conce_6_batch_6.png'),
    ('Módulo 6', '/mnt/data/ghostwriter_images/generated/a_cinematic_highly_detailed_digital_illustration_7_batch_7.png'),
    ('Módulo 7', '/mnt/data/ghostwriter_images/generated/a_sleek_futuristic_high_tech_workspace_scene_in_8_batch_8.png'),
    ('Módulo Extra 1', '/mnt/data/ghostwriter_images/generated/a_high_tech_futuristic_digital_illustration_con_9_batch_9.png'),
    ('Módulo Extra 2', '/mnt/data/ghostwriter_images/generated/a_wide_high_detail_futuristic_digital_illustratio_10_batch_10.png'),
    ('Módulo Agência', '/mnt/data/ghostwriter_images/generated/a_wide_cinematic_futuristic_digital_office_agenc_11_batch_1.png'),
    ('Módulo Operação', '/mnt/data/ghostwriter_images/generated/a_high_detail_futuristic_corporate_tech_illustrati_12_batch_2.png'),
    ('Bônus Estratégias Real Oficial', '/mnt/data/ghostwriter_images/generated/a_high_detail_futuristic_digital_marketing_soci_13_batch_3.png'),
])

SAFE_NAMES = {
    'Módulo 0':'modulo_0.png', 'Módulo 1':'modulo_1.png', 'Módulo 2':'modulo_2.png', 'Módulo 3':'modulo_3.png',
    'Módulo 4':'modulo_4.png', 'Módulo 5':'modulo_5.png', 'Módulo 6':'modulo_6.png', 'Módulo 7':'modulo_7.png',
    'Módulo Extra 1':'modulo_extra_1.png', 'Módulo Extra 2':'modulo_extra_2.png',
    'Módulo Agência':'modulo_agencia.png', 'Módulo Operação':'modulo_operacao.png', 'Bônus Estratégias Real Oficial':'bonus_estrategias.png'
}

# ---------- Parse constants from index.html ----------
text = INDEX.read_text(encoding='utf-8')

def extract_bracketed(source: str, marker: str) -> str:
    i = source.index(marker) + len(marker)
    while i < len(source) and source[i].isspace():
        i += 1
    opener = source[i]
    closer = ']' if opener == '[' else '}'
    depth = 0
    in_str = False
    esc = False
    quote = ''
    start = i
    for pos in range(i, len(source)):
        ch = source[pos]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                in_str = False
        else:
            if ch in ('"', "'"):
                in_str = True
                quote = ch
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    return source[start:pos+1]
    raise ValueError(f'Could not parse constant {marker}')

LESSONS = json.loads(extract_bracketed(text, 'const LESSONS = '))
MODULE_FILES = json.loads(extract_bracketed(text, 'const MODULE_FILES = '))
TEACHER_FILES = json.loads(extract_bracketed(text, 'const TEACHER_FILES = '))
MODULE_SUBTITLES = json.loads(extract_bracketed(text, 'const MODULE_SUBTITLES = '))

# ---------- Copy images and update illustration const ----------
illustration_map = OrderedDict()
for module, src in IMAGE_SOURCES.items():
    srcp = Path(src)
    if not srcp.exists():
        raise FileNotFoundError(src)
    dst = ASSET_DIR / SAFE_NAMES[module]
    shutil.copyfile(srcp, dst)
    illustration_map[module] = f'assets/illustrations_png/{SAFE_NAMES[module]}'

text = re.sub(r'const ILLUSTRATION_FILES = .*?;\nfunction card',
              'const ILLUSTRATION_FILES = ' + json.dumps(illustration_map, ensure_ascii=False) + ';\nfunction card',
              text, flags=re.S)
INDEX.write_text(text, encoding='utf-8')

# ---------- PDF style helpers ----------
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Oblique', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))

PAGE_W, PAGE_H = A4
MARGIN = 1.55 * cm
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BookKicker', fontName='DejaVu-Bold', fontSize=9.8, leading=13, alignment=TA_CENTER, textColor=colors.HexColor('#22D3EE'), spaceAfter=6))
styles.add(ParagraphStyle(name='BookTitle', fontName='DejaVu-Bold', fontSize=23, leading=28, alignment=TA_CENTER, textColor=colors.white, spaceAfter=10))
styles.add(ParagraphStyle(name='BookSub', fontName='DejaVu', fontSize=10.8, leading=15, alignment=TA_CENTER, textColor=colors.HexColor('#D1D5DB'), spaceAfter=4))
styles.add(ParagraphStyle(name='H1x', fontName='DejaVu-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#111827'), spaceBefore=4, spaceAfter=8))
styles.add(ParagraphStyle(name='H2x', fontName='DejaVu-Bold', fontSize=13, leading=17, textColor=colors.HexColor('#4F46E5'), spaceBefore=8, spaceAfter=6))
styles.add(ParagraphStyle(name='H3x', fontName='DejaVu-Bold', fontSize=10.5, leading=13.5, textColor=colors.HexColor('#0F172A'), spaceBefore=4, spaceAfter=4))
styles.add(ParagraphStyle(name='Bodyx', fontName='DejaVu', fontSize=9.15, leading=13.6, textColor=colors.HexColor('#334155'), spaceAfter=6))
styles.add(ParagraphStyle(name='Smallx', fontName='DejaVu', fontSize=8.0, leading=10.8, textColor=colors.HexColor('#64748B'), spaceAfter=4))
styles.add(ParagraphStyle(name='Quotex', fontName='DejaVu-Oblique', fontSize=9.05, leading=13.2, textColor=colors.HexColor('#475569'), leftIndent=10, rightIndent=4, spaceAfter=5))
styles.add(ParagraphStyle(name='Tagx', fontName='DejaVu-Bold', fontSize=7.6, leading=9.5, alignment=TA_CENTER, textColor=colors.HexColor('#0F172A')))

class BookDoc(BaseDocTemplate):
    def __init__(self, filename: str, header_text: str, dark_cover: bool = False):
        self.header_text = header_text
        self.dark_cover = dark_cover
        super().__init__(filename, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=1.55*cm, bottomMargin=1.3*cm)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='F')
        self.addPageTemplates(PageTemplate(id='P', frames=[frame], onPage=self._on_page))

    def _on_page(self, canvas, doc):
        canvas.saveState()
        if doc.page == 1:
            canvas.setFillColor(colors.HexColor('#020617'))
            canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor('#0EA5E9'))
            canvas.circle(PAGE_W-1*cm, PAGE_H-1.4*cm, 4.5*cm, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor('#A855F7'))
            canvas.circle(0.5*cm, 1.2*cm, 3.8*cm, fill=1, stroke=0)
        else:
            canvas.setStrokeColor(colors.HexColor('#E2E8F0'))
            canvas.line(MARGIN, PAGE_H-0.95*cm, PAGE_W-MARGIN, PAGE_H-0.95*cm)
            canvas.setFillColor(colors.HexColor('#64748B'))
            canvas.setFont('DejaVu', 7.4)
            canvas.drawString(MARGIN, PAGE_H-0.68*cm, self.header_text)
            canvas.drawRightString(PAGE_W-MARGIN, 0.62*cm, f'Página {doc.page}')
        canvas.restoreState()


def P(txt: str, sty='Bodyx'):
    return Paragraph(html.escape(str(txt)).replace('\n', '<br/>'), styles[sty])

def Rich(raw: str, sty='Bodyx'):
    return Paragraph(raw, styles[sty])

def bullets(items: List[str], ordered=False):
    clean = [str(x).strip() for x in items if str(x).strip()]
    return ListFlowable([ListItem(P(x)) for x in clean], bulletType='1' if ordered else 'bullet', start='1', leftIndent=18, bulletFontName='DejaVu-Bold' if ordered else 'DejaVu', bulletFontSize=8, spaceAfter=7)

def info_box(title: str, body: str, bg='#F8FAFC', border='#CBD5E1'):
    tbl = Table([[P(title, 'H3x')], [P(body, 'Bodyx')]], colWidths=[PAGE_W - 2*MARGIN - 0.15*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg)), ('BOX',(0,0),(-1,-1),0.6,colors.HexColor(border)),
        ('LEFTPADDING',(0,0),(-1,-1),10), ('RIGHTPADDING',(0,0),(-1,-1),10), ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),7)
    ]))
    return tbl

def tag(text_: str, bg='#E0F2FE', border='#7DD3FC'):
    t = Table([[P(text_, 'Tagx')]], colWidths=[3.2*cm])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor(bg)),('BOX',(0,0),(-1,-1),0.45,colors.HexColor(border)),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    return t

def image_panel(module: str, title: str, caption: str, width_cm=9.2):
    path = ROOT / illustration_map[module]
    img = RLImage(str(path), width=width_cm*cm, height=(width_cm*0.56)*cm)
    inner = [[img], [P(title, 'H3x')], [P(caption, 'Smallx')], [tag(module)]]
    box = Table(inner, colWidths=[width_cm*cm])
    box.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#F8FAFC')), ('BOX',(0,0),(-1,-1),0.55,colors.HexColor('#CBD5E1')),
        ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8), ('TOPPADDING',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),8)
    ]))
    return box

def table_map(lessons: List[dict]):
    data = [[P('Aula','H3x'), P('Tema','H3x'), P('Tempo','H3x'), P('Entrega','H3x')]]
    for l in lessons:
        data.append([P(l['lesson'], 'Smallx'), P(l['title'],'Smallx'), P(l['duration'],'Smallx'), P(l['deliverable'],'Smallx')])
    tbl = Table(data, colWidths=[1.55*cm, 6.7*cm, 1.7*cm, 5.2*cm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EDE9FE')), ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#CBD5E1')),
        ('VALIGN',(0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)
    ]))
    return tbl


def module_lessons(module: str) -> List[dict]:
    return [l for l in LESSONS if l['module'] == module]

# ---------- Student PDFs ----------
def build_student_pdf(module: str, rel_path: str):
    lessons = module_lessons(module)
    doc = BookDoc(str(ROOT / rel_path), f'Método Milionário • Material do Aluno • {module}')
    story = [Spacer(1,1.1*cm), Rich('MÉTODO MILIONÁRIO', 'BookKicker'), Rich(module, 'BookTitle'), Rich('Material do aluno para estudo, acompanhamento e execução prática', 'BookSub'), Spacer(1,0.35*cm), image_panel(module, 'Capa do módulo', MODULE_SUBTITLES.get(module, 'Material do módulo'), 10.3), Spacer(1,0.5*cm), Rich('Este PDF funciona como apostila do módulo. Leia junto com os slides, execute os passos e use os checklists para revisar sua entrega.', 'BookSub'), PageBreak()]

    story += [Rich('Como usar este material', 'H1x'), P('1) Abra a aula no player. 2) Leia esta apostila. 3) Faça o passo a passo no seu projeto. 4) Revise no checklist antes de enviar a entrega.'), info_box('Objetivo deste PDF', 'Dar ao aluno uma base de estudo clara, com explicação, sequência lógica e execução prática. A ideia é que cada aula pareça uma mini aula em livro, e não apenas uma lista solta de tópicos.', '#ECFEFF', '#7DD3FC'), Rich('Mapa do módulo', 'H2x'), table_map(lessons), Spacer(1,0.2*cm)]

    for i, lesson in enumerate(lessons, start=1):
        story += [PageBreak(), Rich(f"{lesson['lesson']} • {lesson['title']}", 'H1x')]
        # two-column intro row
        intro_left = [P(lesson['promise']), tag(lesson['duration'], '#F3E8FF', '#C4B5FD'), Spacer(1,0.1*cm), P(f"Entrega desta aula: {lesson['deliverable']}", 'Smallx')]
        intro_table = Table([[Table([[x] for x in intro_left], colWidths=[7.2*cm]), image_panel(module, 'Resumo visual da aula', lesson['promise'], 7.0)]], colWidths=[7.4*cm, 7.0*cm])
        intro_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
        story += [intro_table, Spacer(1,0.22*cm), Rich('Objetivos da aula', 'H2x'), bullets(lesson.get('objectives', [])), Rich('Conceitos que o aluno precisa entender', 'H2x')]
        concept_paras = [f"<b>{idx+1}. {html.escape(c)}</b><br/>{html.escape(explain_concept(c))}" for idx, c in enumerate(lesson.get('concepts', []))]
        for cp in concept_paras:
            story.append(Rich(cp, 'Bodyx'))
        story += [Rich('Framework da aula', 'H2x'), info_box('Ordem recomendada', ' → '.join(lesson.get('framework', [])), '#F8FAFC', '#CBD5E1'), Rich('Passo a passo detalhado', 'H2x')]
        steps = []
        for idx, st in enumerate(lesson.get('steps', []), start=1):
            steps.append(f"{idx}. {st}. Depois deste passo, confira se ele realmente aproxima você do objetivo da aula.")
        story += [bullets(steps, ordered=True), Rich('Exemplo explicado', 'H2x'), info_box('Exemplo da aula', lesson.get('example', 'Use o exemplo do professor para comparar uma versão confusa e uma versão clara.'), '#FFF7ED', '#FDBA74')]
        story += [Rich('Atividade prática do aluno', 'H2x'), info_box('O que fazer agora', lesson.get('exercise', ''), '#ECFDF5', '#86EFAC'), Rich('Checklist antes de enviar', 'H2x')]
        checklist = [f"Entendi e consigo explicar: {obj}." for obj in lesson.get('objectives', [])]
        checklist += [f"Minha entrega está pronta: {lesson['deliverable']}", 'Revisei a clareza, o contexto e a qualidade final.', 'Anotei uma melhoria para a próxima aula.']
        story += [bullets(checklist)]
        if lesson.get('materials'):
            story += [Rich('Materiais de apoio desta aula', 'H2x'), bullets(lesson['materials'])]
        story += [HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceBefore=4, spaceAfter=6), P('Resumo final: execute a aula, revise o checklist e salve a entrega. O material deste PDF serve para estudo e prática contínua.', 'Smallx')]
    doc.build(story)

# ---------- Teacher PDFs ----------
def parse_teacher_html_blocks(raw: str):
    blocks = []
    if not raw:
        return blocks
    if BeautifulSoup:
        soup = BeautifulSoup(raw, 'html.parser')
        for node in soup.children:
            name = getattr(node, 'name', None)
            if not name:
                continue
            if name == 'span' and 'time-chip' in (node.get('class') or []):
                blocks.append(('time', node.get_text(' ', strip=True)))
            elif name in ('h4','h3'):
                blocks.append(('heading', node.get_text(' ', strip=True)))
            elif name == 'p':
                blocks.append(('p', node.get_text(' ', strip=True)))
            elif name in ('ul','ol'):
                items = [li.get_text(' ', strip=True) for li in node.find_all('li', recursive=False)]
                blocks.append((name, items))
    else:
        plain = re.sub('<[^>]+>', ' ', raw)
        blocks.append(('p', re.sub(r'\s+', ' ', plain).strip()))
    return blocks


def build_teacher_pdf(module: str, rel_path: str):
    lessons = module_lessons(module)
    doc = BookDoc(str(ROOT / rel_path), f'Método Milionário • Roteiro do Professor • {module}')
    story = [Spacer(1,1.1*cm), Rich('MÉTODO MILIONÁRIO', 'BookKicker'), Rich('Roteiro do Professor', 'BookTitle'), Rich(module, 'BookSub'), Spacer(1,0.35*cm), image_panel(module, 'Guia visual do módulo', 'Use este roteiro como apoio do professor durante a aula. O ideal é abrir o slide, o PDF do aluno e este material ao mesmo tempo.', 10.3), Spacer(1,0.45*cm), Rich('Este documento foi organizado como um livro de aula: preparação, condução, demonstração, atividade e fechamento.', 'BookSub'), PageBreak(), Rich('Antes de começar o módulo', 'H1x'), bullets(['Abra o PDF do aluno correspondente ao módulo.', 'Tenha um exemplo pronto para demonstrar na tela.', 'Confirme a entrega prática de cada aula.', 'Conduza a aula em ritmo simples: explicar, demonstrar, pausar e corrigir.']), Rich('Mapa do módulo', 'H2x'), table_map(lessons)]
    for lesson in lessons:
        story += [PageBreak(), Rich(f"{lesson['lesson']} • {lesson['title']}", 'H1x')]
        lesson_top = Table([[image_panel(module, 'Apoio visual da aula', lesson['promise'], 6.8), Table([[P('Promessa da aula', 'H3x')], [P(lesson['promise'])], [P('Entrega do aluno', 'H3x')], [P(lesson['deliverable'])], [P('Materiais sugeridos', 'H3x')], [P(', '.join(lesson.get('materials', [])) or 'Slide, exemplo e material do aluno.', 'Smallx')]], colWidths=[7.5*cm])]], colWidths=[7.0*cm, 7.7*cm])
        lesson_top.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
        story += [lesson_top, Spacer(1,0.25*cm), Rich('Objetivos que o professor precisa reforçar', 'H2x'), bullets(lesson.get('objectives', [])), Rich('Sequência pedagógica recomendada', 'H2x'), bullets([f"{i+1}. {x}" for i, x in enumerate(lesson.get('framework', []))], ordered=False)]
        for s_idx, slide in enumerate(lesson.get('slides', []), start=1):
            story += [Rich(f"Slide {s_idx}: {slide.get('title','Slide')}", 'H2x'), P('Bullets do slide: ' + ' • '.join(slide.get('bullets', [])), 'Smallx')]
            for kind, content in parse_teacher_html_blocks(slide.get('teacherHtml') or slide.get('note') or ''):
                if kind == 'time':
                    story.append(tag('Tempo sugerido: ' + content, '#ECFEFF', '#7DD3FC'))
                    story.append(Spacer(1, 0.08*cm))
                elif kind == 'heading':
                    story.append(P(content, 'H3x'))
                elif kind == 'p':
                    style = 'Quotex' if '“' in content or '"' in content else 'Bodyx'
                    story.append(P(content, style))
                elif kind == 'ul':
                    story.append(bullets(content))
                elif kind == 'ol':
                    story.append(bullets(content, ordered=True))
        story += [Rich('Fechamento sugerido da aula', 'H2x'), bullets(['Recapitule as três ideias mais importantes.', f"Confirme a entrega: {lesson['deliverable']}", 'Peça para o aluno baixar ou revisar o PDF do módulo.', 'Registre as dúvidas recorrentes para a próxima turma.'])]
    doc.build(story)

# ---------- Professor guide ----------
def build_teacher_guide(path: Path):
    doc = BookDoc(str(path), 'Método Milionário • Guia Geral do Professor')
    story = [Spacer(1,1.1*cm), Rich('MÉTODO MILIONÁRIO', 'BookKicker'), Rich('Guia Geral do Professor', 'BookTitle'), Rich('Visão macro do curso, dos módulos e do papel do professor', 'BookSub'), Spacer(1,0.35*cm), image_panel('Módulo 0', 'Visão geral do curso', 'Este guia resume a função de cada módulo. Para dar a aula, use também os PDFs específicos do professor.', 10.2), PageBreak(), Rich('Como conduzir o curso', 'H1x'), bullets(['O professor deve simplificar o processo para o aluno.', 'A aula precisa sempre sair da teoria e chegar em uma entrega prática.', 'É melhor avançar com clareza do que tentar falar tudo de uma vez.', 'O PDF do aluno serve como base de estudo; o PDF do professor serve como roteiro de condução.'])]
    for module in MODULE_FILES.keys():
        lessons = module_lessons(module)
        story += [PageBreak(), Rich(module, 'H1x'), image_panel(module, 'Resumo do módulo', MODULE_SUBTITLES.get(module, ''), 8.6), P(MODULE_SUBTITLES.get(module, '')), table_map(lessons), Rich('Foco do professor neste módulo', 'H2x'), bullets(['Explicar o porquê do processo.', 'Mostrar um exemplo na tela.', 'Fazer o aluno praticar ainda durante a aula.', 'Fechar cada aula com uma entrega clara e revisável.'])]
    doc.build(story)


def explain_concept(concept: str) -> str:
    c = concept.lower()
    if 'hook' in c or 'gancho' in c:
        return 'O hook é o ponto inicial que faz a pessoa parar o dedo e continuar assistindo. Ele precisa chamar atenção sem enganar.'
    if 'contexto' in c:
        return 'Contexto é o que ajuda a audiência a entender rapidamente o assunto e por que aquela fala importa.'
    if 'reten' in c:
        return 'Retenção é a capacidade de manter o público assistindo. Para isso, o corte precisa progredir, remover sobras e criar curiosidade.'
    if 'legenda' in c:
        return 'Legenda boa não é apenas transcrever: ela ajuda o entendimento, acompanha o ritmo e melhora a experiência no celular.'
    if 'direito' in c or 'ética' in c:
        return 'Esses temas orientam o uso responsável do conteúdo. Antes de postar, confirme autorização, contexto e segurança.'
    if 'cliente' in c or 'monet' in c or 'oferta' in c:
        return 'Aqui o aluno precisa enxergar o corte como serviço e solução. O conteúdo se conecta a entrega, posicionamento e valor.'
    if 'métrica' in c or 'anal' in c:
        return 'Métrica não serve apenas para olhar números. Ela ajuda a tomar decisões: repetir o que funcionou e corrigir o que travou.'
    return 'Este conceito deve ser entendido de forma prática: o que ele significa, por que importa e como aplicar na entrega final.'

# ---------- Run generation ----------
for module, rel in MODULE_FILES.items():
    build_student_pdf(module, rel)
for module, rel in TEACHER_FILES.items():
    build_teacher_pdf(module, rel)
build_teacher_guide(ROOT / 'guia_do_professor_detalhado.pdf')

# ---------- Zips ----------
student_zip = Path('/mnt/data/pdfs_alunos_metodo_milionario.zip')
teacher_zip = Path('/mnt/data/pdfs_professor_metodo_milionario.zip')
project_zip = Path('/mnt/data/metodo_milionario_visual_completo.zip')

with zipfile.ZipFile(student_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted((ROOT/'materiais_modulos').glob('*.pdf')):
        z.write(p, arcname=p.name)
with zipfile.ZipFile(teacher_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted((ROOT/'materiais_professor').glob('*.pdf')):
        z.write(p, arcname=p.name)
with zipfile.ZipFile(project_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in ROOT.rglob('*'):
        z.write(p, arcname=str(p.relative_to(ROOT.parent)))

print('DONE')
print(student_zip)
print(teacher_zip)
print(project_zip)