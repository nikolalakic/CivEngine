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
        self.sigma_rd = 155 # [kN/m^2]
        self.gamma_g = 1.35
        self.gamma_q = 1.5
        self.gamma_g_fav = 1

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

    def coefficient_ka(self, stability=False):
        phi_prime_d1 = self._phi_prime(self.phi_k_1, stability)
        numerator = math.cos(self.betta_q) - math.sqrt(math.sin(phi_prime_d1) ** 2 - math.sin(self.betta_q) ** 2)
        denominator = math.cos(self.betta_q) + math.sqrt(math.sin(phi_prime_d1) ** 2 - math.sin(self.betta_q) ** 2)
        ka = numerator/denominator
        return ka

    def hg1(self):
        ka = self.coefficient_ka()
        B = self.B_final()
        hg1 = self.gamma_k_1 * ((B - self.bt - self.ts) * math.tan(self.betta_q) + self.hw2) ** 2 * ka * math.cos(self.betta_q) / 2
        return hg1

    def hg2(self):
        ka = self.coefficient_ka()
        B = self.B_final()
        hg2 = self.gamma_k_1 * ((B - self.bt - self.ts) * math.tan(self.betta_q) + self.hw2) * ka * math.cos(self.betta_q) * self.hw1
        return hg2

    def hg3(self):
        ka = self.coefficient_ka()
        hg3 =  self.gamma_prime * self.hw1 ** 2 * ka * math.cos(self.betta_q) / 2
        return hg3

    def hq(self):
        B = self.B_final()
        ka = self.coefficient_ka()
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

    def sum_of_vertical_forces_g(self):
        def sum_methods(prefix, count):
            return sum(getattr(self, f"{prefix}{i}")() for i in range(1, count + 1))
        hg_sum = sum_methods("hg", 3)
        gc_sum = sum_methods("gc", 3)
        gs_sum = sum_methods("gs", 6)
        w2 = self.w2()
        vg = hg_sum * math.sin(self.betta_q) + gc_sum + gs_sum - w2
        return vg

    def sum_of_vertical_forces_q(self):
        hq = self.hq()
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
        hq = self.hq()
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
              (self.hg1() * math.cos(self.betta_q) * self.vd_hg1() - self.hg1() * math.sin(self.betta_q) * self.hd_hg1()) +
              (self.hg2() * math.cos(self.betta_q) * self.vd_hg2() - self.hg2() * math.sin(self.betta_q) * self.hd_hg2()) +
              (self.hg3() * math.cos(self.betta_q) * self.vd_hg3() - self.hg3() * math.sin(self.betta_q) * self.hd_hg3()) +
              self.hw() * self.hw1 / 3 +
              self.w2() * (B / 2 - B / 3)
              )

        return mg

obj = RetainingWall2()


