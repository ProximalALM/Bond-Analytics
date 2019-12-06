from QuantLib import *
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import inspect as ins
import os


def datetime_to_quantdate(bond_date, form):
    term_date = dt.datetime.strptime(bond_date, form)
    term_year = term_date.year
    term_month = term_date.month
    term_day = term_date.day
    temp_date = Date(term_day, term_month, term_year)

    return temp_date

def term_structure(bond_data, bond_info, bond_calendar, today_day, today_month, today_year, day_count, convention, method):

    bond_date = np.array(bond_calendar['calendarDate'])
    bond_isOpen = np.array(bond_calendar['isOpen'])
    chinaCal = China(China.IB)

    # adjust the China calendar
    for i in range(bond_calendar.shape[0]):
        temp_date = datetime_to_quantdate(bond_date[i], '%Y/%m/%d')
        #print(temp_date)

        if chinaCal.isBusinessDay(temp_date):
            if bond_isOpen[i] == 0:
                chinaCal.addHoliday(temp_date)

        if not chinaCal.isBusinessDay(temp_date):
            if bond_isOpen[i] == 1:
                chinaCal.removeHoliday(temp_date)

    # Bond information
    maturities_yr = bond_data['Maturity']
    maturities = [int(i * 365) for i in bond_data['Maturity']]
    #print(maturities)
    #maturitiesDay_array = np.array(bond_data['MaturityDay'])
    termination_date_array = np.array(bond_info['Terminate'])
    #issue_date_array = np.array(bond_info['Issue'])
    YTM_array = bond_data['YTM']
    coupon_frequency_array = np.array(bond_info['couponFreq'])

    maturity = []
    frequency = Annual
    for i in range(termination_date_array.shape[0]):
        maturity.append(datetime_to_quantdate(termination_date_array[i], '%Y-%m-%d'))

    #    issu_date = dt.datetime.strptime(issue_date_array[i], '%Y-%m-%d')
    #    issu_year = issu_date.year
    #    issu_month = issu_date.month
    #    issu_day = issu_date.day
    #    bondIssueDate.append(Date(issu_day, issu_month, issu_year))
    #
    #    if coupon_frequency_array[i] == 1:
    #        frequency.append(Period(Annual))
    #    elif coupon_frequency_array[i] == 2:
    #        frequency.append(Period(Semiannual))


    print(YTM_array)
    numberOfBonds = len(maturities)
    cleanPrice = [100.0] * numberOfBonds
    quote = [SimpleQuote(c) for c in cleanPrice] #cleanPrice clean_array
    quoteHandle = [RelinkableQuoteHandle()] * numberOfBonds
    for i in range(len(quoteHandle)):
        quoteHandle[i].linkTo(quote[i])

    dc = day_count
    #dc = Thirty360()
        #ActualActual(ActualActual.Bond) #ISMA
    accrualConvention = convention
    #convention = Following
    redemption = 100.0
    print(chinaCal)
    calendar = chinaCal

    today = calendar.adjust(Date(today_day, today_month, today_year))
    Settings.instance().evaluationDate = today

    bondSettlementDays = 0
    bondSettlementDate = calendar.advance(today, Period(bondSettlementDays, Days))
    print(bondSettlementDate)
    instruments = []
    for j in range(len(maturities)):
        #maturity = calendar.advance(
        #    bondSettlementDate,
        #    Period(maturities[j], Days)) #Years

        schedule = Schedule(
            bondSettlementDate, #bondSettlementDate,bondIssueDate[j] ?
            maturity[j],
            Period(frequency), #Period(frequency)
            #frequency[j],
            calendar,
            accrualConvention,
            accrualConvention,
            DateGeneration.Backward,
            False)

        helper = FixedRateBondHelper(
            quoteHandle[j],
            bondSettlementDays,
            100.0, #price? par
            schedule,
            [YTM_array[j]/100.0], #ytm? [pars[j]]
            dc,
            convention,
            redemption)

        instruments.append(helper)

    #print(ins.getsource(SvenssonFitting))
    tolerance = 1.0e-10
    max = 5000

    if method == 'Piecewise Log Cubin Discount':
        ts0 = PiecewiseLogCubicDiscount(bondSettlementDate, instruments, dc)
    elif method == 'Fitted Bond Discount':
        tolerance = 1.0e-10
        max = 5000
        svensson = SvenssonFitting()
        ts0 = FittedBondDiscountCurve(bondSettlementDate, instruments, dc, SvenssonFitting(), tolerance, max)
        
    return ts0
