from QuantLib import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import numpy
import os
from utils import datetime_to_quantdate, term_structure

inputPath = os.path.abspath(os.path.dirname(os.getcwd())) + str('/Data/')

filename_bond = 'bond_pricing.xlsx'
filename_calendar = 'calendar.xlsx'
filename_date = 'date.xlsx'

bond_data = pd.read_excel(inputPath + filename_bond, sheetname = 'daily')
bond_info = pd.read_excel(inputPath + filename_bond, sheetname = 'info')
bond_calendar = pd.read_excel(inputPath + filename_calendar)
bond_080010 = pd.read_excel(inputPath + filename_bond, sheetname = '080010_data')


# fit the yield curve
curve_day_count = Actual365Fixed()
curve_convention = Unadjusted
yield_curve = term_structure(bond_data, bond_info, bond_calendar, 30, 12, 2008, curve_day_count, curve_convention, 'Piecewise Log Cubin Discount')
curve_handle = YieldTermStructureHandle(yield_curve)

#----------------------------------------------------------------------------------------------------------------------------
# pricing a bond
bond_yield = np.array(bond_080010['YTM'])
bond_datee = np.array(bond_080010['Date'])
name = np.array(bond_info['GB'])
coupon = np.array(bond_info['coupon']) / 100

bond_date = np.array(bond_calendar['calendarDate'])
bond_isOpen = np.array(bond_calendar['isOpen'])
chinaCal = China(China.IB)
issue_date_array = np.array(bond_info['Issue'])
termination_date_array = np.array(bond_info['Terminate'])
maturity = []
issue = []

for i in range(termination_date_array.shape[0]):
    maturity.append(datetime_to_quantdate(termination_date_array[i], '%Y-%m-%d'))
    issue.append(datetime_to_quantdate(issue_date_array[i], '%Y-%m-%d'))

today_set = []
for i in range(bond_datee.shape[0]):
    today_set.append(datetime_to_quantdate(bond_datee[i], '%Y/%m/%d'))

# schedule
tenor = Period(Semiannual)
day_count = Actual365Fixed()
business_convention = Unadjusted
compounding_frequency = Semiannual
compounding = Compounded
date_generation = DateGeneration.Backward
month_end = False
schedule = Schedule(issue[7], maturity[7], tenor, chinaCal, business_convention,
                    business_convention, date_generation, month_end)


# build a fixed rate bond object
coupon_rate = coupon[7]
coupons = [coupon_rate]
bondSettlementDays = 0
face_value = 100
result_array = []
#bond_yield = fixed_rate_bond.bondYield(day_count, compounding, compounding_frequency)
print('Bond: %s' % name[7])

for k in range(len(bond_datee)):

    #yield_new = CashFlows.yieldRate(fixed_rate_bond.cashflows(), npv, day_count, compounding, compounding_frequency, True)
    fixed_rate_bond = FixedRateBond(bondSettlementDays, face_value, schedule, coupons, day_count, business_convention)
    #bond_engine = DiscountingBondEngine(curve_handle)
    #fixed_rate_bond.setPricingEngine(bond_engine)
    interest = InterestRate(bond_yield[k] / 100, day_count, compounding, compounding_frequency)
    clean_price = fixed_rate_bond.cleanPrice(bond_yield[k] / 100, day_count, compounding, compounding_frequency, today_set[k])
    dirty_price = fixed_rate_bond.dirtyPrice(bond_yield[k] / 100, day_count, compounding, compounding_frequency, today_set[k])
    accrued = fixed_rate_bond.accruedAmount(today_set[k])
    npv = CashFlows.npv(fixed_rate_bond.cashflows(), interest, False, today_set[k])
    macaulay_duration = CashFlows.duration(fixed_rate_bond.cashflows(), interest, Duration.Macaulay, False, today_set[k])
    modified_duration = CashFlows.duration(fixed_rate_bond.cashflows(), interest, Duration.Modified, False, today_set[k])
    convexity = CashFlows.convexity(fixed_rate_bond.cashflows(), interest, False, today_set[k])
    #print(yield_new)

    #print(bond_yield[k] / 100)
    print(bond_datee[k])
    print("Clean Price: %.4f" % clean_price)
    print("Dirty Price: %.4f" % dirty_price)
    print("Accrued Amount: %.6f" % accrued)
    print("Yield: %.4f%%" % (bond_yield[k]))
    print("NPV': %.4f%%" % (npv))
    print("Macaulay Duration: %.4f" % macaulay_duration)
    print("Modified Duration: %.4f" % modified_duration)
    print("Convexity: %.4f" % convexity)

    print("CashFlows:")
    for m in range(len(fixed_rate_bond.cashflows())):
        print("Date: %s   CashFlow: %.4f" % (fixed_rate_bond.cashflows()[m].date(), fixed_rate_bond.cashflows()[m].amount()))
    print()

    result_array.append([name[7], bond_datee[k], clean_price, dirty_price, bond_yield[k], accrued, npv,
                         macaulay_duration, modified_duration, convexity])


df_result = pd.DataFrame(result_array, columns = ['GB', 'Date', 'Clean Price', 'Dirty Price', 'YTM', 'Accrued Amount', 'NPV', 'Macaulay Duration', 'Modified Duration', 'Convexity'])
outputPath = os.path.abspath(os.path.dirname(os.getcwd())) + str('/Result/')
df_result.to_csv(outputPath + 'result_080010_wind.csv', index = False)



