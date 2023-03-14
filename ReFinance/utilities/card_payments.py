def luhn(number):
    sum = 0

    for i, digit in enumerate(reversed(number)):
        n = int(digit)

        if i % 2 == 0:
            sum += n
        elif n >= 5:
            sum += n * 2 - 9
        else:
            sum += n * 2

    if sum % 10 == 0:
        return True
    else:
        return False