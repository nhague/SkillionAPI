from datetime import datetime, timedelta
from googbot import getEvents
import pytz

dateTimeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"
appointments = getEvents()

now = datetime.now() + timedelta(hours=24)
end = now + timedelta(days=3)
now_d1 = now.replace(tzinfo=pytz.UTC)
end_d1 = end.replace(tzinfo=pytz.UTC)
hours = (now_d1, end_d1)

def get_slots(duration=timedelta(minutes=30)):
    slots = sorted([(hours[0], hours[0])] + appointments + [(hours[1], hours[1])])
    final_slots = []
    for start, end in ((slots[i][1], slots[i+1][0]) for i in range(len(slots)-1)):
        assert start <= end, "Cannot attend all appointments"
        while start + duration <= end:
            final_slots.append("{:%Y-%m-%dT%H:%M:%S.%fZ}".format(start))
            start += duration
    return final_slots
