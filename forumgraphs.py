from igraph import *




def bettergraphgen(edges):
  i = 0
  userdict = {}
  for x in edges:
     if userdict.setdefault(x[0],i) == i: i += 1
     if userdict.setdefault(x[1],i) == i: i += 1
  
  newedges = [(userdict[x[0]], userdict[x[1]]) for x in edges]
  g = Graph(newedges)
  
  for k, v in userdict.iteritems():
    g.vs[v]['label']= k
  return g
  
def community_kernighan_lin_neg(g, num=2, parts=None):
  if not parts:
    parts = [0]*len(g.vs)
  unused = range(len(g.vs))
  bestmod = 1
  while( unused) :
    currentmod = 1
    choice = -1
    for x in unused:
      oldpart=parts[x]
      for i in range(1,num):
        
        parts[x] = (parts[x]+1) % num
        tempmod = g.modularity(parts)
        if tempmod < currentmod:
          choice = (x,i)
          currentmod = tempmod
      parts[x] = oldpart
    
    parts[choice[0]] = (parts[choice[0]]+choice[1]) % num
    unused.remove(choice[0])
    if currentmod < bestmod: 
      bestmod = currentmod
      bestparts = list(parts)
      #print bestmod, bestparts
  
  return bestparts
  

def graphgen(users):
  #userset = []
  #for x in users:
  #  userset.extend(x.keys())
  
  #userset = set(userset)
  
  
  userdict = {}
  edgedict = {}
  k=0
  for x in users:
    tempusers = sorted(x.keys())
    n = len(tempusers)
    for i in range(n):
      userdict.setdefault(tempusers[i], 0)
      userdict[tempusers[i]] += 1
      if i == (n-1): break
      for j in range(i+1, n):
        edgedict.setdefault((tempusers[i],tempusers[j]), 0)
        edgedict[(tempusers[i],tempusers[j])] += 1
    print "Finished usergroup: " +str(k)
    k += 1
 
  numv = len(userdict.keys())
  print "Preparing graph with " + str(numv)+ " vertices."
  g = Graph(numv)
  print "Graph initialized ... "
  g.vs['label'] = userdict.keys()
  print "Vertices labeled ... "
  g.vs['qmax'] = userdict.values()
  print "Qmaxes assigned ... "
  edges = [ (g.vs(label_eq=x[0])[0].index,g.vs(label_eq=x[1])[0].index) for x in edgedict.keys()]
  print "Edges processed ... "
  g.add_edges(edges)
  print "Edges assigned ... "
  g.es['qmax'] = edgedict.values()
  print "Edge qmaxes assigned."
  return g
    