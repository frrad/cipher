import re, random

letOrder = ['e', 't', 'a', 'o', 'i', 'n', 's', 'h', 'r', 'd', 'l', 'c', 'u', 'm', 'w', 'f', 'g', 'y', 'p', 'b', 'v', 'k', 'j', 'x', 'q', 'z']
wordPath = '/usr/share/dict/american-english'
WLMIN = 1
WLMAX = 10
tries = 15


######################
####ANALYSIS TOOLS####
######################


#return character frequency table
def freqTable(text):
    table = dict()
    for let in text:
        if let in table:
            table[let]+= 1
        else:
            table[let] = 1
    return table

def showTable(fTable):
    for let in tableOrder(fTable):
        print let, "+" *fTable[let]

#returns list in descending frequency order from table
def tableOrder(table):
    return sorted(table.keys(), reverse=True, key=lambda letter: table[letter])



#####################
####SUBSTITUTIONS####
#####################

#given a list of letters ordered by frequency return a 
#naive substitution rule
def naiveRule(order):
    sub = dict()
    for i, let in enumerate(order):
        sub[let] = letOrder[i]
    return sub

def substitute(string, rules):
    ans = ""
    for let in string:
        ans += rules[let]
    return ans

def caesar(offset):
    sub = dict()
    for i in range(26):
        to = (i+1 + offset)%26
        if to == 0 : to = 26
        From = i+1
        sub[numLet(From)] = numLet(to)
    return sub
 
def flesh(rule):
    start = set('abcdefghijklmnopqrstuvwxyz')
    end = set('abcdefghijklmnopqrstuvwxyz')

    for key in rule:
        start.discard(key)
        end.discard(rule[key])

    add = list(start)
    for let in add:
        rule[let] = end.pop()

#fleshes out to complete rule while changing as little as possible
def flush(rule):
    start = set('abcdefghijklmnopqrstuvwxyz')
    end = set('abcdefghijklmnopqrstuvwxyz')

    for key in rule:
        start.discard(key)
        end.discard(rule[key])

    add = list(start)
    for let in add:
        if let in end:
            rule[let] = let
            end.discard(let)
        else:
            rule[let] = end.pop()

def randSub():
    subs = dict()
    grouse = list('abcdefghijklmnopqrstuvwxyz')
    for x in xrange(25,-1 ,-1):
        to = random.randint(0,x)
        subs[numLet(x+1)] = grouse[to]
        grouse[to], grouse[x] = grouse[x], grouse[to]

    return subs



#if we know that a means b... 
def knownText(a,b):
    table = dict()
    for i,let in enumerate(a):
        table[let] = b[i]
    return table


#######################
####SCORE FUNCTIONS####
#######################

wordlist = set()

def listinit(minL, maxL):
    plain = re.compile('^[a-z]*$')
    f = open(wordPath,'r')
    dictionary = f.read().split()
    for line in dictionary:
        # print plain.match(line)
        if plain.match(line) and minL <= len(line) <= maxL:
            wordlist.add(line)

#how many substrings of given string are in our list?
#a, b gives range of substring lengths to check
def bruteCheck(cleartext, a,b):
    salmon = [0 for x in range(len(cleartext))]
    for x in range(a,b+1):
        for start in range(len(cleartext) - x +1):
            substr = cleartext[start:start + x]
            # print "<<"+substr
            if substr in wordlist:
                # print substr
                for z in range(x):
                    salmon[z + start] += 1
    total = 0
    for score in salmon:
        if score > 0:
            total +=1
    return total


#slightly better: don't allow overlap
def bCheck2(cleartext, a,b):
    salmon = [0 for x in range(len(cleartext))]
    total = 0

    for x in range(b,a-1, -1):
        # print x
        for start in range(len(cleartext) - x +1):
            substr = cleartext[start:start + x]
            # print "<<"+substr
            if substr in wordlist:
                # print substr
                total += x*x
                for z in range(x):
                    salmon[z + start] += 1
                    cleartext = help(cleartext,z + start)
    # for score in salmon:
    #     if score > 0:
    #         total +=1
    return total

####################
####GENETIC ALGO####    
####################

#breed two substitution rules where n controls how much
#comes from sub1. the closer to 26, the more comes from it
def breed(sub1, sub2, n):
    start = set('abcdefghijklmnopqrstuvwxyz')
    end = set('abcdefghijklmnopqrstuvwxyz')
    newRule = dict()
    for x in xrange(n):
        keep = numLet(random.randint(1,26))
        newRule[keep] = sub1[keep]
        start.discard(keep)
        if sub1[keep] in end: end.remove(sub1[keep])

    temp = list(start)

    for key in temp:
        if sub2[key] in end:
            newRule[key] = sub2[key]
            start.remove(key)
            end.remove(sub2[key])

    temp = list(start)

    #hopefully pop is randomish...
    for remains in temp:
        newRule[remains] = end.pop()

    return newRule

def epoch(pool, time):
    for x in xrange(time):
        # print x
        pile = []
        for i, rule in enumerate(pool):
            for x in xrange(i):
                pile.append(breed(rule, pool[x], 20))

        pile = sorted(pile, reverse=True, key=lambda rule: bCheck2(substitute(ciphertext,rule),WLMIN,WLMAX))

        pool = pile[:len(pool)]

    return pool

############
####MISC####
############

def letNum(letter):
    return ord(letter.lower())-96

def numLet(number):
    return chr(number + 96)

def help(word, pos):
    tasty = list(word)
    tasty[pos] = ' '
    return "".join(tasty)



#####################################

ciphertext = 'DGFMVXCRLCWMIDHDRLCHHDHVKLCAKYMAIHCAHEFIHZDRLHMUDRLFMVZSLIHLGGMZHLRLAHVCEEFFMVODEEMRLZYMQLFMVZDQQLKDCHLWZMSELQICAKGDAKFMVCZLZLCKFGMZUZLCHLZYXCEELAULI'
ciphertext = ciphertext.lower()
listinit(WLMIN,WLMAX)


frequency = freqTable(ciphertext)

metapool = []

for epochN in xrange(1,tries):
    
    #seed the pool
    pool = []

    for x in xrange(3):
        dumb = naiveRule(tableOrder(frequency))
        flesh(dumb)
        pool.append(dumb)

    for x in xrange(26):
        pool.append(randSub())

    pool = epoch(pool, 20)


    top = pool[0]
    topClear = substitute(ciphertext,top)
    print str(epochN) + "\t" + topClear +" "+ str(bCheck2(topClear,WLMIN,WLMAX))


    metapool.extend(pool[:5])


metapool = epoch(metapool,20)

for epochN in xrange(1,tries):
    celar = substitute(ciphertext,metapool[epochN])
    print celar + " " +str(bCheck2(celar, WLMIN, WLMAX))

print len(ciphertext)


 