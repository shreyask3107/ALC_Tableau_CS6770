import xmltodict
import ast
import re

with open("MAN-P7-Input-KB.xml") as xml_file:
     
    kb_dict = xmltodict.parse(xml_file.read())
    xml_file.close()

with open("MAN-P7-Input-Query.xml") as xml_file:
     
    query_dict = xmltodict.parse(xml_file.read())
    xml_file.close()

with open("MAN-P6-KB.xml") as xml_file:
     
    abox_dict = xmltodict.parse(xml_file.read())
    xml_file.close()
    
print('EXAMPLE 1: The one given in Sample Folder')


Ind = []  # Noting all individuals
for i in abox_dict['KB']['DifferentIndividuals']['INDIVIDUAL']:
  Ind.append(i)

Rel = {}   # All relations are saved in this variable
for r in abox_dict['KB']['ObjectProperty']:
  Rel[r['ROLE']] = {}

Class = {}  # All concepts are saved in here
for f in abox_dict['KB']['Individual']:
  if 'Types' in f:
    if f['Types']['CONCEPT'] not in Class:
      Class[f['Types']['CONCEPT']] = []
    Class[f['Types']['CONCEPT']].append(f['INDIVIDUAL'])
  if 'Facts' in f:
    if f['Facts']['FACT']['ROLE'] not in Rel:
      Rel[f['Facts']['FACT']['ROLE']] = {}
    if f['INDIVIDUAL'] not in Rel[f['Facts']['FACT']['ROLE']]:
      Rel[f['Facts']['FACT']['ROLE']][f['INDIVIDUAL']] = []


    Rel[f['Facts']['FACT']['ROLE']][f['INDIVIDUAL']].append(f['Facts']['FACT']['INDIVIDUAL'])
    
print('Classes:',Class)
print('Relations:',Rel)


# Query parsing
Q = [query_dict['KB']['Individual']['INDIVIDUAL']]

nnf = query_dict['KB']['Individual']['Types']
# print(nnf)
str_nnf = str(nnf)
str_nnf = str_nnf.replace('[', '')
str_nnf = str_nnf.replace(']', '')

str_nnf = str_nnf.replace('{', '[')
str_nnf = str_nnf.replace('}', ']')
str_nnf = str_nnf.replace(':', ',')
str_nnf = str_nnf.replace("'CONCEPT', ", '')
str_nnf = str_nnf.replace("'NOT', [", "['!', ")
# str_nnf = str_nnf.replace("],", ",")
str_nnf = str_nnf.replace("'OR', [", "['|', ")
str_nnf = str_nnf.replace("'AND', [", "['&', ")
str_nnf = str_nnf.replace("'EXISTS', [", "['*', ")
str_nnf = str_nnf.replace("'FORALL', [", "['?', ")
str_nnf = str_nnf.replace("'ROLE', ", '')

# print(str_nnf)
Q.append(ast.literal_eval(str_nnf)[0])


def notof(X):
  if isinstance(X,str):
    return ['!',X]
  elif X[0] == '!':
    return X[1]
  else:
    assert False,  "WRONG FORMAT"    
    
    
# Fill L from Abox
def abox2L(Rel,Class):
  L = {};Rr = {}
  for c in Class:
    for a in Class[c]:
      try:
        L[a].append(c)
      except:
        L[a] = [c]
  for R in Rel:
    for a in Rel[R]:
      for b in Rel[R][a]:
        try:
          Rr[a+','+b].append(R)
        except:
          Rr[a+','+b] = [R]
  return L,Rr      


L0 ,R0= abox2L(Rel,Class)
print('Before adding not of query:',L0,R0)

# The negated query is converted to NNF in this function
def addQuery(Q,L,R):  
  a = Q[0]
  c = Q[1]
  if isinstance(Q,list):
    if c[0]=='*':
      Tnow = ['?',c[1],notof(c[2])]
      rel = Tnow[1]
      cl = Tnow[2]
      L[a].append(Tnow)
      for item in L:
        if a+','+item in R and rel in R[a+','+item] and cl not in L[item]:
          L[item].append(cl)
      return L,R    

    elif c[0]=='?':
      Tnow = ['*',c[1],notof(c[2])]
      rel = Tnow[1]
      cl = Tnow[2]
      Lnew = L.copy()
      Rnew = R.copy()
      for a in L:
        Lnew[a].append(Tnow)
        for item in L:
          if not ((a+','+item) in R and rel in R[a+','+item] and cl in L[item]):
            Lnew['var'+a] = [cl]
            Rnew[a+','+'var'+a] = [rel]
      return Lnew,Rnew      
    elif c[0]=='!':
      L[a].append(c[1])
      return L,R

    else:
      assert False; "WRONG FORMAT" 
  else:
    L[a].append(notof[c])   
    return L,R      
    
L1,R1 = addQuery(Q,L0,R0)

print('After adding not of query:',L1,R1)

# TBox Encoding Takes place here
Tbox = []
for s in kb_dict['KB']['Class']:
  nnf = s['EquivalentTo']
  # print(nnf)
  str_nnf = str(nnf)
  str_nnf = str_nnf.replace('[', '')
  str_nnf = str_nnf.replace(']', '')

  str_nnf = str_nnf.replace('{', '[')
  str_nnf = str_nnf.replace('}', ']')
  str_nnf = str_nnf.replace(':', ',')
  str_nnf = str_nnf.replace("'CONCEPT', ", '')
  str_nnf = str_nnf.replace("'NOT', [", "['!', ")
  # str_nnf = str_nnf.replace("],", ",")
  str_nnf = str_nnf.replace("'OR', [", "['|', ")
  str_nnf = str_nnf.replace("'AND', [", "['&', ")
  str_nnf = str_nnf.replace("'EXISTS', [", "['*', ")
  str_nnf = str_nnf.replace("'FORALL', [", "['?', ")
  str_nnf = str_nnf.replace("'ROLE', ", '')
  
  str_nnf = '[' + str_nnf[1:].replace("[[", "['|', [")

  rep_str = re.search("\['[A-Za-z]+'\]", str_nnf)
  if rep_str:
    str_nnf = str_nnf.replace(str(rep_str.group()), "['!', " +str(rep_str.group())[1:])

  # print(str_nnf)
  Tbox.append(ast.literal_eval(str_nnf)[0])


