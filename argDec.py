def argDec(args):
  res = {}
  n = 0
  while n<len(args):
    i = args[n]
    if i[0]=='-':
      if len(i)>2:
        for j in i[1:]:
          res[j] = None
      elif n==len(args)-1 or args[n+1][0]=='-':
        res[i[1]] = None
      else:
        res[i[1]] = ''
        while n!=len(args)-1 and args[n+1][0]!='-':
          res[i[1]] += args[n+1]+' '
          n += 1
        res[i[1]] = res[i[1]].strip()
    n+=1
        
      
  return res

if __name__=="__main__":
  import sys
  print argDec(sys.argv)
