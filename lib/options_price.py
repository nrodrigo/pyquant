from math import *

"""
The python version of the Black Scholes formula as seen here:
http://www.espenhaug.com/black_scholes.html
"""
class Options_Price:

    def __init__(self):
        pass

    # Cumulative normal distribution
    @staticmethod
    def CND(X):
        (a1,a2,a3,a4,a5) = (
            0.31938153,
            -0.356563782,
            1.781477937, 
            -1.821255978,
            1.330274429)
        L = abs(X)
        K = 1.0 / (1.0 + 0.2316419 * L)
        w = 1.0 - 1.0 / sqrt(2*pi)*exp(-L*L/2.) * (a1*K + a2*K*K + a3*pow(K,3) +
            a4*pow(K,4) + a5*pow(K,5))
        if X<0:
            w = 1.0-w
        return w

    # Black Sholes Function
    #  S = stock price
    #  X = strike price of option
    #  T = time to expiration in years
    #  r = risk-free interest rate
    #  v = volatility
    @staticmethod
    def BlackScholes(CallPutFlag, S, X, T, r, v):
        S = float(S)
        X = float(X)
        T = float(T)
        r = float(r)
        v = float(v)
        d1 = (log(S/X) + (r+v*v/2.) * T) / (v * sqrt(T))
        d2 = d1 - v * sqrt(T)
        if CallPutFlag=='c':
            return S * Options_Price.CND(d1) - X * exp(-r * T) * Options_Price.CND(d2)
        else:
            return X * exp(-r * T) * Options_Price.CND(-d2) - S * Options_Price.CND(-d1)

