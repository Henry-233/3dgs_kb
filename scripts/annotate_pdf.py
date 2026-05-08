import fitz  # pymupdf
import json
import sys
import io
from pathlib import Path

# Fix Windows GBK encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def annotate_pdf(pdf_path: str, annotations: list, output_path: str = None):
    doc = fitz.open(pdf_path)
    
    # 颜色映射
    colors = {
        "core_contribution": (1, 0.9, 0),      # 黄色：核心贡献
        "method":            (0.5, 1, 0.5),    # 绿色：方法细节
        "result":            (0.5, 0.8, 1),    # 蓝色：实验结果
        "limitation":        (1, 0.6, 0.4),    # 橙色：局限性
        "default":           (1, 1, 0),         # 默认黄色
    }
    
    for ann in annotations:
        page_num = ann.get("page", 1) - 1
        phrase   = ann.get("phrase", "")
        category = ann.get("category", "default")
        note     = ann.get("note", "")
        
        if page_num < 0 or page_num >= len(doc):
            print(f"⚠️  跳过：页码 {page_num+1} 超出范围")
            continue
            
        page    = doc[page_num]
        results = page.search_for(phrase)
        
        if not results:
            print(f"⚠️  未找到：'{phrase}'（第{page_num+1}页）")
            continue
        
        color = colors.get(category, colors["default"])
        for rect in results:
            highlight = page.add_highlight_annot(rect)
            highlight.set_colors(stroke=color)
            if note:
                highlight.set_info(content=note)
            highlight.update()
        
        print(f"✅ 已标注：第{page_num+1}页 '{phrase[:30]}...'")
    
    # 输出路径默认在原文件名加 _annotated
    if not output_path:
        p = Path(pdf_path)
        output_path = str(p.parent / f"{p.stem}_annotated{p.suffix}")
    
    doc.save(output_path)
    print(f"\n📄 已保存：{output_path}")
    return output_path


if __name__ == "__main__":
    # 从命令行接收 JSON 文件路径和 PDF 路径
    if len(sys.argv) < 3:
        print("用法：python annotate_pdf.py <pdf路径> <annotations.json路径>")
        sys.exit(1)
    
    pdf_path  = sys.argv[1]
    json_path = sys.argv[2]
    
    with open(json_path, encoding="utf-8") as f:
        annotations = json.load(f)
    
    annotate_pdf(pdf_path, annotations)