for i in range(len(Tbox)):
  for j in range(len(Tbox[i])):
    # print(j)
    if type(Tbox[i][j]) == list:
      if Tbox[i][j][0] == '|' or Tbox[i][j][0] == '&':
        # print(len(Tbox[i][j]))

        if len(Tbox[i][j]) != 3:
          temp = Tbox[i][j]
          Tbox[i][j] = [Tbox[i][j][0], temp[:3], temp[3]]


def isConsistent(L):
  for a in L:
    for c in L[a]:
      if ['!',c] in L[a]:
        print('Inconsistancy: ',c,', ',['!',c],' in L(',a,'):',L[a])
        return False
  return True
  
  
def evaluate(L,R,Tbox):
  print('L : ',L)
  print('R : ',R)
  print('Tbox : ',Tbox)

  if len(Tbox)==0:
    return isConsistent(L)
  if not isConsistent(L):
    return False

  Tnow = Tbox[0]
  if isinstance(Tnow,list):
    if Tnow[0] == '&':
      print('AND RULE:',Tnow[0])
      Tnew = Tnow[1:]+Tbox[1:]+[Tbox[0]]
      return evaluate(L,R,Tnew)

    elif Tnow[0] == '|':
      print('OR RULE:',Tnow[0])
      Tnew1 = [Tnow[1]]+Tbox[1:]+[Tbox[0]]  
      Tnew2 = [Tnow[2]]+Tbox[1:]+[Tbox[0]]
      return evaluate(L,R,Tnew1) or evaluate(L,R,Tnew2)

    elif Tnow[0] == '*':
      print('THERE EXISTS RULE:',Tnow[0])
      Lnew = L.copy()
      Rnew = R.copy()
      rel = Tnow[1]
      cl = Tnow[2]

      for a in L:
        Lnew[a].append(Tnow)
        for item in L:
          if not ((a+','+item) in R and rel in R[a+','+item] and cl in L[item]):
            Lnew['var'+a] = [cl]
            Rnew[a+','+'var'+a] = [rel]
      return evaluate(Lnew,Rnew,Tbox[1:])    

    elif Tnow[0] == '?': 
      print('FOR ALL RULE:',Tnow[0])
      Lnew = L.copy()
      Rnew = R.copy()
      rel = Tnow[1]
      cl = Tnow[2]

      for a in Lnew:
        Lnew[a].append(Tnow)
        for item in L:
          if a+','+item in R and rel in R[a+','+item] and cl not in L[item]:
            Lnew[item].append(cl)
      return evaluate(Lnew,Rnew,Tbox[1:]+[Tbox[0]]) 

    elif Tnow[0] == '!':      
      for a in L:
        L[a].append(Tnow)
      return evaluate(L,R,Tbox[1:])
      
    else:
      assert False, "WRONG SYNTAX"  
  else:
    for a in L:
      L[a].append(Tnow)
    return evaluate(L,R,Tbox[1:])      

def printEntailment(L,R,Tbox):
  e = evaluate(L,R,Tbox)
  if e:
    print('Model exists => Query not entailed by KB')
  else:
    print('Model does not exists => Query is entailed by KB')  
    
printEntailment(L1,R1,Tbox)



## More examples to Test our Methodology
print ('#############################################################################################')
print('#############################################################################################')
print('#############################################################################################')

print('EXAMPLE 2')
L = {'a':['T']}
R = {}
Tbox = ['C',['!','C']]

print('Is KB consistent?:',evaluate(L,R,Tbox))

print('EXAMPLE 3')

Rel = {'Likes':{'Lucy':['Apple']}}
Class = {'Fruit':['Apple'],'Person':['Lucy']}
L ,R= abox2L(Rel,Class)
Tbox = []
print(L)
print(R)

# Given that Lucy likes apple and no other information about
# her likes/dislikes, can we conclude that Lucy likes fruits?
Query = ['Lucy',['*','Likes','Fruit']]

Lq,Rq = addQuery(Query,L,R)
print(Lq)
print(Rq)

printEntailment(Lq,Rq,Tbox)

print('EXAMPLE 4')

Rel = {'Likes':{'Lucy':['Apple']}}
Class = {'Fruit':['Apple'],'Person':['Lucy']}
L ,R= abox2L(Rel,Class)
Tbox = []
print('Before adding not of query')
print(L)
print(R)

# Given that Lucy likes apple and no other information about
# her likes/dislikes, can we conclude that Lucy likes ONLY fruits?

Query = ['Lucy',['?','Likes','Fruit']]


Lq,Rq = addQuery(Query,L,R)

print('After adding not of query')
print(Lq)
print(Rq)

printEntailment(Lq,Rq,Tbox)

print('EXAMPLE 5')

Rel = {'R':{}}
Class = {'T':['a']}

# Does { T(a), C in D } entail (∃R•C in ∃R•D)?
L ,R= abox2L(Rel,Class)
Tbox = [['|',['!','C'],'D'],
        ['&',['*','R','C'],['?','R',['!','D']]]] #<= not of Query
        
print('Just checking consistancy of system')
print(L)
print(R)

printEntailment(L,R,Tbox)

