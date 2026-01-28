// Cinemas in city.
db.cinema.aggregate([
    {
        $match: {
            "city": { $regex: /^Brzeg$/i }
        }
    },
    {
        $project: {
            _id: 1,
            city: 1,
            region_name: 1,
            street: 1,
            building_number: 1
        }
    },
    {
        $sort: { _id: 1 }
    }
])