from pathlib import Path
SUPPORTED_EXT = (".md", ".txt")

def load_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文档不存在：{file_path}")
    if path.suffix not in SUPPORTED_EXT:
        raise ValueError(f"不支持的文档类型：{path.suffix}，支持：{SUPPORTED_EXT}")
    return path.read_text(encoding="utf-8")
