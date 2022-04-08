# -*- coding: utf-8 -*-
import numpy as np
from sko.tools import func_transformer

__all__ = ["PSO_Seismic", "SeismicLocate"]


class PSO_Seismic():
    """
    ----------------------------------------
    # <Microseismic source stratified location algorithm> 
    @ Author  : S.Li 
    @ Time    : 2022/03/25
    This algorithm is improved to solve the problem of seismic location.  

    This algorithm was adapted from the earlier works of github.com/guofei9987
    ----------------------------------------
    # <PSO algorithm>
    # @Author  : github.com/guofei9987
    # @Time    : 2019/8/20


    Parameters
    --------------------
    func : function
        The func you want to do optimal
    n_dim : int
        Number of dimension, which is number of parameters of func.
    pop : int
        Size of population, which is the number of Particles. We use 'pop' to keep accordance with GA
    max_iter : int
        Max of iter iterations
    threshold : float
        The loop will stop if gbest less than threshold
    N:
        The loop will stop if continuous N gbest has no improvement
    lb : array_like
        The lower bound of every variables of func
    ub : array_like
        The upper bound of every variables of func
    constraint_eq : tuple
        equal constraint. Note: not available yet.
    constraint_ueq : tuple
        unequal constraint
    Attributes
    ----------------------
    pbest_x : array_like, shape is (pop,dim)
        best location of every particle in history
    pbest_y : array_like, shape is (pop,1)
        best image of every particle in history
    gbest_x : array_like, shape is (1,dim)
        general best location for all particles in history
    gbest_y : float
        general best image  for all particles in history
    gbest_y_hist : list
        gbest_y of every iteration

    """

    def __init__(self, n_dim = 4, pop = 40, max_iter = 150, threshold = None, N = None, lb = -1e5, ub = 1e5, w = 0.8,
                 c1 = 0.5, c2 = 0.5,
                 constraint_eq = tuple(), constraint_ueq = tuple(),
                 geophones_coordinates = list(), time_list = list()
                 ):

        n_dim = n_dim

        self.func = func_transformer(self.fitness_function)
        self.w = w  # inertia
        self.cp, self.cg = c1, c2  # parameters to control personal best, global best respectively
        self.pop = pop  # number of particles
        self.n_dim = n_dim  # dimension of particles, which is the number of variables of func
        self.max_iter = max_iter  # max iter
        self.threshold = threshold
        self.N = N
        self.geophones_coordinates = geophones_coordinates
        self.time_list = time_list

        self.lb, self.ub = np.array(lb) * np.ones(self.n_dim), np.array(ub) * np.ones(self.n_dim)
        self.compressed_lb, self.compressed_ub = self.lb.copy(), self.ub.copy()

        assert self.n_dim == len(self.lb) == len(self.ub), 'dim == len(lb) == len(ub) is not True'
        assert np.all(self.ub > self.lb), 'upper-bound must be greater than lower-bound'

        self.has_constraint = bool(constraint_ueq)
        self.constraint_ueq = constraint_ueq
        self.is_feasible = np.array([True] * pop)

        self.X = np.random.uniform(low = self.lb, high = self.ub, size = (self.pop, self.n_dim))
        v_high = self.ub - self.lb
        self.V = np.random.uniform(low = -v_high, high = v_high, size = (self.pop, self.n_dim))  # speed of particles
        self.Y = self.cal_y()  # y = f(x) for all particles
        self.pbest_x = self.X.copy()  # personal best location of every particle in history
        self.pbest_y = np.array([[np.inf]] * pop)  # best image of every particle in history
        self.gbest_x = self.pbest_x.mean(axis = 0).reshape(1, -1)  # global best location for all particles
        self.gbest_y = np.inf  # global best y for all particles
        self.gbest_y_hist = []  # gbest_y of every iteration
        self.update_gbest()

        # record verbose values
        self.record_mode = False
        self.record_value = {'X': [], 'V': [], 'Y': []}
        self.best_x, self.best_y = self.gbest_x, self.gbest_y  # history reasons, will be deprecated

    def check_constraint(self, x):
        # gather all unequal constraint functions
        for constraint_func in self.constraint_ueq:
            if constraint_func(x) > 0:
                return False
        return True

    def update_V(self):
        r1 = np.random.rand(self.pop, self.n_dim)
        r2 = np.random.rand(self.pop, self.n_dim)
        self.V = self.w * self.V + \
                 self.cp * r1 * (self.pbest_x - self.X) + \
                 self.cg * r2 * (self.gbest_x - self.X)

    def update_X(self):
        self.X = self.X + self.V
        self.X = np.clip(self.X, self.lb, self.ub)

    def cal_y(self):
        # calculate y for every x in X
        self.Y = self.func(self.X).reshape(-1, 1)
        return self.Y

    def update_pbest(self):
        '''
        personal best
        :return:
        '''
        self.need_update = self.pbest_y > self.Y
        for idx, x in enumerate(self.X):
            if self.need_update[idx]:
                self.need_update[idx] = self.check_constraint(x)

        self.pbest_x = np.where(self.need_update, self.X, self.pbest_x)
        self.pbest_y = np.where(self.need_update, self.Y, self.pbest_y)

    def update_gbest(self):
        '''
        global best
        :return:
        '''
        idx_min = self.pbest_y.argmin()
        if self.gbest_y > self.pbest_y[idx_min]:
            self.gbest_x = self.X[idx_min, :].copy()
            self.gbest_y = self.pbest_y[idx_min]

    def recorder(self):
        if not self.record_mode:
            return
        self.record_value['X'].append(self.X)
        self.record_value['V'].append(self.V)
        self.record_value['Y'].append(self.Y)

    def fit(self):
        '''
        Fit
        '''
        global_iter_num = 0
        # last_gbest_y = float('inf')
        # c = 0
        iter_num = 0
        # ajust_w_iter_num = 0
        while iter_num < self.max_iter:
            global_iter_num += 1
            # print(global_iter_num,iter_num)

            # if global_iter_num>10000:
            #     print()
            #     break
            # else:
            #     pass

            # print(f"\r{round(global_iter_num/10000*100,2)}%",end='',flush=True)

            self.update_V()
            self.recorder()
            self.update_X()
            self.cal_y()
            self.update_pbest()
            self.update_gbest()

            self.gbest_y_hist.append(self.gbest_y)
            iter_num += 1

            # # Step 2
            # if not self.expert_judge():
            #     continue

            # # Step 4
            # if self.gbest_y < last_gbest_y:
            #     ajust_w_iter_num = 0
            #     # print("<<<")
            #     # Step 5
            #     if ((self.threshold is not None) and (self.gbest_y < self.threshold)):
            #         break
            #     else:
            #         last_gbest_y = self.gbest_y
            #         self.gbest_y_hist.append(self.gbest_y)
            #         iter_num += 1
            #         continue
            # else:
            #     # Step 6
            #     if ajust_w_iter_num <= 0:
            #         # print("ajust_W")
            #         self.ajust_w()
            #     # print("ajust_w_iter_num += 1")
            #     ajust_w_iter_num += 1

            #     if ajust_w_iter_num >= self.N:
            #         # Step7 & Step 8
            #         # print("N ******")
            #         ajust_w_iter_num = 0
            #         self.compress_search_space()
            #         self.ajust_V_limit()
            #     else:
            #         pass

            # if iter_num > 0 and (self.N is not None) and (self.gbest_y >= self.gbest_y_hist[-1]):
            #     c = c + 1
            #     if c > self.N:
            #         break
            #     else:
            #         c = 0

        self.best_x, self.best_y = self.gbest_x, self.gbest_y
        return self.best_x, self.best_y

    def fitness_function(self, x):
        #  X, Y, Z
        x_0, y_0, z_0 = x
        C_0 = [x_0, y_0, z_0]
        V = 3600
        # Coordinates
        C = self.geophones_coordinates
        # The number of geophone
        n = len(C)
        W = self.time_list
        t = sum([W[k] - self.eu_dist(C_0, C[k]) / V for k in range(n)]) / n
        Q = sum([(W[k] - t - self.eu_dist(C_0, C[k]) / V) ** 2 for k in range(n)])

        return Q

    def eu_dist(self, C_0: list, C_k: list):
        return ((C_k[0] - C_0[0]) ** 2 + (C_k[1] - C_0[1]) ** 2 + (C_k[2] - C_0[2]) ** 2) ** 0.5

    def expert_judge(self):
        """
        ...
        """
        return True

    def ajust_w(self):
        self.w = self.w * np.random.uniform(0.9, 1.1)

    def ajust_V_limit(self):
        v_high = self.ub - self.lb
        compressed_v_high = self.compressed_ub - self.compressed_lb
        V_1 = np.random.uniform(low = -v_high, high = v_high, size = (int(self.pop / 2), self.n_dim))
        V_2 = np.random.uniform(low = -compressed_v_high, high = compressed_v_high,
                                size = (self.pop - int(self.pop / 2), self.n_dim))
        self.V = np.concatenate((V_1, V_2), axis = 0)

    def compress_search_space(self):
        self.compressed_lb = self.compressed_lb * 1.05
        self.compressed_ub = self.compressed_ub * 0.95
        X_1 = np.random.uniform(low = self.lb, high = self.ub, size = (int(self.pop / 2), self.n_dim))
        X_2 = np.random.uniform(low = self.compressed_lb, high = self.compressed_ub,
                                size = (self.pop - int(self.pop / 2), self.n_dim))
        self.X = np.concatenate((X_1, X_2), axis = 0)

    def compute(self):

        bset_x, best_y = self.fit()

        x_0, y_0, z_0 = bset_x
        C_0 = [x_0, y_0, z_0]
        V = 3600

        C = self.geophones_coordinates
        n = len(C)
        W = self.time_list
        t = sum([W[k] - self.eu_dist(C_0, C[k]) / V for k in range(n)]) / n
        results = [t, x_0, y_0, z_0, best_y[0]]

        # print("RES:",results)
        return results


