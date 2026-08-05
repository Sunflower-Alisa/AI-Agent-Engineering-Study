from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text_langchain(text: str, chunk_size=500, overlap=50) -> list[str]:
    """
    递归文本切分
    chunk_size：单块最大字符
    chunk_overlap：块之间重叠，保证上下文连贯
    """
    spliter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", "。", ".", " "],
    )
    chunks = spliter.split_text(text)
    return chunks
