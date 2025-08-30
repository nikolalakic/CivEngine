import math
import os
import shutil
from Scripts.RetainingWall2 import RetainingWall2

class RetainingWall2Tex(RetainingWall2):
    def __init__(self):
        super().__init__()
        self.phi_prime = self._phi_prime(self.phi_k_2)
        self.dict = {
            'hw1' : f'{self.hw1}',
            'hw2': f'{self.hw2}',
            'B_final' : f'{self.B_final()}',
            't_s' : f'{self.ts}',
            'b_t' : f'{self.bt}',
            't_b' : f'{self.tb}',
            'h_prvo' : f'{self.h}',
            'gamma_k_1' : f'{self.gamma_k_1}',
            'gamma_k_2' : f'{self.gamma_k_2}',
            'gamma_prime' : f'{self.gamma_prime}',
            'gamma_k1w' : f'{self.gamma_k1w}',
            'phi_k_1' : f'{self.phi_k_1}',
            'phi_k_2' : f'{self.phi_k_2}',
            'h_u' : f'{round(self.total_H(), 2)}',
            'Df' : f'{self.Df}',
            'b_h' : f'{self.bh_rankine()}',
            'b_o': f'{self.b}',
            'sigma_rd' : f'{self.sigma_rd}',
            'q_u' : f'{self.q}',
            'gammag' : f'{self.gamma_g}',
            'gammaq' : f'{self.gamma_q}',
            'gamma_gfav' : f'{self.gamma_g_fav}',
            'gamma_gstb' : f'{self.gamma_g_stb}',
            'gamma_gdstb' : f'{self.gamma_g_dstb}',
            'gamma_qstb' : f'{self.gamma_q_stb}',
            'gamma_qdstb' : f'{self.gamma_q_dstb}',
            'gamma_rh' : f'{self.gamma_r_h}',
            'gamma_concrete' : f'{self.gamma_concrete}',
            'bh_calculated' : f'{self.bh_calculated()}',
            'gs1': f'{round(self.gs1(),2)}',
            'gs2': f'{round(self.gs2(),2)}',
            'gs3': f'{round(self.gs3(),2)}',
            'gs4': f'{round(self.gs4(),2)}',
            'gs5': f'{round(self.gs5(),2)}',
            'gs6': f'{round(self.gs6(),2)}',
            'gc1': f'{round(self.gc1(),2)}',
            'gc2': f'{round(self.gc2(),2)}',
            'gc3': f'{round(self.gc3(),2)}',
            'alpha_c' : f'{round(self.alpha_c * 180/math.pi, 2)}',
            'betta_q' : f'{round(self.betta_q * 180/math.pi, 2)}',
            'gs_three_eq_zero' : f'{round(self.gs3_hw1_eq_zero(),2)}',
            'gs_six_eq_zero': f'{round(self.gs6_hw1_eq_zero(),2)}',
            'koeficijent_ka': f'{round(self.coefficient_ka(phi=self.phi_k_1), 3)}',
            'phi_prime1d' : f'{round(self._phi_prime(phi=self.phi_k_1) * 180/math.pi, 3)}',
            'vqq' : f'{round(self.vq(), 2)}',
            'w_2' : f'{round(self.w2(), 2)}',
            'h_g1' : f'{round(self.hg1(phi=self.phi_k_1), 2)}',
            'h_g2' : f'{round(self.hg2(phi=self.phi_k_1), 2)}',
            'h_g3': f'{round(self.hg3(phi=self.phi_k_1), 2)}',
            'hqq' : f'{round(self.hq(phi=self.phi_k_1), 2)}',
            'h_w' : f'{round(self.hw(), 2)}',
            'hd_hg1' : f'{round(self.hd_hg1(), 3)}',
            'hd_q' : f'{round(self.hd_q(), 2)}',
            'vd_hg1' : f'{round(self.vd_hg1(), 3)}',
            'vd_hg2' : f'{round(self.vd_hg2(), 3)}',
            'vd_hg3' : f'{round(self.vd_hg3(), 3)}',
            'vd_hw' : f'{round(self.vd_hw(), 3)}',
            'vd_hq' : f'{round(self.vd_hq(), 3)}',
            'v_gu' : f'{round(self.sum_of_vertical_forces_g(phi=None, stability=False), 2)}',
            'h_gu' : f'{round(self.sum_of_horizontal_forces_g(), 2)}',
            'h_qu' : f'{round(self.sum_of_horizontal_forces_q(), 2)}',
            'v_qu' : f'{round(self.sum_of_vertical_forces_q(), 2)}',
            'm_g' : f'{round(self.moment_g_around_t(), 2)}',
            'm_q' : f'{round(self.moment_q_around_t(), 2)}'
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
        os.rename("obrada.pdf", 'RetainingWall2_report.pdf')
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