class SeismicLocate():
    def __init__(self, geophones_coordinates: list, time_list: list, max_distance: float = 1500, v_p: float = 3600):
        self.geophones_coordinates = geophones_coordinates
        self.time_list = time_list
        self.max_distance = max_distance

    def run(self):
        x_i = [xyz[0] for xyz in self.geophones_coordinates]
        y_i = [xyz[1] for xyz in self.geophones_coordinates]
        z_i = [xyz[2] for xyz in self.geophones_coordinates]
        x_0_min, x_0_max = min(
            x_i) - self.max_distance, max(x_i) + self.max_distance
        y_0_min, y_0_max = min(
            y_i) - self.max_distance, max(y_i) + self.max_distance
        # z_0_min, z_0_max = min(
        #     z_i) - self.max_distance, max(z_i) + self.max_distance
        z_0_min, z_0_max = 890, 950

        constraint_ueq = []
        for x, y, z in self.geophones_coordinates:
            constraint_ueq.append(
                lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2 + (p[2] - z) ** 2 - self.max_distance ** 2
            )

        alg = PSO_Seismic(
            n_dim = 3,
            pop = 60,
            max_iter = 100,
            threshold = 1e-10,
            N = None,
            lb = [x_0_min, y_0_min, z_0_min],
            ub = [x_0_max, y_0_max, z_0_max],
            w = 0.3,
            c1 = 2,
            c2 = 2,
            # constraint_eq=tuple(),
            constraint_ueq = constraint_ueq,
            geophones_coordinates = self.geophones_coordinates,
            time_list = self.time_list
        )
        res = alg.compute()
        # print(res)
        return res


