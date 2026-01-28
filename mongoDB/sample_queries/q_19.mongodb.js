// Employees with the most hours worked last month
db.shift.aggregate([
    {
        $match: {
            "start_time": {
                $gte: new Date(new Date().setDate(new Date().getDate() - 3000)),
                $lt: new Date()
            }
        }
    },
    {
        $group: {
            _id: "$worker_id",
            total_duration_ms: {
                $sum: { $subtract: ["$end_time", "$start_time"] }
            }
        }
    },
    {
        $lookup: {
            from: "user",
            localField: "_id",
            foreignField: "_id",
            as: "worker_details"
        }
    },
    {
        $unwind: "$worker_details"
    },
    {
        $project: {
            name: "$worker_details.name",
            surname: "$worker_details.surname",
            hours_of_work: {
                $divide: ["$total_duration_ms", 3600000]
            }
        }
    },
    {
        $sort: { hours_of_work: -1 }
    }
])