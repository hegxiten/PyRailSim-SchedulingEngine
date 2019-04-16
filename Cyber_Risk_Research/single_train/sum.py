import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
from collections import defaultdict
import heapq
import simpy

import intervals as I
# from simpy.Simulation import *
# import pandas as pd

class RailNetwork:
    '''
    Class RailNetwork is the base map where the trains are operating on. 
    This class doesn't change the output or parameters for calculation.
    '''
    def __init__(self, G = nx.Graph()):
        self.G = G
    
    @property    
    def single_track_init(self, block_length = [0.5]*100):
        corridor_path = range(length(block_length))
        self.G.add_path(corridor_path)
        for i in range(length(block_length)+1):
                    self.G[i-1][i]['dist'] = block_length[i-1]
                    self.G[i-1][i]['attr'] = None    
        
    def siding_init(self, siding = [10, 20, 30, 40, 50, 60, 70, 80, 90]):
            for i in siding:
                if isinstance(i, int):
                    self.G[i-1][i]['attr'] = 'siding'
                else:
                    self.G[i[0]][i[1]]['attr'] = 'siding'

class Simulator:
    '''
    Class Simulator is trying to instantiate an object. 
    Not started yet.  
    '''
    def __init__(self, strt_t, stop_t, speed, time_log):
        ## define the feature parameters of a train object
        self.refresh = 2
        self.all_schedule = {}
        self.strt_t_ticks = time.mktime(time.strptime(strt_t, "%Y-%m-%d %H:%M:%S"))
        self.stop_t_ticks = time.mktime(time.strptime(stop_t, "%Y-%m-%d %H:%M:%S"))
    
    def scheduling(self):
        pass
    def attack_DoS(self, DoS_strt_t, DoS_stop_t, DoS_block):
        pass
class Train_generator:
    '''
    Class Train_generator is trying to rewrite the generation process within single_train class. 
    Not started yet.  
    '''
    def __init__(self):
        pass


