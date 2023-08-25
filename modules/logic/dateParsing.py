import datetime
import calendar
from modules.logic.templates import ContractMonths


class customDate:
    date: int = 0
    month: int = 0
    year: int = 0
    _monthCalendar = None
    ########################### MONTHS OBJECT ###########################
    _contract_months = ContractMonths()

    def __init__(self):
        today = datetime.datetime.today()
        self.date = today.day
        self.month = today.month  # 1-12
        self.year = today.year
        calendar.setfirstweekday(3 + 1)
        self._monthCalendar = calendar.monthcalendar(self.year, self.month)

    def _getCoordinatesOfDate(self):
        weekNum, day = 0, 0
        for i, week in enumerate(self._monthCalendar):
            if week[6] >= self.date or week[6] == 0:
                weekNum = i
                break
        for i, date in enumerate(self._monthCalendar[weekNum]):
            if date == self.date:
                day = i
        return weekNum, day

    def _getNMonthNumbers(self, n: int):
        """ :return add N months to current date (not in place) and return month (1-12) and year"""
        month: int = self.month + n - 1  # 0 to 11
        year: int = self.year + int(month / 12)
        month = month % 12

        return month + 1, year

    def _getDateAtCoordinates(self, week, day):
        return self._monthCalendar[week][day]

    ########################### THESE METHODS ARE EXPOSED ###########################
    def resetDate(self):
        today = datetime.datetime.today()
        self.date = today.day
        self.month = today.month  # 1-12
        self.year = today.year
        self._monthCalendar = calendar.monthcalendar(self.year, self.month)

    def date_str(self):
        return f"{self.date}-{self._contract_months.months_list[self.month - 1].MMM}-{self.year}"

    def get_DMY(self):
        """ :return int date, contract_month object, int year"""
        return self.date, self._contract_months.months_list[self.month - 1], self.year

    def addNWeeks(self, n: int):
        weekNum, day = self._getCoordinatesOfDate()
        numWeeks = len(self._monthCalendar)
        while n > 0:
            if weekNum < numWeeks - 1 and self._getDateAtCoordinates(weekNum + 1, day) != 0:
                weekNum += 1
            else:
                self.month, self.year = self._getNMonthNumbers(1)
                self._monthCalendar = calendar.monthcalendar(self.year, self.month)
                numWeeks = len(self._monthCalendar)
                weekNum = 0
                if self._monthCalendar[weekNum][day] == 0:
                    weekNum += 1
            n -= 1
        self.date = self._monthCalendar[weekNum][day]

    def addNDays(self, n: int):
        if n == 0:
            return
        fullWeeks = int(n / 7)
        self.addNWeeks(fullWeeks)
        n -= 7 * fullWeeks
        weekNum, day = self._getCoordinatesOfDate()
        numWeeks = len(self._monthCalendar)

        while n > 0:
            if day == 6:
                if weekNum < numWeeks - 1:
                    day = 0
                    weekNum += 1
                else:
                    day = 0
                    weekNum = 0
                    self.month, self.year = self._getNMonthNumbers(1)
                    self._monthCalendar = calendar.monthcalendar(self.year, self.month)
                    numWeeks = len(self._monthCalendar)
            else:
                if self._monthCalendar[weekNum][day + 1] == 0:
                    weekNum = 0
                    self.month, self.year = self._getNMonthNumbers(1)
                    self._monthCalendar = calendar.monthcalendar(self.year, self.month)
                    numWeeks = len(self._monthCalendar)
                day += 1
            n -= 1
        self.date = self._monthCalendar[weekNum][day]

    def skipToThursday(self):
        weekNum, day = self._getCoordinatesOfDate()
        day = 6  # thursday

        if self._monthCalendar[weekNum][day] != 0:
            self.date = self._getDateAtCoordinates(weekNum, day)
        else:
            self.addNWeeks(1)
            self.skipToThursday()

    def isLastThursday(self):
        weekNum, day = self._getCoordinatesOfDate()
        if day != 6:
            return False

        weeksInMonth = len(self._monthCalendar)
        if weeksInMonth - 1 == weekNum or (
                weekNum == weeksInMonth - 2 and self._monthCalendar[weeksInMonth - 1][6] == 0):
            return True
        return False

    def getExpiryMonthAfterNDays(self, n: int):
        """ :return contract_month object and year"""
        # Equity Options (Monthly Expiry)
        # {Ex}:{Ex_UnderlyingSymbol}{YY}{MMM}{Strike}{Opt_Type}
        # NSE:NIFTY20OCT11000CE
        self.addNDays(n)
        weekNum, day = self._getCoordinatesOfDate()
        if weekNum != len(self._monthCalendar) - 1 or self._monthCalendar[weekNum][6] != 0:
            contractMonth = self._contract_months.months_list[self.month - 1]
        else:
            contractMonth = self._contract_months.months_list[self.month - 1 + 1]
        return contractMonth, self.year

    def getExpiryWeekAfterNDays(self, n: int):
        # Equity Options (Weekly Expiry)
        # {Ex}:{Ex_UnderlyingSymbol}{YY}{M}{dd}{Strike}{Opt_Type}
        # NSE:NIFTY20O0811000CE

        self.addNDays(n)
        self.skipToThursday()
        return self.date, self._contract_months.months_list[self.month - 1], self.year
