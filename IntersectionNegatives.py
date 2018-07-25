def Intersection(s):
    user = s
    negativewords = ['not','n\'t']
    together = user.split()
    test = [word for word in together if word.lower() in negativewords]
    if len(test)%2==1:
        return('isNegative')
    else:
        return('notNegative')

print(Intersection("Georgie shouldn't not one of the best dogs ever"))
