import math

class RetainingWall1: # Rankin theory
    def __init__(self):
        self.ts = 0.25 # [m]
        self.tb = 0.40 # [m]
        self.B = 2 # [m]
        self.h = 2.5 # [m]
        self.gamma_k_1 = 19 # [kN/m^3]
        #self.ck1 = 0
        self.phi_k_1 = 25 # [degrees]
        self.gamma_k_2 = 18  # [kN/m^3]
        #self.ck2 = 5
        self.phi_k_2 = 25  # [degrees]
        self.Df = 1.2 # [m]
        self.gamma_concrete = 25 # [kN/m^3]
        self.q = 5 # [kN/m]
        self.H = self.tb + self.h
        self.sigma_rd = 150 # [kN/m^2]
        self.gamma_g = 1.35
        self.gamma_q = 1.5
        self.gamma_g_fav = 1

    def phi_prime_d1(self):
        gamma_prime_phi = 1
        phi_prime_d_1 = math.radians(self.phi_k_1)/gamma_prime_phi
        return phi_prime_d_1

    def phi_prime_d1_stability(self):
        gamma_prime_phi = 1.25
        phi_k_1 = math.radians(self.phi_k_1)
        phi_prime_d_1 = math.atan(math.tan(phi_k_1)/gamma_prime_phi)
        return phi_prime_d_1

    def phi_prime_d2(self):
        gamma_prime_phi = 1
        phi_prime_d_2 = math.radians(self.phi_k_2)/gamma_prime_phi
        return phi_prime_d_2

    def phi_prime_d2_stability(self):
        gamma_prime_phi = 1.25
        phi_k_2 = math.radians(self.phi_k_2)
        phi_prime_d_2 = math.atan(math.tan(phi_k_2)/gamma_prime_phi)
        return phi_prime_d_2

    def bh(self):
        phi_prime_d_1 = self.phi_prime_d1()
        # Wide heel check
        bh = self.h * math.tan(math.radians(45) - phi_prime_d_1/2)
        bh = math.ceil(bh * 10)/10
        return bh

    def bt(self): # Leg width
        bh = self.bh()
        bt = self.B - self.ts - bh
        return bt

    def gw(self): # Weight of wall
        gw = self.h * self.ts * self.gamma_concrete
        return gw

    def gf(self): # Weight of foundation
        gf = self.B * self.tb * self.gamma_concrete
        return gf

    def gs2(self): # Weight of soil above leg (disregarded in this case)
        bt = self.bt()
        t = self.Df - self.tb
        gs1 = bt * t * self.gamma_k_2
        return gs1

    def gs1(self): # Weight of soil above heel
        bh = self.bh()
        gs2 = bh * self.h * self.gamma_k_1
        return gs2

    def q_load(self): # Force of distributed load q
        bh = self.bh()
        q = self.q * bh
        return q

    def coefficient_ka(self):
        phi_prime_d1 = self.phi_prime_d1()
        ka = math.pow(math.tan(math.pi/4 - phi_prime_d1/2), 2)
        return ka

    def coefficient_ka_stability(self):
        phi_prime_d1 = math.atan(math.tan(self.phi_prime_d1())/1.25)
        ka = math.pow(math.tan(math.pi/4 - phi_prime_d1/2), 2)
        return ka

    def rhg(self):
        ka = self.coefficient_ka()
        #hg1 = ka * self.gamma_k_1 * self.h
        hg2 = ka * self.gamma_k_1 * self.H
        rhg = hg2 * self.H/2
        return rhg

    def rhg_stability(self):
        ka = self.coefficient_ka_stability()
        #hg1 = ka * self.gamma_k_1 * self.h
        hg2 = ka * self.gamma_k_1 * self.H
        rhg = hg2 * self.H/2
        return rhg

    def rhq(self):
        ka = self.coefficient_ka()
        hq1 = ka * self.q
        hq2 = hq1
        rhq = hq2 * self.H
        return rhq

    def rhq_stability(self):
        ka = self.coefficient_ka_stability()
        hq1 = ka * self.q
        hq2 = hq1
        rhq = hq2 * self.H
        return rhq

    def mg(self):
        bt = self.bt()
        bh = self.bh()
        gw = self.gw()
        gs1 = self.gs1()
        gf = self.gf()
        rhg = self.rhg()
        mg = gw * (self.B/2 - bt - self.ts/2) - gs1 * (self.B/2 - bh/2) + rhg * self.H/3 + gf * 0
        return mg

    def mq(self):
        bh = self.bh()
        rhq = self.rhq()
        q = self.q_load()
        mq = rhq * self.H/2 - q * (self.B/2 - bh/2)
        return mq

    def vg(self):
        gs1 = self.gs1()
        gf = self.gf()
        gw = self.gw()
        vg = gs1 + gf + gw
        return vg

    def vq(self):
        q = self.q_load()
        vq = q
        return vq

    def hg(self):
        rhg = self.rhg()
        hg = rhg
        return hg

    def hq(self):
        rhq = self.rhq()
        hq = rhq
        return hq

    def maximum_gross_soil_stress_check(self): # ULS STR
        vg = self.vg()
        vq = self.vq()
        mg = self.mg()
        mq = self.mq()
        f = self.B * 1 # area of foundation with width of 1m
        w = math.pow(self.B, 2)/6 * 1
        vu = self.gamma_g * vg + self.gamma_q * vq
        mu = self.gamma_g * mg + self.gamma_q * mq
        qed_max = vu/f + mu/w
        if qed_max > self.sigma_rd:
            a = ("Maximum gross soil stress exceeded....FAIL!\n"
                  f"qed_max = {round(qed_max,1)} [kN/m] <= sigma_Rd = {round(self.sigma_rd, 1)} [kN/m]\n")
        else:
            a = (f"Maximum gross soil stress....OK!\n qed_max = {round(qed_max,1)} [kN/m]"
                 f" <= sigma_Rd = {round(self.sigma_rd, 1)} [kN/m]\n")
        return a

    def minimum_gross_soil_stress_check(self): # ULS STR
        vg = self.vg()
        vq = self.vq()
        mg = self.mg()
        mq = self.mq()
        f = self.B * 1 # area of foundation with width of 1m
        w = math.pow(self.B, 2)/6 * 1
        vu = self.gamma_g * vg + self.gamma_q * vq
        mu = self.gamma_g * mg + self.gamma_q * mq
        qed_min = vu/f - mu/w
        if qed_min < 0 or qed_min >= self.sigma_rd:
            a = ("Tension in foundation line or maximum soil stress exceeded....FAIL!\n"
                  f"qed_min = {round(qed_min,1)} [kN/m] >= sigma_Rd = {round(self.sigma_rd, 1)} [kN/m]\n")
        else:
            a = ("Minimum gross soil check....OK!\n"
                 f"qed_min = {round(qed_min,1)} [kN/m]"
                 " >= 0\n"
                 f"qed_min = {round(qed_min,1)} [kN/m] <= sigma_Rd = {round(self.sigma_rd, 1)} [kN/m]\n")
        return a

    def overturning_stability_check(self):
        bt = self.bt()
        bh = self.bh()
        gamma_g_stb = 0.9
        gamma_g_dstb = 1.1
        gamma_q_stb = 0
        gamma_q_dstb = 1.5
        gf = self.gf()
        gw = self.gw()
        gs1 = self.gs1()
        vq = self.vq()
        rhg = self.rhg_stability()
        rhq = self.rhq_stability()
        med_stb = gamma_g_stb * (gw * (self.ts/2 + bt) + gs1 * (bh/2 + self.ts + bt) + gf * (self.B/2)) + gamma_q_stb * vq * (bh/2 + self.ts + bt)
        med_dstb = gamma_g_dstb * (rhg * self.H/3) + gamma_q_dstb * (rhq * self.H/2)
        if med_dstb/med_stb <= 1:
            a = ("Overturning stability check....OK!\n"
                  f"med_dstb/med_stb = {round(med_dstb/med_stb, 2)} <= 1"
                  " [kNm/m]\n")
        else:
            a = ("Overturning stability check....FAIL!\n"
                  f"med_dstb/med_stb = {round(med_dstb/med_stb, 2)} > 1"
                  " [kNm/m]\n")
        return a

    def sliding_stability_check(self):
        phi_prime_d2 = self.phi_prime_d2()
        gamma_rh = 1.1
        vg = self.vg()
        vq = self.vq()
        vd = self.gamma_g_fav * vg + self.gamma_q * vq
        hg = self.hg()
        hq = self.hq()
        hd = self.gamma_g * hg + self.gamma_q * hq
        h_rd = vd * math.tan(phi_prime_d2)/gamma_rh
        if hd/h_rd > 1:
            a = ("Sliding stability check....FAIL!\n"
                 f"hd/h_rd = {round(hd / h_rd, 2)} > 1"
                 " [kN/m]\n")
        else:
            a = ("Sliding stability check....OK!\n"
                 f"hd/h_rd = {round(hd / h_rd, 2)} <= 1"
                 " [kN/m]\n")
        return a

    def overall_check(self):
        maximum_gross_stress = self.maximum_gross_soil_stress_check()
        minimum_gross_stress = self.minimum_gross_soil_stress_check()
        overturning_check = self.overturning_stability_check()
        sliding_check = self.sliding_stability_check()
        print(maximum_gross_stress)
        print(minimum_gross_stress)
        print(overturning_check)
        print(sliding_check)

obj = RetainingWall1()
obj.overall_check()
