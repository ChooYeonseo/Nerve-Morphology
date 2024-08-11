import pandas as pd
import sys, os
import math

file_dir = f'./data/sn_data.csv'
GLOBAL_MIN = 0.01
BRANCH_MAX = 4

df = pd.read_csv(file_dir)
LR = ['L', 'R']
CADAVER_NAME = ['23-21', '23-27']

class LegModel:

    def __init__(self, name):
        # Leg는 종류 상관 없이 무조건 9개의 꼭짓점을 가지는 도형
        # Initial point (0, 0)은 tip으로 지정

        self.leg_coord = [[0, 0] for i in range(10)]
        '''
        leg_coord의 구성을 살펴보자.
        leg_coord[0] = tip
        leg_coord[1] = mid
        leg_coord[2] = distal ant. boarder
        leg_coord[3] = proximal ant. boader
        leg_coord[4] = ant. knee joint line
        leg_coord[5] = med. knee joint line
        leg_coord[6] = proximal med. boader
        leg_coord[7] = distal med. boarder
        leg_coord[8] = lat
        '''
        self.lr = LR.index(name[-1]) #0 if left, 1 if right
        self.cadaver_id = CADAVER_NAME.index(name[:-1])
        self.name = name

        self.landmarks = [[0, 0] for i in range(6)]
        '''
        landmarks[0] = tip
        landmarks[1] = mid
        landmarks[2] = cp
        landmarks[3] = mid12
        landmarks[4] = mid10
        landmarks[5] = lat
        '''

    def get_coord(self):
        self.setcoor()
        return self.leg_coord, self.landmarks
        

    def getattributedict(self):
        L = list(df[self.name])
        for i, item in enumerate(L):
            try:
                new_item = float(item)
            except ValueError:
                new_item = str(item)
            L[i] = new_item
        
        result = dict(zip(list(df['Unnamed: 0']), L))
        assert len(result) == 43, "The length of column for attribute dictionary doesn't match!"
        return result
    
    def setcoor(self):
        dict = self.getattributedict()
        #============some constants============
        alpha = 0.3
        beta0 = 0.35
        l_mhdiff = 0.9
        beta1 = beta0 * 0.7
        gamma0 = 0.4
        gamma1 = 0.7
        t = 0.1
        #======================================
        
        x_mid10, y_mid10 = self.get_mid10(dict, alpha, gamma1)
        x_mid12, y_mid12 = self.get_mid12(dict, alpha, gamma1)
        assert x_mid10 == x_mid12, "x coordinate of mid10 and mid12 doesn't match."

        self.leg_coord[0] = [0, 0]
        self.leg_coord[9] = [0, 0]
        self.leg_coord[1] = [alpha * dict["width_mm"], dict["tip_mid"]]
        self.leg_coord[2] = [gamma0 * self.leg_coord[1][0], beta0 * y_mid10]
        self.leg_coord[8] = [- (1-alpha) * dict["width_mm"], self.leg_coord[1][1] * l_mhdiff]
        self.leg_coord[7] = [gamma1 * self.leg_coord[8][0], self.leg_coord[2][1] * l_mhdiff]
        self.leg_coord[3] = [self.leg_coord[2][0], dict["leg_length"] * 10 * (1- t)]
        self.leg_coord[4] = [gamma0 * 1.4 * self.leg_coord[1][0], dict["leg_length"] * 10]
        self.leg_coord[5] = [- (1-alpha) * dict["width_mm"], dict["leg_length"] * 10]
        self.leg_coord[6] = [gamma1 * self.leg_coord[8][0], dict["leg_length"] * 10 * (1- t)]

        self.landmarks[0] = self.leg_coord[0]
        self.landmarks[1] = self.leg_coord[1]
        self.landmarks[2] = [self.leg_coord[7][0], dict["tip_cp"]*10]
        self.landmarks[3] = [x_mid12, y_mid12]
        self.landmarks[4] = [x_mid10, y_mid10]
        self.landmarks[5] = self.leg_coord[8]

    def get_mid10(self, dict, alpha, gamma1):
        x_mid10 = - dict["width_mm"] * (1-alpha) * gamma1
        y_mid10 = math.sqrt(100**2 - x_mid10**2)

        return x_mid10, y_mid10
    
    def get_mid12(self, dict, alpha, gamma1):
        x_mid12 = - dict["width_mm"] * (1-alpha) * gamma1
        y_mid12 = math.sqrt(144**2 - x_mid12**2)

        return x_mid12, y_mid12
    
