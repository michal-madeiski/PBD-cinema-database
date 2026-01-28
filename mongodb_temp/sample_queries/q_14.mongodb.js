//Overall number of workers per shift type in each cinema.
db.shift.aggregate([
    {
        $lookup: {
            from: "cinema",
            localField: "cinema_id",
            foreignField: "_id",
            as: "cinema_snapshot"
        }
    },
    {$unwind: "$cinema_snapshot"},
    {
        
        $group: {
            _id: "$cinema_id",
            cinema_address: {$first: {$concat: ["$cinema_snapshot.city", ", ", "$cinema_snapshot.street", " ", "$cinema_snapshot.building_number"]}},
            cashier_count: {$sum: {$cond: [{$eq: ["$type", "cashier"]}, 1, 0]}},
            usher_count: {$sum: {$cond: [{$eq: ["$type", "usher"]}, 1, 0]}},
            cleaning_count: {$sum: {$cond: [{$eq: ["$type", "cleaning"]}, 1, 0]}},
            projection_count: {$sum: {$cond: [{$eq: ["$type", "projection"]}, 1, 0]}},
            technical_support_count: {$sum: {$cond: [{$eq: ["$type", "technical_support"]}, 1, 0]}},
        }
    },
    {
        $project: {
            _id: 0,
        }
    }
])