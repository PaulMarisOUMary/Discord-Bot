from O365 import Account, MSGraphProtocol
from datetime import datetime
import os

class MicrosoftO365():
    def __init__(self, resource) -> None:
        self.resource = resource
        self.Authenticated = False

    def readToken(self):
        source_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.CLIENT_ID = open(os.path.join(source_directory, "auth", "client.dat"), "r").read()
        self.SECRET_ID = open(os.path.join(source_directory, "auth", "secret.dat"), "r").read()
        self.TENANT_ID = open(os.path.join(source_directory, "auth", "tenant_id.dat"), "r").read()

        return self.CLIENT_ID, self.SECRET_ID, self.TENANT_ID

    def login(self):
        account = Account((self.CLIENT_ID, self.SECRET_ID), protocol=MSGraphProtocol(default_resource=self.resource), auth_flow_type='credentials', tenant_id=self.TENANT_ID)
        if account.authenticate(scope=['Calendars.Read.Shared', 'Calendars.Read']): 
            self.Authenticated = True
            self.schedule = account.schedule()
            self.calendar = self.schedule.get_default_calendar()

    def extractCalendar(self, start, end):
        query = self.calendar.new_query('start').greater_equal(start)
        query.chain('and').on_attribute('end').less_equal(end)
        events = self.calendar.get_events(query=query, include_recurring=True)
        return events

    def extractEvents(self, events):
        self.events = []
        for event in events:
            info = str(event)
            if not 'start' in info:
                heading = info[info.find('Subject:')+9:info.find('on:')-2]
                date = info[info.find('on:')+4:info.find('from:')-1]
                start_timetable = info[info.find('from:')+6:info.find('to:')-1]
                end_timetable = info[info.find('to:')+4:-1]
                self.events.append([heading, date, start_timetable, end_timetable])

        return self.events

    def sortByDay(self, events):
        sort = sorted(events, key = lambda x: datetime.strptime(x[1], '%Y-%m-%d'), reverse=False)

        array, temp, ref = [], [], sort[0][1]
        for element in sort:
            if element[1] == ref:
                temp.append(element)
            else:
                array.append(temp)
                temp = [element]
                ref = element[1]
        
        array.append(temp)

        self.events = array

    def sortByHour(self, events):
        array = []
        for event in events:
            array.append(sorted(event, key = lambda x: datetime.strptime(x[2], '%H:%M:%S'), reverse=False))

        self.events = array

    def findDuplicate(self, events):
        array, day, temp = [], [], []
        for event in events:
            for object in event:
                astart = float(object[2][0:2])+float(object[2][3:5])/60
                aend = float(object[3][0:2])+float(object[3][3:5])/60
                for item in event:
                    bstart = float(item[2][0:2])+float(item[2][3:5])/60
                    bend = float(item[3][0:2])+float(item[3][3:5])/60

                    if astart >= bstart and astart < bend or aend > bstart and aend <= bend:
                        if not item in temp: 
                            temp.append(item)

                if not temp in day: day.append(temp)
                temp = []

            array.append(day)
            day = []

        final, fday = [], []
        for day in array:
            for duplicate in day:
                for i, event in enumerate(duplicate):
                    event.append(i+1)
                    event.append(len(duplicate))
                    fday.append(event)
            final.append(fday)
            fday = []

        self.events = final
