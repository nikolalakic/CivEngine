import math

class RetainingWall2: # Wide heel
    def __init__(self):
        self.hw1 = 2 # [m]
        self.ts = 0.3 # [m]
        self.tb = 0.8 # [m]
        self.B = 3.5 # [m] aprox. (0.5-0.7)*H
        self.b = 1.4 # [m]
        self.bt = 0.4 # [m]
        self.h = 3.2  # [m]
        self.gamma_k_1 = 19 # [kN/m^3]
        self.gamma_k_1_w = 22 # [kN/m^3]
        self.gamma_prime = self.gamma_k_1_w - 9.807 # [kN/m^3]
        if self.hw1 == 0:
            self.gamma_k_1_w = self.gamma_k_1
            self.gamma_prime = self.gamma_k_1
        self.hw2 = self.h + self.tb - self.hw1
        self.alpha_c = math.atan((self.b - self.ts) / self.h) # [radians]
        self.H = self.h + self.tb
        #self.ck1 = 0
        self.phi_k_1 = 34 # [degrees]
        self.gamma_k_2 = 18  # [kN/m^3]
        #self.ck2 = 5
        self.phi_k_2 = 30  # [degrees]
        self.Df = 1.3 # [m]
        self.gamma_concrete = 24 # [kN/m^3]
        self.q = 10 # [kN/m]
        betta_q = 15 # degrees
        self.betta_q = math.radians(betta_q) # [radians]
        self.H = self.tb + self.h
        self.sigma_rd = 155.6  # [kN/m^2]
        self.gamma_g = 1.35
        self.gamma_q = 1.5
        self.gamma_g_fav = 1
        self.gamma_g_stb = 0.9
        self.gamma_g_dstb = 1.1
        self.gamma_q_stb = 0
        self.gamma_q_dstb = 1.5
        self.gamma_r_h = 1.1

    @staticmethod
    def _phi_prime(phi, stability=False):
        gamma_prime_phi = 1.25 if stability else 1
        phi_rad = math.radians(phi)
        return math.atan(math.tan(phi_rad) / gamma_prime_phi)

    def bh_rankine(self):
        phi_prime_d_1 = self._phi_prime(self.phi_k_1)
        tg_gamma = math.tan(math.pi/4 + phi_prime_d_1)
        bh_geometrical = self.B - self.b - self.bt
        # Wide heel check
        bh = self.h/tg_gamma- self.b + self.ts
        if bh < 0:
            #print(f'\nCalculated bh={round(bh, 2)} <=0 [m] >> bh={round(bh_geometrical,2)} [m] [accepted]\n\n')
            bh = bh_geometrical
        elif math.ceil(bh * 10) / 10 > 0 and bh < bh_geometrical:
           #print(f'\nCalculated bh={bh} >=0 [m] and bh<={round(bh_geometrical,2)} [m] >> bh = {round(bh_geometrical,2)} [m] [accepted]\n\n')
            bh = bh_geometrical
        else:
            bh = math.ceil(bh * 10) / 10
        return bh

    def B_final(self):
        bh = self.bh_rankine()
        b_final = bh + self.b + self.bt
        if b_final < self.B:
            return self.B
        else:
            return b_final

    def gs1(self): # Soil weight 1
        t = self.Df - self.tb
        gs1 = self.bt * t * self.gamma_k_2
        return gs1

    def gs2(self): # Soil weight 2
        gs2 = math.tan(self.alpha_c) * self.hw2 ** 2 / 2 * self.gamma_k_1
        return gs2

    def gs3(self): # Soil weight 3
        bh = self.bh_rankine()
        gs3 = (self.b - self.ts + bh - math.tan(self.alpha_c) * self.hw2) * self.hw2 * self.gamma_k_1
        return gs3

    def gs4(self): # Soil weight 4
        bh = self.bh_rankine()
        gs4 = math.tan(self.betta_q) * (bh + self.b - self.ts) ** 2 / 2 * self.gamma_k_1
        return gs4

    def gs5(self): # Soil weight 5
        gs5 = math.tan(self.alpha_c) * (self.hw1 - self.tb) ** 2 /2 * self.gamma_k_1_w
        return gs5

    def gs6(self): # Soil weight 6
        bh = self.bh_rankine()
        gs6 = bh * (self.hw1 - self.tb) * self.gamma_k_1_w
        return gs6

    def w2(self): # Buoyancy
        B = self.B_final()
        w2 = (self.hw1 * 9.807) * B / 2
        return w2

    def vq(self):
        B = self.B_final()
        vq = self.q * (B - self.ts - self.bt)/math.cos(self.betta_q)
        return vq

    def gc1(self): # Concrete weight 1
        gc1 = self.h * self.ts * self.gamma_concrete
        return gc1

    def gc2(self): # Concrete weight 2
        B = self.B_final()
        bh = self.bh_rankine()
        gc2 = (B - bh - self.ts - self.bt) * self.h / 2 * self.gamma_concrete
        return gc2

    def gc3(self): # Concrete weight 3
        B = self.B_final()
        gc3 = B * self.tb * self.gamma_concrete
        return gc3

    def coefficient_ka(self, phi, stability=False):
        phi_prime_d1 = self._phi_prime(phi, stability)
        numerator = math.cos(self.betta_q) - math.sqrt(math.sin(phi_prime_d1) ** 2 - math.sin(self.betta_q) ** 2)
        denominator = math.cos(self.betta_q) + math.sqrt(math.sin(phi_prime_d1) ** 2 - math.sin(self.betta_q) ** 2)
        ka = numerator/denominator
        return ka

    def hg1(self, phi, stability=False):
        ka = self.coefficient_ka(phi,stability)
        B = self.B_final()
        hg1 = self.gamma_k_1 * ((B - self.bt - self.ts) * math.tan(self.betta_q) + self.hw2) ** 2 * ka * math.cos(self.betta_q) / 2
        return hg1

    def hg2(self, phi, stability=False):
        ka = self.coefficient_ka(phi,stability)
        B = self.B_final()
        hg2 = self.gamma_k_1 * ((B - self.bt - self.ts) * math.tan(self.betta_q) + self.hw2) * ka * math.cos(self.betta_q) * self.hw1
        return hg2

    def hg3(self, phi, stability=False):
        ka = self.coefficient_ka(phi,stability)
        hg3 =  self.gamma_prime * self.hw1 ** 2 * ka * math.cos(self.betta_q) / 2
        return hg3

    def hq(self, phi, stability=False):
        B = self.B_final()
        ka = self.coefficient_ka(phi,stability)
        hq = self.q * ka * math.cos(self.betta_q) * ((B - self.bt - self.ts) * math.tan(self.betta_q) + self.hw2 + self.hw1)
        return hq

    def hw(self):
        hw = self.hw1 ** 2 * 9.807 / 2
        return hw

    # Horizontal and vertical distances of hgi and hq
    def vd_hg1(self):
        B = self.B_final()
        hd_hg1 = self.hw1 + 1 / 3 * ((B - self.bt - self.ts) * math.tan(self.betta_q) + self.hw2)
        return hd_hg1

    def hd_hg1(self):
        B = self.B_final()
        hd_hg1 = B/2
        return hd_hg1

    def vd_hg2(self):
        vd_hg2 = self.hw1 / 2
        return vd_hg2

    def hd_hg2(self):
        B = self.B_final()
        vd_hg2 = B/2
        return vd_hg2

    def vd_hg3(self):
        vd_vg3 = self.hw1 / 3
        return vd_vg3

    def hd_hg3(self):
        B = self.B_final()
        vd_hg1 = B/2
        return vd_hg1

    def vd_hw(self):
        vd_hw = self.hw1 / 3
        return vd_hw

    def vd_hq(self):
        B = self.B_final()
        vd_hq = (((B - self.bt - self.ts) * math.tan(self.betta_q) + self.hw2 + self.hw1)/2)
        return vd_hq

    def hd_hq(self):
        B = self.B_final()
        hd_hq = B/2
        return hd_hq

    def sum_of_vertical_forces_g(self, phi=None, stability=False):
        if phi is None:
            phi = self.phi_k_1  # Default to self.phi_k_1 if phi is not provided

        def sum_methods(prefix, count, phi=None, stability=None):
            total = 0
            for i in range(1, count + 1):
                method = getattr(self, f"{prefix}{i}")
                if prefix == "hg":
                    total += method(phi, stability)
                else:
                    total += method()
            return total
        hg_sum = sum_methods("hg", 3, phi, stability)
        gc_sum = sum_methods("gc", 3)
        gs_sum = sum_methods("gs", 6)
        w2 = self.w2()
        vg = hg_sum * math.sin(self.betta_q) + gc_sum + gs_sum - w2
        return vg

    def sum_of_vertical_forces_q(self):
        hq = self.hq(phi=self.phi_k_1)
        vq_sum = hq * math.sin(self.betta_q)
        return vq_sum

    def sum_of_horizontal_forces_g(self):
        def sum_methods(prefix, count):
            return sum(getattr(self, f"{prefix}{i}")() for i in range(1, count + 1))
        hg = sum_methods("hg", 3)
        hw = self.hw()
        hg_sum = hg * math.cos(self.betta_q) + hw
        return hg_sum

    def sum_of_horizontal_forces_q(self):
        hq = self.hq(phi=self.phi_k_1)
        hq_sum = hq * math.cos(self.betta_q)
        return hq_sum

    def moment_g_around_t(self):
        B = self.B_final()
        bh = self.bh_rankine()
        mg = (self.gc1() * (B / 2 - self.bt - self.ts / 2) +
              self.gc2() * (B / 2 - self.bt - self.ts - 1 / 3 * (self.b - self.ts)) +
              self.gc3() * (B /2 - B / 2) +
              self.gs1() * (B / 2 - self.bt / 2) +
              self.gs2() * (B / 2 - self.bt - self.ts - 2 / 3 * (math.tan(self.alpha_c) * self.hw2)) -
              self.gs3() * (self.bt + self.ts + (math.tan(self.alpha_c) * self.hw2))/2 -
              self.gs4() * (B / 2 - 1 / 3 * (B - self.bt - self.ts)) +
              self.gs5() * (B / 2 - (self.bt + self.ts + (math.tan(self.alpha_c) * self.hw2) + 2 / 3 * (self.b - self.ts - (math.tan(self.alpha_c) * self.hw2)))) -
              self.gs6() * (B / 2 - bh / 2) +
              (self.hg1(phi=self.phi_k_1) * math.cos(self.betta_q) * self.vd_hg1() - self.hg1(phi=self.phi_k_1) * math.sin(self.betta_q) * self.hd_hg1()) +
              (self.hg2(phi=self.phi_k_1) * math.cos(self.betta_q) * self.vd_hg2() - self.hg2(phi=self.phi_k_1) * math.sin(self.betta_q) * self.hd_hg2()) +
              (self.hg3(phi=self.phi_k_1) * math.cos(self.betta_q) * self.vd_hg3() - self.hg3(phi=self.phi_k_1) * math.sin(self.betta_q) * self.hd_hg3()) +
              self.hw() * self.hw1 / 3 +
              self.w2() * (B / 2 - B / 3)
              )

        return mg

    def moment_q_around_t(self):
        bh = self.bh_rankine()
        B = self.B_final()
        mq = self.hq(phi=self.phi_k_1) * (math.cos(self.betta_q) * (self.H + math.tan(self.betta_q) * (bh + self.b - self.ts))/2 -
                          math.sin(self.betta_q) * B / 2)
        return mq

    def stability_check(self):
        B = self.B_final()
        bh = self.bh_rankine()
        med_stb = (self.gamma_g_stb *
                   (self.gc1() * (self.ts / 2 + self.bt) +
                    self.gc2() * ((self.b - self.ts) / 3 + self.bt + self.ts) +
                    self.gc3() * (B / 2) +
                    self.gs1() * (self.bt / 2) +
                    self.gs2() * (2 / 3 * (math.tan(self.alpha_c) * self.hw2) + self.ts + self.bt) +
                    self.gs3() * ((B + ((math.tan(self.alpha_c) * self.hw2) + self.ts + self.bt))/2) +
                    self.gs4() * (2 / 3 * (B - self.bt - self.ts) + self.ts + self.bt) +
                    self.gs5() * (self.bt + self.ts + (math.tan(self.alpha_c) * self.hw2) + 2 / 3 * ((self.hw1 - self.tb) * math.tan(self.alpha_c))) +
                    self.gs6() * (bh / 2 + self.b + self.bt) +
                    self.hg1(phi=self.phi_k_2, stability=True) * math.sin(self.betta_q) * B +
                    self.hg2(phi=self.phi_k_2, stability=True) * math.sin(self.betta_q) * B +
                    self.hg3(phi=self.phi_k_2, stability=True) * math.sin(self.betta_q) * B +
                    self.hq(phi=self.phi_k_2, stability=True) * math.sin(self.betta_q) * B * self.gamma_q_stb
        ))
        med_dstb = (self.gamma_g_dstb *
                    (self.hg1(phi=self.phi_k_2, stability=True) * math.cos(self.betta_q) * ((math.tan(self.betta_q) * (bh + self.b - self.ts) + self.hw2) / 3 + self.hw1) +
                     self.hg2(phi=self.phi_k_2, stability=True) * math.cos(self.betta_q) * self.hw1 / 2 +
                     self.hg3(phi=self.phi_k_2, stability=True) * math.cos(self.betta_q) * self.hw1 / 3 +
                     self.w2() * 2 / 3 * B +
                     self.hw() * self.hw1 / 3
                     ) + self.gamma_q_dstb * (self.hq(phi=self.phi_k_2, stability=True) * math.cos(self.betta_q) * (self.H + (math.tan(self.betta_q) * (bh + self.b - self.ts))) / 2)
                    )
        if med_dstb/med_stb <= 1:
            a = ("Overturning stability check....OK!\n "
                  f"med_dstb/med_stb = {round(med_dstb/med_stb, 2)} <= 1"
                  "\n")
        else:
            a = ("Overturning stability check....FAIL!\n "
                  f"med_dstb/med_stb = {round(med_dstb/med_stb, 2)} > 1"
                  " \n")
        return a

    def maximum_gross_soil_stress_check(self): # ULS STR
        B = self.B_final()
        f = B * 1
        vg = self.sum_of_vertical_forces_g()
        vq = self.sum_of_vertical_forces_q()
        mg = self.moment_g_around_t()
        mq = self.moment_q_around_t()
        w = 1 / 6 * B ** 2 * 1
        v = self.gamma_g * vg + self.gamma_q * vq
        m = self.gamma_g * mg + self.gamma_q * mq
        sigma_max = v/f + m/w
        if sigma_max > self.sigma_rd:
            a = ("Maximum gross soil stress exceeded....FAIL!\n "
                  f"qed_max = {round(sigma_max,1)} [kN/m] <= sigma_Rd = {round(self.sigma_rd, 1)} [kN/m]\n")
        else:
            a = (f"Maximum gross soil stress....OK!\n "
                 f"qed_max = {round(sigma_max,1)} [kN/m]"
                 f" <= sigma_Rd = {round(self.sigma_rd, 1)} [kN/m]\n")
        return a

    def minimum_gross_soil_stress_check(self): # ULS STR
        vg = self.sum_of_vertical_forces_g()
        vq = self.sum_of_vertical_forces_q()
        mg = self.moment_g_around_t()
        mq = self.moment_q_around_t()
        B = self.B_final()
        f = B * 1 # area of foundation with width of 1m
        w = math.pow(B, 2)/6 * 1
        v = self.gamma_g * vg + self.gamma_q * vq
        m = self.gamma_g * mg + self.gamma_q * mq
        sigma_min = v/f - m/w
        if sigma_min < 0 or sigma_min >= self.sigma_rd:
            a = ("Tension in foundation line or maximum soil stress exceeded....FAIL!\n "
                  f"qed_min = {round(sigma_min,1)} [kN/m] >= sigma_Rd = {round(self.sigma_rd, 1)} [kN/m]\n")
        else:
            a = ("Minimum gross soil check....OK!\n "
                 f"qed_min = {round(sigma_min,1)} [kN/m]"
                 " >= 0\n"
                 f" qed_min = {round(sigma_min,1)} [kN/m] <= sigma_Rd = {round(self.sigma_rd, 1)} [kN/m]\n")
        return a

    def sliding_check(self):
        vg = self.gamma_g_fav * (self.sum_of_vertical_forces_g() + self.w2()) - self.w2() * self.gamma_g
        vq =  self.gamma_q * self.hq(phi=self.phi_k_1) * math.sin(self.betta_q)
        vd = vg + vq
        hrd = (vd * math.tan(self._phi_prime(phi=self.phi_k_2))) / self.gamma_r_h
        hd = (self.gamma_g * (self.hg1(phi=self.phi_k_1) * math.cos(self.betta_q) + self.hg2(phi=self.phi_k_1) * math.cos(self.betta_q) +
              self.hg3(phi=self.phi_k_1) * math.cos(self.betta_q)) + self.gamma_g * self.hw() +
              self.gamma_q * self.hq(phi=self.phi_k_1) * math.cos(self.betta_q))
        if hd/hrd > 1:
            a = ("Sliding stability check....FAIL!\n "
                 f"hd/h_rd = {round(hd / hrd, 2)} > 1")
        else:
            a = ("Sliding stability check....OK!\n "
                 f"hd/h_rd = {round(hd / hrd, 2)} <= 1")
        return a

    def overall_check(self):
        maximum_gross_stress = self.maximum_gross_soil_stress_check()
        minimum_gross_stress = self.minimum_gross_soil_stress_check()
        overturning_check = self.stability_check()
        sliding_check = self.sliding_check()
        print(maximum_gross_stress)
        print(minimum_gross_stress)
        print(overturning_check)
        print(sliding_check)

obj = RetainingWall2()
obj.overall_check()


