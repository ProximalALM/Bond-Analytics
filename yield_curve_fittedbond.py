from QuantLib import *
import pandas as pd
#import seaborn as sb
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import os
from utils import datetime_to_quantdate, term_structure

# read file
#inputPath = 'X:/temp/quantlib/Data/'
inputPath = os.path.abspath(os.path.dirname(os.getcwd())) + str('/Data/')

filename_bond = 'bond_yield_curve.xlsx'
filename_calendar = 'calendar.xlsx'
bond_data = pd.read_excel(inputPath + filename_bond, sheetname = 'daily')
bond_info = pd.read_excel(inputPath + filename_bond, sheetname = 'info')
bond_calendar = pd.read_excel(inputPath + filename_calendar)

day_count = ActualActual(ActualActual.Bond)
convention = Following
ts0 = term_structure(bond_data, bond_info, bond_calendar, 7, 11, 2018, day_count, convention, 'Fitted Bond Discount')
times = np.linspace(0.0, 49, 360)
yields_spot = [ts0.zeroRate(t, Continuous, Annual).rate()*100 for t in times ]  #dc, Compounded, frequency
yields_discount = [ts0.discount(t) for t in times]
yields_forward = [ts0.forwardRate(t, t + 0.5, Continuous, Annual).rate() * 100 for t in times]

y = list(zip(times, yields_spot))
plt.plot(times, yields_spot, label = 'spot rate')
plt.plot(times, yields_discount, label = 'discount rate')
plt.plot(times, yields_forward, label = 'forward rate')
plt.title('Yield Curve by Fitted Bond Discount Discount')
plt.legend(loc = 0)
plt.show()
print(pd.DataFrame(y, columns = ["Maturities", "Curve"], index = [''] * len(times)))


