import os
import shutil
from Scripts.RetainingWall2 import RetainingWall2

class RetainingWall2Tex(RetainingWall2):
    def __init__(self):
        super().__init__()
        self.dict = {
            'hw1' : f'{self.hw1}',
            'hw2': f'{self.hw2}',
            'B_final' : f'{self.B}'
        }

    def tex_file_path(self):
        os.chdir("../LatexTemplates")
        filepath = str(os.getcwd()) +  r'\RetainingWall2.tex'
        return filepath

    def consume_file(self):
        file = self.tex_file_path()
        src = file
        dst = os.path.dirname(os.path.abspath(file)) + r'\obrada.tex'
        shutil.copy(src, dst)
        return dst

    def cleanup_of_residual_files(self):
        os.chdir('../LatexTemplates')
        files= os.listdir()
        for i in files:
            if i.endswith(".pdf"):
                os.remove(i)
        path_pdf_latex = 'pdflatex.exe'
        os.system(f'{path_pdf_latex} obrada.tex')
        final_pdf = os.rename("obrada.pdf", 'RetainingWall2_report.pdf')
        files_to_delete = ["obrada.tex", "obrada.aux", "obrada.log", "obrada.out", "obrada.synctex.gz"]
        try:
            for i in files_to_delete:
                os.remove(i)
        except FileNotFoundError:
            pass

    def substitute_variables_in_latex_file(self):
        texfile = self.consume_file()
        lines = []
        with open(texfile, 'r', encoding='UTF-8') as infile:
            content = infile.read()
            for src, target in self.dict.items():
                content = content.replace(src, target)
        with open(texfile, 'w', encoding='UTF-8') as outfile:
            outfile.write(content)




def main():
    obj = RetainingWall2Tex()
    obj.consume_file()
    obj.substitute_variables_in_latex_file()
    obj.cleanup_of_residual_files()

if __name__ == "__main__":
    main()