def networkX_write():
    '''
    generate a network graph in simple grids and save it into 'gpickle' file.
    '''
    number = 120
    G = nx.MultiGraph()
    
    pos = {}
    ## define the position (coordinates on the graph) of all nodes on the graph 
    ## it should be a dictionary
    for i in range(1, number+1):
        col = ((i-1) % 20) + 1 if ((i-1) // 20) % 2 == 0 else 20 - (i-1) % 20
        row = i // 20 if i % 20 != 0 else i // 20 - 1
        pos[i] = [col, row]

    nodes = []
    edges = []
    for i in range(1, number+1):
        nodes.append(i)
        if i < number:
            edges.append((i, i+1))
    
    siding = [15, 35, 55, 75]    
    for c in siding:
        nodes.append(c)
        G.add_path((c - 1, c + 1))
    
    ## define siding locations in the grids
    ## add corresponding links to the graph generated 
     
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.set_node_attributes(G, pos, 'pos')
    nx.write_gpickle(G, "a.gpickle")
    

def networkX_read():
    '''
    read "gpickle" file (basemap + data features 'pos')
    dynamically display the node: change the color of a node from red to green every second.
    data are stored in gpickle file together with the basemap
    '''

    G = nx.read_gpickle("a.gpickle")
    pos = nx.get_node_attributes(G, 'pos')

    ncolor = []
    for i in range(len(pos)):
        ncolor.append('r')

    #plt.ion()
    for index in range(len(ncolor)):
        plt.cla()
        ncolor[index] = 'g'
        if index > 0:
            ncolor[index-1] = 'r'
        nx.draw_networkx_nodes(G, pos, node_color=ncolor)
        nx.draw_networkx_labels(G, pos, font_size=16)
        nx.draw_networkx_edges(G, pos)

        # plt.pause(0.01)
    #plt.ioff()
    plt.show()
    #plt.pause(0.2)
    plt.cla()
    plt.close('all')
    return

'''
# code in main class
import networkX_w_r
networkX_w_r.networkX_write()
networkX_w_r.networkX_read()
'''

## Update starts here 20190313       
            

class single_train:
    '''
    many trains are generated by one control point,
    here I want to output the schedule of each train.
    '''

    def __init__(self, strt_t, stop_t, is_DoS, DoS_strt_t, DoS_stop_t, DoS_block, siding, block):
        self.all_schedule = defaultdict(lambda: {})     
        # initialize the global schedule for train Key: self.number
        
        ## load the rail network
        self.G = nx.read_gpickle("a.gpickle")   
        self.pos = nx.get_node_attributes(self.G, 'pos')
        self.labels = {}
        self.pos_labels = {}
        
        self.siding = siding    # position of sidings. A list of integer (block index)
        self.block = block      # the length of each block. A list of floats
        self.blk_sum_top = [sum(self.block[:i+1]) for i in range(len(self.block))]
        self.blk_sum_bot = [sum(self.block[:i]) for i in range(len(self.block))]
        self.blk_interval = zip(self.blk_sum_bot, self.blk_sum_top)
        self.blk_boundaries = self.blk_sum_top[:-1]
        self.blk_idx_list = [a for a in range(len(self.block))]
        self.refresh = 1        # unit of refreshing time in minutes
        
        ## strt_t and stop_t are string for time, the format is '2018-01-01 00:00:00'
        self.T = time
        self.strt_t_ticks = time.mktime(time.strptime(strt_t, "%Y-%m-%d %H:%M:%S"))
        self.stop_t_ticks = time.mktime(time.strptime(stop_t, "%Y-%m-%d %H:%M:%S"))
        
        self.is_DoS = is_DoS    # dummy information of DoS (if DoS is in-place or not)
        self.DoS_strt_t_ticks = time.mktime(time.strptime(DoS_strt_t, "%Y-%m-%d %H:%M:%S"))
        self.DoS_stop_t_ticks = time.mktime(time.strptime(DoS_stop_t, "%Y-%m-%d %H:%M:%S"))
        
        self.clock_time = self.strt_t_ticks
        
        self.DoS_block = DoS_block
        
        self.number = 0         ## self.number is the number of trains.
        
        self.one_schedule = {}  # we get a new self.one_schedule after each refresh
        self.one_detail = {}
        
        self.max_speed = {}
        self.max_acc = {}
        
        self.curr_spd = {}
        self.curr_acc = {}
        
        self.hdw_exp_min = 10   # parameter of headway, in minutes
        self.hdw_dev_min = 3   # standard deviation of headway, in minutes
        
        self.mph_exp = 50       # parameter of speed, in miles per hour
        self.mph_dev = 5        # standard deviation of speed, in miles per hour
        
        '''state variables below: dictionaries describing the states of every train
        ## coord_mp means x-axis coordinates, default value is 0
        ## coord_mp is the dictionary for trains with the Key Value as train indices (integers)
        ## the current block for any train at any moment 1 is the default value for any key in this dictionary
        ## the cumulative distance used to determine the current block, default value is the length of the first block
        '''
        self.curr_mp = defaultdict(lambda: 0.0)    # assuming every train initialize from the coordinate origin
        self.rank = defaultdict(lambda: 0)          # rank is used to determine the order of trains                  
        self.curr_block = defaultdict(lambda: 0)
        self.curr_occupy = {}                
        self.curr_duration = {}
        self.init_moment = {}       
        
        '''The dictionary showing the operating duration for each train of the system at the current moment.
        curr_duration : dictionary
            Key: train number 'tn'
            Value: duration of train number 'tn' has been traveling at this moment, unit in seconds
        '''
        # define which siding that late/fast train surpass previous/slow trains
        self.isPass = defaultdict(lambda: float('inf'))
        # in order to solve problem: the number of trains is not the rank of trains. I use dict rank[n]
        self.rank = defaultdict(lambda: 0)
        self.tn_by_rank = {}
        
        self.weight = defaultdict(lambda: 0)
    
    def train(self, env):
        '''
        This function describes all the actions for each train object in the simulator of each refreshing time (Discrete Event Simulator).
        Each self.refresh is the time increment for the train actions to be taken.
        
        >>>e.g. approach_block, leaving_block, etc. as train's actions (built-in functions below) for each self.refresh time.
        >>>Although not written in Class, the train are supposed to be re-written in objects.
        '''   
        def get_curr_block(tn):
            """Encapsulated function to determine concurrent block and total blocked distance of a train:
            
            (at each moment)
            the accumulative distance traveled by a train. 
            the current block number of a train.
            
            Function or returns: 
                Update the (curr_block) dictionary
            
            curr_block : dictionary
                Key: train number 'tn'
                Value: current block number for this train  
                
            Notes:
            ------
                Calculate distance[tn] first, and then update the two dictionaries.
                coord_mp[tn] is the current distance from the origin of coordinates. 
            
            To-do:
            ------
                The relationships and logics need to be normalized to eliminate the more than/less than signs. 
                Merge two directions into one single judgment logic.   
            """
            # if (coord_mp > block_begin), block go further; if (coord_mp < block_end), block go close.
            if tn == 0:     # avoid initializing train number 0 (int) in the default dictionaries. 
                            # who?
                pass
            else:
                if self.curr_mp[tn] not in self.blk_boundaries:
                    for i in range(len(self.blk_interval)):
                        if self.blk_interval[i][0] < self.curr_mp[tn] < self.blk_interval[i][1]:
                            self.curr_occupy[tn] = I.open(self.blk_interval[i][0], self.blk_interval[i][1]) 
                            self.curr_block[tn] = i
                else:
                    if self.curr_spd[tn] != 0:
                        idx = self.blk_boundaries.index(self.curr_mp[tn])
                        self.curr_occupy[tn] = I.open(blk_interval[i-1][0], blk_interval[i][1])
                        self.curr_block[tn] = sorted([i-1, i])
                    if self.curr_spd[tn] == 0:
                         pass
 
        def approach_block(tn, blk_idx):
            # Approach is a status that the tn_th train is approaching the blk_idx_th block.
            # After the refresh time the train still does not enter the block.
            if self.curr_spd[tn] > 0:
                if self.curr_mp[tn] + self.curr_spd[tn] * self.refresh < self.blk_interval[blk_idx][0]:
                    #print 'approaching, MP: '+' train '+str(tn) +' '+ str(round(self.curr_mp[tn] + self.curr_spd[tn] * self.refresh))+' DoS has been: '+str(self.curr_duration[tn]-self.DoS_strt_t_ticks)  
                    return True 
            if self.curr_spd[tn] < 0:
                if self.curr_mp[tn] + self.curr_spd[tn] * self.refresh > self.blk_interval[blk_idx][1]:
                    return True
        
        def leaving_block(tn, blk_idx):
            # Leaving is a status that the tn_th train is leaving the blk_idx_th block.
            # Before and after the refresh time, the train had left the block.
            if self.curr_spd[tn] > 0 and self.curr_mp[tn] > self.blk_interval[blk_idx][1]: 
                #print 'leaving, MP: '+' train '+str(tn) +' '+ str(round(self.curr_mp[tn] + self.curr_spd[tn] * self.refresh))+' DoS has been: '+str(self.curr_duration[tn]-self.DoS_strt_t_ticks)  
                return True 
            if self.curr_spd[tn] < 0 and self.curr_mp[tn] < self.blk_interval[blk_idx][0]:
                return True
        
        def in_block(tn, blk_idx):
            # In_block is a status that the tn_th train is in the blk_idx_th block.
            # Before and after the refresh time, the train is in the block.
            if self.curr_spd[tn] != 0: 
                if self.blk_interval[blk_idx][0] < self.curr_mp[tn] <= self.blk_interval[blk_idx][1]: 
                    if self.blk_interval[blk_idx][0] < self.curr_mp[tn] + self.curr_spd[tn] * self.refresh <= self.blk_interval[blk_idx][1]:
                        #print 'within, MP: '+' train '+str(tn) +' '+ str(round(self.curr_mp[tn] + self.curr_spd[tn] * self.refresh))+' DoS has been: '+str(self.curr_duration[tn]-self.DoS_strt_t_ticks)  
                        return True    
                
        def enter_block(tn, blk_idx):
            # Enter is a status that the tn_th train is entering the blk_idx_th block.
            # Before the refresh time, the train was not in the block.
            # After the refresh time, the train was in the block.
            if not self.blk_interval[blk_idx][0] < self.curr_mp[tn] <= self.blk_interval[blk_idx][1]:
                if self.blk_interval[blk_idx][0] < self.curr_mp[tn] + self.curr_spd[tn] * self.refresh <= self.blk_interval[blk_idx][1]:
                    return True 
        
        def skip_block(tn, blk_idx):
            # Skip is a status that the tn_th train is skiping the blk_idx_th block.
            # Before the refresh time, the train was appoarching the block.
            # After the refresh time, the train was leaving the block.
            if not self.blk_interval[blk_idx][0] < self.curr_mp[tn] < self.blk_interval[blk_idx][1]:
                if self.curr_spd[tn] > 0:
                    if self.curr_mp[tn] + self.curr_spd[tn] * self.refresh > self.blk_interval[blk_idx][1]:
                        if self.curr_mp[tn] < self.blk_interval[blk_idx][0]:
                            print 'Warning: refresh too short, DoS got skipped'
                            return True 
                if self.curr_spd[tn] < 0:
                    if self.curr_mp[tn] + self.curr_spd[tn] * self.refresh < self.blk_interval[blk_idx][0]:
                        if self.curr_mp[tn] > self.blk_interval[blk_idx][1]: 
                            print 'Warning: refresh too short, DoS got skipped'
                            return True
        
        def exit_block(tn, blk_idx):
            # Exit is a status that the tn_th train is exiting the blk_idx_th block.
            # Before the refresh time, the train was in the block.
            # After the refresh time, the train was not in the block.
            if self.blk_interval[blk_idx][0] < self.curr_mp[tn] <= self.blk_interval[blk_idx][1]: 
                if not self.blk_interval[blk_idx][0] < self.curr_mp[tn] + self.curr_spd[tn] * self.refresh < self.blk_interval[blk_idx][1]:
                    return True 
        
        
        
        #=======================================================================
        # def train_proceed(tn, delta_t):
        #     get_curr_block(tn)
        #     update_rank()
        #     
        #     next_blk_idx = 
        #     prev_blk_idx = 
        #     
        #     if self.blk_interval[self.curr_block[tn]][0] <= self.curr_mp[tn] + self.curr_spd[tn] * delta_t <= self.blk_interval[self.curr_block[tn]][1]:
        #         self.curr_mp[tn] += self.curr_spd[tn] * delta_t
        #     elif next_avail(tn):
        #         
        #     enter_block(tn, self.curr_block[tn] + 1):
        #         self.curr_mp[tn] += self.curr_mp[tn] + 1
        #         get_curr_block(tn)
        #     elif enter_block(tn, self.curr_block[tn] - 1):
        #         self.curr_mp[tn] += 
        #                
        #     rank_tn_to_follow = self.rank[tn] - 1
        #     tn_to_follow = self.tn_by_rank[rank_tn_to_follow]
        #      
        #     if in_block(tn, self.curr_block[tn]):
        #         self.curr_mp[tn] += self.curr_spd[tn] * delta_t
        #         self.curr_duration[tn] += self.refresh * 60
        #     if enter_block(tn, self.curr_block[tn] + 1):
        #         if abs(self.curr_block[tn_to_follow] - self.curr_block[tn]) > 1:
        #             if self.rank[tn] -  
        #=======================================================================
         
        
        def DoS_reach_blk_end(tn, blk_idx):
            '''Not yet implemented time update, only coord_mp now.
            '''
            
            if self.curr_spd[tn] > 0:   
                self.curr_mp[tn] = self.blk_interval[blk_idx][1]
            if self.curr_spd[tn] < 0:
                self.curr_mp[tn] = self.blk_interval[blk_idx][0]
            if self.curr_spd[tn] == 0:
                if self.max_speed > 0:
                    self.curr_mp[tn] = self.blk_interval[blk_idx][1]
                if self.max_speed < 0:
                    self.curr_mp[tn] = self.blk_interval[blk_idx][0]
            print 'DoS Reaching End Done', tn, self.curr_mp[tn], blk_idx
            
            
        '''Dictionary containing the concurrent rank for each train, with train number as keys. 
        rank : dictionary
            Key: train number 'tn'
            Value: current order of position (directional, no.1 on the 'rightmost')
        '''
        def update_rank():
            """Update the ranking for all concurrent trains in the system
            
            """
            sorted_distance = sorted(self.curr_mp.values(),reverse=True)
            for i in self.curr_mp.keys():
                self.rank[i] = 1 + sorted_distance.index(self.curr_mp[i])
            self.tn_by_rank  = {v : k for k, v in self.rank.items()}
        
        '''
        Below is the logics for the relationships among trains when the simulation is running. 
        The actions before the while loop is the initialization of the simulation. 
        '''   
        update_rank()           # initialize the rank dictionary
        hdw_stpwatch = 0                # hdw_stpwatch is a stop watch with refreshing time, counting the reminder time before another new train is generated in minutes. 
        np.random.seed()
        #self.curr_spd[1] = np.random.normal(self.mph_exp/60.0, self.mph_dev/60.0)      # speed in miles per minute, float division
        #self.weight[1] = np.random.randint(1, 4)        
        whileloopcount = 0
        the_last_action = 'None'
        while True:
            '''
            The while loop serves as the continuous simulation until the timeout funcion called at the end (yield env.timeout())
            This is the application of the simpy library. Needs to be explained later. 
            '''
            whileloopcount += 1
            #print zip(self.curr_mp.keys(),self.curr_mp.values())
            #print 'this is loop: ' +str(whileloopcount)
            
            '''Explain the while True loop
            '''
            '''First, draw the dynamic circle dots in the topology view 
            Notes:
            ------
                Initializing labels and colors
            ''' 
            plt.clf()
            self.labels.clear()
            self.pos_labels.clear()
            self.ncolor = []
            # default empty block to 'green'
            for i in range(len(self.pos)):
                self.ncolor.append('g')
            # default block which have siding to 'black'
            for i in self.siding:
                self.ncolor[i] = 'black'        
            #===================================================================
            '''20190401
            To do:
            HUGE problems with standard time.
            float problem when printing the events.  
            '''
            #===================================================================
            # headway in minutes, local variable, randomize every loop in the while True body
            headway = np.random.normal(self.hdw_exp_min, self.hdw_dev_min)
            while headway <= 0:
                headway = np.random.normal(self.hdw_exp_min, self.hdw_dev_min)  
            # because headway > hdw_stpwatch is possible, determine if there is a new train after a new refresh by the judgment below:
            if hdw_stpwatch < headway:  ## no need for a new train, do nothing
                hdw_stpwatch += self.refresh
            else:               ## need a new train and clear hdw_stpwatch
                hdw_stpwatch = headway % self.refresh   # clearing the hdw_stpwatch stop watch
                self.number += 1                # adding a new train, meanwhile assigning the train number as its identifier.
                spd_seed = np.random.normal(self.mph_exp/60.0, self.mph_dev/60.0) 
                while spd_seed <= 0:
                    spd_seed = np.random.normal(self.mph_exp/60.0, self.mph_dev/60.0)    
                self.max_speed[self.number] = spd_seed
                self.curr_spd[self.number] = spd_seed                                          # speed in miles per minute
                self.init_moment[self.number] = self.clock_time + hdw_stpwatch * 60 
                self.curr_duration[self.number] = hdw_stpwatch * 60                         # in seconds because of the ticks are in seconds
                self.weight[self.number] = np.random.randint(1, 4)
                # update coord_mp[tn] and block status for the newly generated train
                self.curr_mp[self.number] += self.curr_spd[self.number] * hdw_stpwatch    # miles/min * mins
            
            get_curr_block(self.number)
            """The block above ONLY determine the need to initialize a new train.
            """
            #===================================================================
            
            #===================================================================
            '''Starting below includes both DoS and overtaking policies. Needs to be separated.
            The for loop iterates all the online trains and their neighbors to determine if there is overtaking or holding actions to be taken. 
            Below is the major part to be re-written and split.
            '''
            update_rank()
            # for x in xrange(1, self.number + 1):        # for all current trains, starting from the first of the queue
            for tn in self.curr_mp.keys():                
                #print tn, self.curr_mp[tn], self.curr_block[tn], self.blk_interval[self.curr_block[tn]], 'crr_spd', self.curr_spd[tn]
                # tn = self.rank[x]                        # train number x (1,2,3,4,5...) is now ranked as tn
                self.one_detail = {}                    # initialize the one_detail dictionary
                '''Dictionary containing the momentary information and behaviors of a train, with train number as keys.
                one_detail : dictionary
                    Key: train number 'tn'
                    Value: dictionary for key-value pairs with lifetime attributes of a train 
                ''' 
                        
                # update time line in seconds accrues by refresh, refresh in minutes, time in seconds
                # note the key here is tn instead of x, because the actions are based on the order of the queue. 
                
                '''If DoS happens:
                '''
                get_curr_block(tn)
                if self.is_DoS:
                    # self.curr_duration[tn] is the duration for a train has been traveling in seconds, concurrent life of time for train 'tn'
                    # so self.clock_time is the current global time. Notice that time is a dictionary, with keys as integer train identifiers.
                    if self.clock_time < self.DoS_strt_t_ticks or self.clock_time > self.DoS_stop_t_ticks:
                        self.curr_spd[tn] = self.max_speed[tn]
                        self.curr_mp[tn] += self.curr_spd[tn] * self.refresh
                
                    else:
                        if approach_block(tn, self.DoS_block) or in_block(tn, self.DoS_block) or leaving_block(tn, self.DoS_block):
                            self.curr_spd[tn] = self.max_speed[tn]
                            self.curr_mp[tn] += self.curr_spd[tn] * self.refresh
                            
                        elif enter_block(tn, self.DoS_block):
                            DoS_reach_blk_end(tn, self.curr_block[tn])
                            self.curr_spd[tn] = 0
                        elif skip_block(tn, self.DoS_block):
                            DoS_reach_blk_end(tn, self.curr_block[tn])
                            self.curr_spd[tn] = 0
                        elif exit_block(tn, self.DoS_block):
                            DoS_reach_blk_end(tn, self.curr_block[tn])
                            self.curr_spd[tn] = 0
                        elif self.curr_spd[tn] == 0:
                            self.curr_mp[tn] += self.curr_spd[tn] * self.refresh
                            print 'Train: ',tn, 'curr spd: ', self.curr_spd[tn], ' MP:', self.curr_mp[tn], self.T.strftime("%Y-%m-%d %H:%M:%S", self.T.localtime(self.clock_time))
                            
                    self.curr_duration[tn] += self.refresh * 60
                    get_curr_block(tn)
                else:
                    self.curr_mp[tn] += self.curr_spd[tn] * self.refresh
                    self.curr_duration[tn] += self.refresh * 60
                    get_curr_block(tn)

                
                '''When overtaking happens:
                Traverse the rank of all train, if low rank catch up high rank, it should follow instead of surpass. 
                Unless there is a siding.
                '''
                    
                if i > 0 is False:

                    # The block position of prev train and current train
                    '''
                    Overtake Policy:

                      # when block small enough and speed large enough, there would be a bug
                    '''
                    if self.curr_block[self.rank[x - 1]] <= self.curr_block[self.rank[x]] + 1:
                        for sd in self.siding:
                            if self.curr_block[self.rank[x - 1]] == sd:
                                if self.curr_spd[self.rank[x-1]] < self.curr_spd[self.rank[x]]:
                                    self.rank[x], self.rank[x - 1] = self.rank[x - 1], self.rank[x]
                                    self.curr_mp[self.rank[x]] -= self.curr_spd[self.rank[x]] * self.refresh
                                    get_curr_block(i)
                                break

                            elif sd == self.siding[-1]:
                                pass
                                #self.curr_mp[self.rank[x]] = self.sum_block_dis[self.rank[x]] - self.block[self.curr_block[self.rank[x]]]
                                #self.curr_mp[self.rank[x]] = max(0, self.curr_mp[self.rank[x]])
                                #--------------------- get_curr_block(i)

                # set the color of train node
                k = self.curr_block[i]
                if 0 < k < len(self.pos):
                    self.ncolor[k-1] = 'r'
                if 0 < k < len(self.pos):
                    self.labels[k] = i
                    self.pos_labels[k] = self.pos[k]

#                 self.one_detail['duration'] = round(self.curr_spd[i], 2)
                
                self.one_detail['duration'] = self.curr_duration[tn]
                self.one_detail['coord_mp(miles)'] = self.curr_mp[tn]
                
                t_stamp_std = self.T.strftime("%Y-%m-%d %H:%M:%S", self.T.localtime(self.clock_time))    # set the first train as reference time
                self.one_schedule[t_stamp_std] = self.one_detail       
                #-------------------------- print self.one_schedule.values()[:5]
                self.all_schedule[tn][t_stamp_std] = self.one_detail 
                
                the_last_action = 'train number: '      +str(tn)\
                                    +' as rank: '       +str(self.rank[tn])\
                                    +' approach MP: '   +str(self.curr_mp[tn])\
                                    +' at ticks: '      +str(self.curr_duration[tn])[-9:]
                
                                    
            # draw the train map
            # nx.draw_networkx_nodes(self.G, self.pos, node_color=self.ncolor, node_size=200)
            # nx.draw_networkx_labels(self.G, self.pos_labels, self.labels, font_size=10)
            # nx.draw_networkx_edges(self.G, self.pos)
            
            # networkX pause 0.01 seconds
            # plt.pause(0.05)
            #print sorted(self.all_schedule[50].keys())[-5:], sorted([self.all_schedule[50][i]['coord_mp(miles)'] for i in sorted(self.all_schedule[50].keys())[-5:]])
            
            '''
            To explain the usage of the scripts below, refer simpy documents or ask Kai directly.
            '''
            self.clock_time += self.refresh * 60
            yield env.timeout(self.refresh*60)
        
    
    def run(self):
        '''
        Serves as the simpy envrionment for DES simulation. 
        To explain the usage of the scripts below, refer simpy documents or ask Kai directly.
        '''
        # use simpy library to define the process of train system
        env = simpy.Environment()
        env.process(self.train(env))
        duration = self.stop_t_ticks - self.strt_t_ticks
        env.run(until=duration)

    def string_diagram(self):
        '''
        To draw the string diagram based on the schedule dictionary for all the trains. 
        '''
        # draw the train working diagram
        '''begin comment__train stringline diagram'''
        x = []; y = []
        for tn in self.all_schedule:
            x.append([])
            y.append([])

            for t_stamp_std in self.all_schedule[tn]:  #t_stamp_std is all the time stamps
                x[tn-1].append((time.mktime(time.strptime(t_stamp_std, "%Y-%m-%d %H:%M:%S"))-self.strt_t_ticks)/3600)
                y[tn-1].append(self.all_schedule[tn][t_stamp_std]['coord_mp(miles)'])
                #print x[tn-1]
            
            y[tn-1] = [n for (m,n) in sorted(zip(x[tn-1],y[tn-1]))] 
            x[tn-1] = sorted(x[tn-1])
            
            
                
            #self.tn_by_rank  = {v : rk for rk, v in self.rank.items()}
        
        plt.title('Result Analysis')
        for n in range(len(x)-1):
            if n % 4 == 0:
                plt.plot(x[n], y[n], color='green')
            if n % 4 == 1:
                plt.plot(x[n], y[n], color='blue')
            if n % 4 == 2:
                plt.plot(x[n], y[n], color='red')
            if n % 4 == 3:
                plt.plot(x[n], y[n], color='black')

        plt.legend()
        plt.xlabel('time /hours')
        plt.ylabel('coord_mp /miles')
        plt.show()
        '''end comment__train stringline diagram'''

        # print self.all_schedule
        return self.all_schedule

if __name__ == '__main__':
    a = single_train('2018-01-01 00:00:00', '2018-01-01 12:00:00', True, '2018-01-01 05:00:00', '2018-01-01 09:30:00', 05, [20, 30, 40], [20] * 60)
    a.run()
    print a.blk_interval
    print a.blk_interval[18]
    print '2018-01-01 09:00:00', '2018-01-01 09:30:00'
    a.string_diagram()
    

class multi_dirc:
    '''
    Needs to be re-written after the single direction is done.
    Better to integrate multi-dirction with single direction. 
    '''

    def __init__(self, strt_t, stop_t, dis_miles, buffer_list):
        # define parameters
        self.buffer = 3
        self.all_schedule_A = {}
        self.dis = dis_miles
        self.buffer_list = buffer_list
        self.T = time
        self.strt_t_ticks = time.mktime(time.strptime(strt_t, "%Y-%m-%d %H:%M:%S"))
        self.stop_t_ticks = time.mktime(time.strptime(stop_t, "%Y-%m-%d %H:%M:%S"))
        self.number = 1
        self.one_schedule_A = {}
        self.one_schedule_B = {}
        self.one_detail_A = {}
        self.one_detail_B = {}
        self.curr_spd_A = {}
        self.curr_spd_B = np.random.normal(3, 0.5)
        self.distance_A = {1: 0}
        self.curr_duration = {1: self.strt_t_ticks}
        env = simpy.Environment()
        env.process(self.train(env))
        duration = self.stop_t_ticks - self.strt_t_ticks
        env.run(until=duration)

    def train(self, env):
        # n is used for create many "one_detail_A", otherwise all "one_schedule_A" will be the same
        n = 0
        index_A = 0
        index_B = len(self.buffer_list)

        while True:
            np.random.seed()
            self.curr_spd_A[self.number] = np.random.normal(3, 0.5) # miles per minute
            headway = np.random.normal(20, 5)
            self.all_schedule_A[self.number] = {}
            self.curr_duration[self.number] = self.strt_t_ticks
            self.distance_A[self.number] = 0

            for i in xrange(1, self.number+1):
                self.one_detail_A[n] = {}
                self.curr_duration[i] += headway * 60
                self.distance_A[i] += self.curr_spd_A[i] * headway
                distance_B = (self.curr_spd_B * (self.clock_time - self.strt_t_ticks)) / 60
                if i > 1:
                    if self.distance_A[i] > self.distance_A[i-1] - self.curr_spd_A[i-1] * self.buffer:
                        self.distance_A[i] = self.distance_A[i-1] - self.curr_spd_A[i-1] * self.buffer
                dirc = 'A'
                self.one_detail_A[n]['dirc'] = dirc
                self.one_detail_A[n]['speed_A(mils/min)'] = self.curr_spd_A[i]
                self.one_detail_A[n]['distance_A(miles)'] = self.distance_A[i]
                self.one_detail_A[n]['headway(mins)'] = headway

                # get A and B pass through which buffer
                for x in range(len(self.buffer_list)):
                    if self.buffer_list[x] < self.distance_A[i]:
                        index_A = x + 1
                for x in range(len(self.buffer_list), 0):
                    if self.dis - self.buffer_list[x] < distance_B:
                        index_B = x + 1
                # A and B
                if index_B - index_A == 2:
                    time_arrive_buffer_A = self.buffer_list[index_A-1] / self.curr_spd_A[i]
                    time_arrive_buffer_B = (self.dis - self.buffer_list[index_B-1]) / self.curr_spd_B
                    if time_arrive_buffer_A < time_arrive_buffer_B:
                        self.distance_A[i] -= (time_arrive_buffer_B - time_arrive_buffer_A) * self.curr_spd_A[i]
                    else:
                        distance_B -= (time_arrive_buffer_A - time_arrive_buffer_B) * self.curr_spd_B

                self.one_detail_A[n]['buffer_index'] = index_A
                t_stamp_std = self.T.strftime("%Y-%m-%d %H:%M:%S", self.T.localtime(self.curr_duration[i]))
                self.one_schedule_A[t_stamp_std] = self.one_detail_A[n]
                self.all_schedule_A[i][t_stamp_std] = self.one_schedule_A[t_stamp_std]
                n += 1
            self.number += 1
            yield env.timeout(headway * 60)

    def string_diagram(self):
        return self.all_schedule_A


