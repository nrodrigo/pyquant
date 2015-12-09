from random import randint

balls = ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'R', 'R', 'R']
balance = 0
attempts = 1000000
win_loss = 1

for i in range(0, attempts): 
    if balls[randint(0,9)] =='G':
        balance = balance + win_loss
    else:
        balance = balance - win_loss

print balance
