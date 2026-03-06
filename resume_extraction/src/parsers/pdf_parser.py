from typing import Optional
from ..models import ResumeModel
from ..utils.text_utils import clean_text


class PdfParser:
    """PDF格式简历解析器"""
    
    def __init__(self):
        """初始化PDF解析器"""
        try:
            import PyPDF2
            self.pypdf2_available = True
        except ImportError:
            self.pypdf2_available = False
    
    def parse(self, text: str) -> ResumeModel:
        """解析PDF格式的简历文本
        
        注意：PDF解析需要安装PyPDF2库
        pip install PyPDF2
        
        Args:
            text: PDF文件路径
            
        Returns:
            ResumeModel: 解析后的简历模型
        """
        from ..parsers.txt_parser import TextParser
        
        # 初始化文本解析器
        text_parser = TextParser()
        
        if self.pypdf2_available:
            # 从PDF文件中提取文本
            pdf_text = self.extract_text(text)
            # 使用文本解析器解析提取的文本
            return text_parser.parse(pdf_text)
        else:
            # 如果没有安装PyPDF2，直接返回空模型
            return ResumeModel()
    
    def extract_text(self, pdf_path: str) -> str:
        """从PDF文件中提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            str: 提取的文本
        """
        if not self.pypdf2_available:
            return ""
        
        import PyPDF2
        
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + '\n'
        
        return clean_text(text)
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """从PDF文件中提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            str: 提取的文本
        """
        return self.extract_text(pdf_path)
