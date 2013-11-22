def cumulativeAbility():
    a = float(raw_input())
    b = float(raw_input()) 
    while b:
        a = a*0.8+b*0.2
        b = float(raw_input())
        print a
    return

def computeExpertise(x, y):
    return 1 / (1 + 1 / ((x - y) * 100) ** 2)
