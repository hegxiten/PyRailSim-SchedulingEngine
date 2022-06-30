import random
from datetime import datetime

from simulation_core.network.System.System import System

sim_init_time = datetime.strptime('2018-01-10 10:00:00', "%Y-%m-%d %H:%M:%S")
sim_term_time = datetime.strptime('2018-01-10 15:30:00', "%Y-%m-%d %H:%M:%S")
spd_container = [random.uniform(0.01, 0.02) for i in range(20)]
acc_container = [0.5 * random.uniform(2.78e-05 * 0.85, 2.78e-05 * 1.15) for i in range(20)]
dcc_container = [0.2 * random.uniform(2.78e-05 * 0.85, 2.78e-05 * 1.15) for i in range(20)]
headway = 300
refresh_time = 50
dos_period = ['2018-01-10 11:30:00', '2018-01-10 12:30:00']
dos_pos = (10, 15)
dos_pos = (-1, -1)

max_spd_list = \
    [0.01933490674860608,
     0.019453894986990607,
     0.019707829327066988,
     0.017072263857428882,
     0.01933490674860608,
     0.010149390929403533,
     0.01700583854618233,
     0.01591656830734718,
     0.019453894986990607,
     0.010893050503940778,
     0.019772652083893845,
     0.01933490674860608]

max_acc_list = \
    [1.3421675939502108e-05,
     1.3421675939502108e-05,
     1.4714042032097714e-05,
     1.2468684884532034e-05,
     1.4714042032097714e-05,
     1.3041880286149402e-05,
     1.3011420386764812e-05,
     1.5164051034412393e-05,
     1.4714042032097714e-05,
     1.5164051034412393e-05,
     1.5556148986558487e-05,
     1.2723347121756601e-05]

max_dcc_list = \
    [2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05,
     2.765432098765432e-05]

