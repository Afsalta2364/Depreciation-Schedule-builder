# depreciation_methods.py

from dateutil.relativedelta import relativedelta

def straight_line_monthly(cost, salvage, start_date, end_date):
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    monthly = (cost - salvage) / months
    acc = 0
    schedule = []
    current = start_date

    for _ in range(months):
        acc += monthly
        schedule.append({
            "Period": current.strftime("%b %Y"),
            "Depreciation Expense": round(monthly, 2),
            "Accumulated Depreciation": round(acc, 2),
            "Book Value": round(cost - acc, 2)
        })
        current += relativedelta(months=1)

    return schedule

def straight_line_yearly(cost, salvage, life_years):
    annual = (cost - salvage) / life_years
    acc = 0
    schedule = []

    for year in range(1, life_years + 1):
        acc += annual
        book_value = cost - acc
        schedule.append({
            "Period": f"Year {year}",
            "Depreciation Expense": round(annual, 2),
            "Accumulated Depreciation": round(acc, 2),
            "Book Value": round(book_value, 2)
        })
    return schedule
