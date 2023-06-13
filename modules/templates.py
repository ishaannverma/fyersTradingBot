########################### CONTRACT MONTHS ###########################

class ContractMonth:
    MMM = ""
    M = ""

    def __init__(self, mmm: str, m: str):
        self.MMM = mmm.upper()
        self.M = m.upper()


class ContractMonths:
    months_list = [
        ContractMonth('JAN', "1"),
        ContractMonth('FEB', "2"),
        ContractMonth('MAR', "3"),
        ContractMonth('APR', "4"),
        ContractMonth('MAY', "5"),
        ContractMonth('JUN', "6"),
        ContractMonth('JUL', "7"),
        ContractMonth('AUG', "8"),
        ContractMonth('SEP', "9"),
        ContractMonth('OCT', "O"),
        ContractMonth('NOV', "N"),
        ContractMonth('DEC', "D")
    ]
    january = months_list[0]
    february = months_list[1]
    march = months_list[2]
    april = months_list[3]
    may = months_list[4]
    june = months_list[5]
    july = months_list[6]
    august = months_list[7]
    september = months_list[8]
    october = months_list[9]
    november = months_list[10]
    december = months_list[11]
