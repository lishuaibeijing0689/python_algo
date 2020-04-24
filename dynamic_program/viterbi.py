import sys

states = ('Rainy', 'Sunny', 'Snowy', 'Thunder')
 
observations = ('walk', 'playSnow', 'clean', 'clean', 'shop', 'clean', 'walk', 'shop', 'clean', 'playSnow', 'scare', 'walk')
 
start_probability = {'Rainy': 0.4, 'Sunny': 0.3, 'Snowy': 0.2, 'Thunder': 0.1}
 
transition_probability = {
    'Rainy' : {'Rainy': 0.5, 'Sunny': 0.2, 'Snowy': 0.15, 'Thunder': 0.15},
    'Sunny' : {'Rainy': 0.1, 'Sunny': 0.5, 'Snowy': 0.3, 'Thunder': 0.1},
    'Snowy' : {'Rainy': 0.4, 'Sunny': 0.2, 'Snowy': 0.3, 'Thunder': 0.1},
    'Thunder' : {'Rainy': 0.4, 'Sunny': 0.2, 'Snowy': 0.1, 'Thunder': 0.3},
    }
 
emission_probability = {
    'Rainy' : {'walk': 0.1, 'shop': 0.3, 'clean': 0.4, 'playSnow':0.1, 'scare':0.1},
    'Sunny' : {'walk': 0.4, 'shop': 0.2, 'clean': 0.1, 'playSnow':0.1, 'scare':0.1},
    'Snowy' : {'walk': 0.2, 'shop': 0.1, 'clean': 0.2, 'playSnow':0.4, 'scare':0.1},
    'Thunder' : {'walk': 0.1, 'shop': 0.1, 'clean': 0.4, 'playSnow':0.1, 'scare':0.3},
}

def viterbi_output(states,observations,start_probability,transition_probability,emission_probability):
    """
    states:隐状态
    observations:观察状态
    start_probability:初始概率
    transition_probability:转换概率(某个隐状态转换到某个隐状态)
    emission_probability:发射概率(某个隐状态转换到某个观察状态)
    算法思路:
        目的:根据三天的观察状态,计算最有可能的三天天气隐状态
        根据:得到最后一天的概率后,其中概率最大的即表示该条状态链是最有可能的隐状态链
        方法:
            第一天概率:隐状态的初始概率*该状态到第一天的观察状态的发射概率
            其他天概率:前一天隐状态的概率*前一天隐状态到当天隐状态的转换概率*当天隐状态到当天观察状态的发射概率
        关键:
            1.并不需要保存每一天的状态,实际上每天的循环计算中只会用到前一天的数据即可(因此V这个变量实际上长度为2即可)
            2.路径的保存
    """
    V = [{}]#V[时间][天气]=概率
    path = {}#保存路径
    #第一天
    for state in states:
        V[0][state]=start_probability[state]*emission_probability[state][observations[0]]
        path[state]=[state]
        print "第一天概率估计:(天气:%s,概率:%f)" % (state,V[0][state])
    #其他时间
    for day in range(1,len(observations)):
        print "第%d天概率估计:" % (day+1)
        V.append({})
        newPath = {}
        for day_s in states:
            (prop,state) = max([V[day-1][s]*transition_probability[s][day_s]*emission_probability[day_s][observations[day]],s]for s in states)
            V[day][day_s]=prop
            newPath[day_s] = path[state]+[day_s]
            print "\t假设当前隐状态为:%s,得到最大概率:%f,对应前一天隐状态:%s" % (day_s,prop,state)
        path = newPath
    return max([(V[len(observations)-1][prop],path[prop])for prop in V[len(observations)-1]])

if __name__ == '__main__':
#argv[1]表示计算观察的天数
    print viterbi_output(states,observations[:int(sys.argv[1])],start_probability,transition_probability,emission_probability)
