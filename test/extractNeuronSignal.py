__author__ = 'malbert'

s1 = [n.mean(b.signal(i)[63:75,330:352,75:100]) for i in range(100)]
s2 = [n.mean(b.signal(i)[75:82,610:631,273:293]) for i in range(100)]
s3 = [n.mean(b.signal(i)[41:48,558:575,163:188]) for i in range(100)]