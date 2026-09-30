"""A3分割アプリの「PDF1つにまとめて共有」で作ったPDFから、埋め込みJPEGを元の解像度のまま取り出す。

使い方: python extract_pdf_images.py 入力.pdf [出力フォルダ]
出力フォルダを省略すると、PDFと同じ場所に「PDF名_images」フォルダを作る。
"""
import re
import sys
from pathlib import Path

HEAD = re.compile(rb'/Filter\s*/DCTDecode\s*/Length\s+(\d+)\s*>>\s*stream\r?\n')


def extract(pdf_path: Path, out_dir: Path) -> list[Path]:
    data = pdf_path.read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, m in enumerate(HEAD.finditer(data), 1):
        start, length = m.end(), int(m.group(1))
        jpg = data[start:start + length]
        if not jpg.startswith(b'\xff\xd8'):
            raise ValueError(f'{i}枚目がJPEGとして読めません')
        path = out_dir / f'{i:02d}.jpg'
        path.write_bytes(jpg)
        saved.append(path)
    return saved


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    pdf = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else pdf.with_name(pdf.stem + '_images')
    files = extract(pdf, out)
    if not files:
        sys.exit('JPEGが見つかりませんでした。A3分割アプリで作ったPDFではないか、途中で作り直された可能性があります。')
    print(f'{len(files)}枚を取り出しました: {out}')
