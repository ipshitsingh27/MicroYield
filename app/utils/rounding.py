import math

def calculate_roundoff(amount: float):
    if amount < 500:
        rounded = math.ceil(amount)
    elif amount <= 10000:
        rounded = math.ceil(amount / 10) * 10
    else:
        rounded = math.ceil(amount / 100) * 100

    roundoff = rounded - amount
    return roundoff, rounded