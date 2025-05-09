def straight_line_yearly(cost, salvage, life):
    annual = (cost - salvage) / life
    acc_dep = 0
    schedule = []

    for year in range(1, life + 1):
        acc_dep += annual
        book_value = cost - acc_dep
        schedule.append({
            "Period": f"Year {year}",
            "Depreciation Expense": round(annual, 2),
            "Accumulated Depreciation": round(acc_dep, 2),
            "Book Value": round(book_value, 2)
        })
    return schedule