def solve(geophones_coordinates, time_list):
    geophones_coordinates = [[-3902077.25, 36376474.50, 886.34],
                             [-3902541.43, 36376337.24, 904.82],
                             [-3902776.98, 36376478.80, 902.56],
                             [-3902733.14, 36376282.27, 908.90]]
    time_list = [6.902, 6.776, 6.714, 6.760]
    obj = SeismicLocate(geophones_coordinates, time_list)
    t, x, y, z, r = obj.run()
    # print(x, y, z)
    return x, y, z


if __name__ == "__main__":
    # Example
    # geophones_coordinates = [[-3902077.25, 36376474.50, 886.34],
    #                          [-3902541.43, 36376337.24, 904.82],
    #                          [-3902776.98, 36376478.80, 902.56],
    #                          [-3902733.14, 36376282.27, 908.90]]
    # time_list = [6.902, 6.776, 6.714, 6.760]
    # res = solve(geophones_coordinates, time_list)
    # loc = [*res]
    # print(loc)

    """ 返回值
    t: P波到时
    x,y,z: 定位坐标
    r: 残差平方和
    """
    # obj = SeismicLocate(geophones_coordinates, time_list)
    # t,x,y,z,r=obj.run()
    # print(x,y,z)

    """  # Test
    import time
    t_0=time.time()
    X,Y=[],[]
    for _ in range(10):
        obj = SeismicLocate(geophones_coordinates, time_list)
        t,x,y,z,r=obj.run()

        t_pos=[-3902776.23,36376457.23, 904.61 ]

        def eu_dist( C_0: list, C_k: list):
            return ((C_k[0]-C_0[0])**2+(C_k[1]-C_0[1])**2+(C_k[2]-C_0[2])**2)**0.5

        dist=eu_dist(t_pos,[x,y,z])
        dx=x-t_pos[0]
        dy=y-t_pos[1]
        dz=z-t_pos[2]
        print("dist=",dist,"dx=",dx,"dy=",dy,"dz=",dz)
        X.append(dx)
        Y.append(dy)
    
    print("T=",time.time()-t_0)
    import matplotlib.pyplot as plt


    plt.scatter(X,Y)
    plt.show()
    """
