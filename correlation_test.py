import db_handler
import websim
import correlation

c = correlation.Correlation(1)
#c.request_several(['f838811ba41a421ea2a993fac447440b', 'e86d7948449449c9b9264fd45a872914', '2abd00ab916042df9addc0bbb92645e8', '23203453305048599977d15dbd1c44dd', 'd8ac4db69c7b43288ec1ccdab4c45542', '4ebc11aa196c4a128a55dd187db317a3', '95c55b460029421bb047231f3994d478', '3a47b524f5774c5eaab0afbc21bf79f9', '4d9f4c43a95841e383afc143e646b647', 'f22261104c1d42f58d7bd04bcdd667fa'])
print c.correlation(49, 51, False)