class NerveMap:
    def __init__(self, leg_coord, landmark, name):
        
        self.leg = leg_coord
        self.lm = landmark
        self.name = name
        self.dictionary = self.getattributedict()
    
    def getattributedict(self):
        L = list(df[self.name])
        for i, item in enumerate(L):
            try:
                new_item = float(item)
            except ValueError:
                new_item = str(item)
            L[i] = new_item
        
        result = dict(zip(list(df['Unnamed: 0']), L))
        assert len(result) == 43, "The length of column for attribute dictionary doesn't match!"
        return result
    
    def getorderoflm(self):
        dictionary = self.dictionary
        
        landmark = {}
        annote_leg = ["TIP", "MID", "CP", "MID12", "MID10", "LAT"]
        for i, an in enumerate(annote_leg):
            landmark[an] = self.lm[i]
        landmark["BP"] = [0, dictionary['tip_bp'] * 10]

        landmark = dict(sorted(landmark.items(), key = lambda item: -item[1][1]))
        return landmark

    def keyorderprinter(self):
        landmark_dictionary = self.getorderoflm()
        landmark_dictionary.pop('BP')
        landmark_dictionary.pop('LAT')

        dictionary = self.dictionary
        n = len(landmark_dictionary)
        result = "##########\n"
        cnt = 1
        for key, value in landmark_dictionary.items():
            key = key.lower()
            result += key
            result += ": "
            key += '_brch'
            value_str = ""
            for i in range(int(dictionary[key])):
                value_str += (str(cnt) + " ")
                cnt += 1
            result = result + value_str + "\n"

        result += "##########"

        print(result)
        return None
    
    def get_oriented_values(self, name):
        name = name.lower()
        dictionary = self.dictionary
        landmark_dictionary = self.getorderoflm()

        name += '_sn'
        
        x_coord = []
        if name == "cp_sn":
            x_coord.append(landmark_dictionary["CP"][0])
            return x_coord
            
        for i in range(1, BRANCH_MAX+1):
            if str(dictionary[name + str(i)]) not in ['nan', 'Nmb']:
                if name == "tip_sn":
                    x_coord.append(float(dictionary[name + str(i)]) + landmark_dictionary['TIP'][0])
                if name == "mid_sn":
                    x_coord.append(float(dictionary[name + str(i)]) + landmark_dictionary['MID'][0])
                if name == "mid10_sn":
                    x_coord.append(-float(dictionary[name + str(i)]) + landmark_dictionary['MID10'][0])
                if name == "mid12_sn":
                    x_coord.append(-float(dictionary[name + str(i)]) + landmark_dictionary['MID12'][0])

        return sorted(x_coord)
    
    def NervePlottingPoints(self):
        dictionary = self.dictionary
        landmark_dictionary = self.getorderoflm()
        pop_L = ['BP', 'LAT']
        for i in pop_L:
            landmark_dictionary.pop(i)

        Nerve_point_number = 0
        
        for key, value in landmark_dictionary.items():
            key = key.lower() + '_brch'
            Nerve_point_number += int(dictionary[key])
        print("Total Nerve Point is: {}".format(Nerve_point_number))

        points = list(landmark_dictionary.keys())
        point_dict = {}
        assert_cnt = 0
        for N in points:
            temp_x = self.get_oriented_values(N)
            for x in temp_x:
                assert_cnt += 1
                point_dict[assert_cnt] = [float(x), landmark_dictionary[N][1]]
        
        assert assert_cnt == Nerve_point_number, "NERVE POINT DOESN'T MATCH!"

        return Nerve_point_number, point_dict