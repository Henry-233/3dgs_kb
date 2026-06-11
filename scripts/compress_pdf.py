import fitz
import sys
from pathlib import Path

def compress_pdf(input_path: str, max_mb: int = 25):
    p = Path(input_path)
    output_path = p.parent / f"{p.stem}_compressed{p.suffix}"
    
    doc = fitz.open(input_path)
    doc.save(
        str(output_path),
        deflate=True,
        garbage=4,
        clean=True,
        image_quality=60
    )
    
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"✅ 压缩完成: {output_path}")
    print(f"   原始大小: {Path(input_path).stat().st_size/1024/1024:.1f} MB")
    print(f"   压缩后: {size_mb:.1f} MB")
    
    if size_mb > max_mb:
        print(f"⚠️  仍超过 {max_mb}MB，建议手动处理")
    
    return str(output_path)

if __name__ == "__main__":
    compress_pdf(sys.argv[1])