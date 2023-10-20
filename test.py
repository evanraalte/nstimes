from datetime import datetime

from nstimes.departure import Departure

planned = datetime.now()
d = Departure(train_type="", platform="", planned_departure_time=planned)
print(d)
