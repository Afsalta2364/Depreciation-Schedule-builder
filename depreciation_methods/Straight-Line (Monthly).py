from dateutil.relativedelta import relativedelta

def straight_line_monthly(cost, salvage, start_date, end_date):
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    monthly_dep = (cost - salvage) / months
    acc_dep = 0
    schedule = []

    current = start_date
    for _ in range(months):
        acc_dep += monthly_dep
        book_value = cost - acc_dep
        schedule.append({
            "Period": current.strftime("%b %Y"),
            "Depreciation Expense": round(monthly_dep, 2),
            "Accumulated Depreciation": round(acc_dep, 2),
            "Book Value": round(book_value, 2)
        })
        current += relativedelta(months=1)

    return schedule
