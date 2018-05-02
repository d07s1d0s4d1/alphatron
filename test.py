import sys
#import websim
import db_handler
#import generators.tree_generator as tg
#import generators.parser as ps
#import generators.alpha_stream_generator as asg
from numpy import random
import time
#import submitter

db = db_handler.DBHandler()
f = open('market_data','r')
data = [code[:-1] for code in f]
print data
for code1 in data:
    for code2 in data:
        if code1 != code2:
            print '(' + code1 + '/' + code2 + ')'
            codeID = db.add_code('(' + code1 + '/' + code2 + ')', 'trivial relationships', 'trivial relationships')
            db.add_sending(codeID)
f.close()
'''
tree = tg.dict_tree(ps.parse('(((high + low)/2 - close)/stddev((high+low)/2-close,90)^3))'))
print tree
print tg.count_market_data_consts(tree)
'''
'''
sb = submitter.Submitter(1)
sb.submit_alpha(12425)
'''
'''
sys.setrecursionlimit(3000)
code = 'signedpower(scale(signedpower(scale(rank(scale(rank(scale(rank(scale(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))+scale(scale(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))))*rank(((rank((sum(returns,10))/(sum(sum(returns,2),3))))-(rank(decay_linear(correlation(((vwap)*(0.318108))+((open)*((1)-(0.318108))),sum(adv20,37.2467),13.557),12.2883))))*((0)-(1)))))*rank(scale(signedpower((sales/assets),2.31412848785))+scale(rank(signedpower(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))),2.37631548601))*rank(signedpower((0)-((1)*((rank((sum(returns,10))/(assets)))*(rank((returns)*(cap))))),1.89398773505)))+scale(((0)-((1)*(delta((((close)-(low))-(((1)*(((1)-((open)/(close)))^(1)))-(close)))/((high)+(low)),9)))))+scale(rank(scale(rank(((rank(decay_linear(delta(IndNeutralize(close, industry),2.25164),8.22237))-rank(decay_linear(correlation(((vwap*0.318108)+(open*(1-0.318108))),sum(adv20,37.2467),13.557),12.2883)))*(0-1)))*rank((sales/assets))))*rank(((0)-((1)*(delta((((close)-(low))-(((1)*(((1)-((open)/(close)))^(1)))-(close)))/((high)+(low)),9)))))))))*rank(signedpower(signedpower(signedpower(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))),2.37631548601),2.89391942926),2.21432856512)))+scale(rank(signedpower(((correlation(adv20,open,5))+(((high)+(low))/(2)))-(close),2.07129816083))*rank(scale(rank((((1-rank((stddev(returns,2)/stddev(returns,5))))+(1-rank(delta(close,1))))))*rank(scale(rank((((0)-((1)*(rank(delta(delta(close,1),1)))))*(rank((open)-(delay(close,1)))))*(rank((open)-(delay(low,1)))))*rank((((0)-((1)*(rank(delta(delta(close,1),1)))))*(rank((open)-(delay(close,1)))))*(rank((open)-(delay(low,1))))))))+scale(rank((sales/assets))*rank(scale(rank(scale(rank(scale(rank((rank((open - (sum(vwap, 10) / 10))) * (0-1 * abs(rank((close - vwap))))))*rank((((correlation(adv20,low,5)+((high+low)/2))-close)))))*rank(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))))*rank(scale(rank(scale(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))+scale(scale(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))))*rank(((rank((sum(returns,10))/(sum(sum(returns,2),3))))-(rank(decay_linear(correlation(((vwap)*(0.318108))+((open)*((1)-(0.318108))),sum(adv20,37.2467),13.557),12.2883))))*((0)-(1)))))))))),2.0560390918))+scale(signedpower(signedpower(scale(rank(signedpower((scale((rank(((rank(decay_linear(delta(IndNeutralize(close,industry),2.25164),8.22237)))-(rank(decay_linear(correlation(((vwap)*(0.318108))+((open)*((1)-(0.318108))),sum(adv20,37.2467),13.557),12.2883))))*((0)-(1))))*(rank((sales)/(assets)))))+(scale(scale((rank(signedpower((((high)*(low))^(0.5))-(vwap),0.32795580334)))*(rank((sales)/(assets)))))),2.92393838016))*rank(signedpower(signedpower(signedpower(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))),2.37631548601),2.89391942926),2.21432856512))),1.27211171721),2.38426010591))+scale(signedpower(scale(rank(scale(rank((sales/assets))*rank((sales/assets))))*rank(scale(rank(scale(rank(signedpower(scale(rank(signedpower((((high*low)^0.5)-vwap),0.32795580334))*rank((sales/assets)))+scale(scale(rank(signedpower((((high*low)^0.5)-vwap),0.32795580334))*rank((sales/assets)))),2.92393838016))*rank(signedpower(scale((rank(decay_linear(correlation(((vwap)*(0.318108))+((open)*((1)-(0.318108))),sum(adv20,37.2467),13.557),12.2883)))*(rank((sales)/(assets)))),2.37631548601))))*rank(signedpower(signedpower(signedpower(signedpower((0)-(((close)/(assets))^(2)),1.28983019101),2.71444189734),2.82949262762),2.75285018217))))),2.93302211777))+scale(rank(scale(rank((0)-((1)*((rank((sum(returns,10))/(assets)))*(rank((returns)*(cap))))))*rank((sales/assets))))*rank(signedpower(signedpower(signedpower(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))),2.37631548601),2.89391942926),2.21432856512)))+scale(signedpower((((0)-((1)*(rank((open)-(delay(high,1))))))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))+scale(scale(signedpower((((0)-((1)*(rank((open)-(delay(high,1))))))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762)))+scale(rank((((correlation(adv20,low,5)+((high+low)/2))-close)))*rank(scale(rank(signedpower(scale((((correlation(adv20,low,5)+((high+low)/2))-close)))+scale(rank(scale(rank((((0-1*rank((open-delay(high,1))))*rank((open-delay(close,1))))*rank((open-delay(low,1)))))*rank((0-1*rank(((stddev(abs((close-open)),5)+(close-open))+correlation(close,open,10)))))))*rank(scale(rank(scale(rank(((rank(decay_linear(delta(IndNeutralize(close, industry),2.25164),8.22237))-rank(decay_linear(correlation(((vwap*0.318108)+(open*(1-0.318108))),sum(adv20,37.2467),13.557),12.2883)))*(0-1)))*rank((sales/assets))))*rank(((0)-((1)*(delta((((close)-(low))-(((1)*(((1)-((open)/(close)))^(1)))-(close)))/((high)+(low)),9)))))))),2.35847590781))*rank(scale((rank(((high)*(rank((open)-(delay(close,1)))))*(rank((open)-(delay(low,1))))))*(rank((0)-((1)*(rank(((stddev(abs((close)-(open)),5))+((close)-(open)))+(correlation(close,open,10))))))))))))+scale((rank((0)-((1)*((rank((open)-(delay(close,1))))*(rank((returns)*(cap)))))))*(rank(((1)-(rank((stddev(returns,2))/(stddev(returns,5)))))+((1)-(rank(delta(close,1)))))))+scale(signedpower(signedpower(signedpower(((0)-(((close)/(assets))^(2))),1.28983019101),2.71444189734),2.88974652283))+scale(signedpower((((high*low)^0.5)-vwap),0.32795580334))+scale(scale(signedpower((((high*low)^0.5)-vwap),0.32795580334)))+scale(rank((sales/assets))*rank((sales/assets)))+scale(rank(scale(rank(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))))*rank(scale(rank(scale(rank(((rank(decay_linear(delta(IndNeutralize(close, industry),2.25164),8.22237))-rank(decay_linear(correlation(((vwap*0.318108)+(open*(1-0.318108))),sum(adv20,37.2467),13.557),12.2883)))*(0-1)))*rank((sales/assets))))*rank(((0)-((1)*(delta((((close)-(low))-(((1)*(((1)-((open)/(close)))^(1)))-(close)))/((high)+(low)),9)))))))))*rank(signedpower((rank((open - (sum(vwap, 10) / 10))) * (0-1 * abs(rank((close - vwap))))),2.87644983386)))+scale(scale(signedpower(scale(rank(scale(rank(scale(rank(scale(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))+scale(scale(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))))*rank(((rank((sum(returns,10))/(sum(sum(returns,2),3))))-(rank(decay_linear(correlation(((vwap)*(0.318108))+((open)*((1)-(0.318108))),sum(adv20,37.2467),13.557),12.2883))))*((0)-(1)))))*rank(scale(signedpower((sales/assets),2.31412848785))+scale(rank(signedpower(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))),2.37631548601))*rank(signedpower((0)-((1)*((rank((sum(returns,10))/(assets)))*(rank((returns)*(cap))))),1.89398773505)))+scale(((0)-((1)*(delta((((close)-(low))-(((1)*(((1)-((open)/(close)))^(1)))-(close)))/((high)+(low)),9)))))+scale(rank(scale(rank(((rank(decay_linear(delta(IndNeutralize(close, industry),2.25164),8.22237))-rank(decay_linear(correlation(((vwap*0.318108)+(open*(1-0.318108))),sum(adv20,37.2467),13.557),12.2883)))*(0-1)))*rank((sales/assets))))*rank(((0)-((1)*(delta((((close)-(low))-(((1)*(((1)-((open)/(close)))^(1)))-(close)))/((high)+(low)),9)))))))))*rank(signedpower(signedpower(signedpower(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))),2.37631548601),2.89391942926),2.21432856512)))+scale(rank(signedpower(((correlation(adv20,open,5))+(((high)+(low))/(2)))-(close),2.07129816083))*rank(scale(rank((((1-rank((stddev(returns,2)/stddev(returns,5))))+(1-rank(delta(close,1))))))*rank(scale(rank((((0)-((1)*(rank(delta(delta(close,1),1)))))*(rank((open)-(delay(close,1)))))*(rank((open)-(delay(low,1)))))*rank((((0)-((1)*(rank(delta(delta(close,1),1)))))*(rank((open)-(delay(close,1)))))*(rank((open)-(delay(low,1))))))))+scale(rank((sales/assets))*rank(scale(rank(scale(rank(scale(rank((rank((open - (sum(vwap, 10) / 10))) * (0-1 * abs(rank((close - vwap))))))*rank((((correlation(adv20,low,5)+((high+low)/2))-close)))))*rank(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))))*rank(scale(rank(scale(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))+scale(scale(signedpower((((0)-((1)*(returns)))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))))*rank(((rank((sum(returns,10))/(sum(sum(returns,2),3))))-(rank(decay_linear(correlation(((vwap)*(0.318108))+((open)*((1)-(0.318108))),sum(adv20,37.2467),13.557),12.2883))))*((0)-(1)))))))))),2.0560390918))+scale(signedpower(signedpower(scale(rank(signedpower((scale((rank(((rank(decay_linear(delta(IndNeutralize(close,industry),2.25164),8.22237)))-(rank(decay_linear(correlation(((vwap)*(0.318108))+((open)*((1)-(0.318108))),sum(adv20,37.2467),13.557),12.2883))))*((0)-(1))))*(rank((sales)/(assets)))))+(scale(scale((rank(signedpower((((high)*(low))^(0.5))-(vwap),0.32795580334)))*(rank((sales)/(assets)))))),2.92393838016))*rank(signedpower(signedpower(signedpower(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))),2.37631548601),2.89391942926),2.21432856512))),1.27211171721),2.38426010591))+scale(signedpower(scale(rank(scale(rank((sales/assets))*rank((sales/assets))))*rank(scale(rank(scale(rank(signedpower(scale(rank(signedpower((((high*low)^0.5)-vwap),0.32795580334))*rank((sales/assets)))+scale(scale(rank(signedpower((((high*low)^0.5)-vwap),0.32795580334))*rank((sales/assets)))),2.92393838016))*rank(signedpower(scale((rank(decay_linear(correlation(((vwap)*(0.318108))+((open)*((1)-(0.318108))),sum(adv20,37.2467),13.557),12.2883)))*(rank((sales)/(assets)))),2.37631548601))))*rank(signedpower(signedpower(signedpower(signedpower((0)-(((close)/(assets))^(2)),1.28983019101),2.71444189734),2.82949262762),2.75285018217))))),2.93302211777))+scale(rank(scale(rank((0)-((1)*((rank((sum(returns,10))/(assets)))*(rank((returns)*(cap))))))*rank((sales/assets))))*rank(signedpower(signedpower(signedpower(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))),2.37631548601),2.89391942926),2.21432856512)))+scale(signedpower((((0)-((1)*(rank((open)-(delay(high,1))))))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762))+scale(scale(signedpower((((0)-((1)*(rank((open)-(delay(high,1))))))*(rank((close)/(open))))*(rank((open)-(delay(low,1)))),2.82949262762)))+scale(rank((((correlation(adv20,low,5)+((high+low)/2))-close)))*rank(scale(rank(signedpower(scale((((correlation(adv20,low,5)+((high+low)/2))-close)))+scale(rank(scale(rank((((0-1*rank((open-delay(high,1))))*rank((open-delay(close,1))))*rank((open-delay(low,1)))))*rank((0-1*rank(((stddev(abs((close-open)),5)+(close-open))+correlation(close,open,10)))))))*rank(scale(rank(scale(rank(((rank(decay_linear(delta(IndNeutralize(close, industry),2.25164),8.22237))-rank(decay_linear(correlation(((vwap*0.318108)+(open*(1-0.318108))),sum(adv20,37.2467),13.557),12.2883)))*(0-1)))*rank((sales/assets))))*rank(((0)-((1)*(delta((((close)-(low))-(((1)*(((1)-((open)/(close)))^(1)))-(close)))/((high)+(low)),9)))))))),2.35847590781))*rank(scale((rank(((high)*(rank((open)-(delay(close,1)))))*(rank((open)-(delay(low,1))))))*(rank((0)-((1)*(rank(((stddev(abs((close)-(open)),5))+((close)-(open)))+(correlation(close,open,10))))))))))))+scale((rank((0)-((1)*((rank((open)-(delay(close,1))))*(rank((returns)*(cap)))))))*(rank(((1)-(rank((stddev(returns,2))/(stddev(returns,5)))))+((1)-(rank(delta(close,1)))))))+scale(signedpower(signedpower(signedpower(((0)-(((close)/(assets))^(2))),1.28983019101),2.71444189734),2.88974652283))+scale(signedpower((((high*low)^0.5)-vwap),0.32795580334))+scale(scale(signedpower((((high*low)^0.5)-vwap),0.32795580334)))+scale(rank((sales/assets))*rank((sales/assets)))+scale(rank(scale(rank(scale(rank(((0)-(((close)/(assets))^(2))))*rank((sales/assets))))*rank(scale(rank(scale(rank(((rank(decay_linear(delta(IndNeutralize(close, industry),2.25164),8.22237))-rank(decay_linear(correlation(((vwap*0.318108)+(open*(1-0.318108))),sum(adv20,37.2467),13.557),12.2883)))*(0-1)))*rank((sales/assets))))*rank(((0)-((1)*(delta((((close)-(low))-(((1)*(((1)-((open)/(close)))^(1)))-(close)))/((high)+(low)),9)))))))))*rank(signedpower((rank((open - (sum(vwap, 10) / 10))) * (0-1 * abs(rank((close - vwap))))),2.87644983386)))),0.879395068735)'
print code
print '\n', len(code)
res = ps.parse(code)
print res
res = tg.compile_alpha(tg.dict_tree(res))
print '\n', res
#res = tg.expr.parseString(code)
#print '\n', res
#res = tg.compile_alpha(tg.dict_tree(res))
#print '\n', res
'''
'''
code = '1-1*1*1-1'
#db = db_handler.DBHandler()
sys.setrecursionlimit(3000)
#code = db.get_sending_result(9)['code']
print len(code)
print '\n' + code
#code1 = db.get_sending_result(2500)['code']
#res = asg.treeCode(code, code1)
res = tg.expr.parseString(code)
#res = asg.truncateCode(code)
print '\n'
print res
res = tg.compile_alpha(tg.dict_tree(res))
print '\n', res
res = tg.expr.parseString(res)
#res = asg.truncateCode(code)
print '\n'
print res
res = tg.compile_alpha(tg.dict_tree(res))
print '\n', res
'''

'''
sys.setrecursionlimit(1000)
def test(i):
    i += 1
    print i
    test(i)

i = 0
test(i)
'''
'''
sys.setrecursionlimit(3000)
db = db_handler.DBHandler()
res1 = ''
res2 = ''
i = 0
while str(res1) == str(res2):
    print '\n------------------------------------------------------------------------------------------'
    i += 1
    print 'Number: ',i
    try:
        code = db.get_sending_result(i)['code']
    except:
        print '\nDB failed'
        continue
    #if '^' in code:
    #    print '\n^'
    #    continue
    print '\nlen code = ', len(code)
    print '\ncode: ', code
    t1 = time.time()
    #res1 = tg.compile_alpha(tg.dict_tree(ps.parse(code)))
    res1 = ps.parse(code)
    t2 = time.time()
    print '\nres1: ', res1
    x = t2 - t1
    print '\ntime1: ', x
    t1 = time.time()
    #res2 = tg.compile_alpha(tg.dict_tree(tg.expr.parseString(code)))
    res2 = tg.expr.parseString(code)
    t2 = time.time()
    print '\nres2: ', res2
    y = t2 - t1
    print '\ntime2: ', y
    print '\nt2/t1: ', y/x

print 'Failed code: ', code
'''