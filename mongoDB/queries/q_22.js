//Which screenings are available in the given cinema?
var cinema_id= ObjectId("6978c3545009f7a53ebbede6"); 
var startOfDay = new Date("2027-03-06T00:00:00.000+00:00")
var endOfDay = new Date(startOfDay);
endOfDay.setDate(startOfDay.getDate() + 1);

db.screening.find({cinema_id: cinema_id, start_time: {$gte: startOfDay, $lt: endOfDay}}, {_id: 0,start_time: 1, movie_title: 1, version_snapshot: 1})

