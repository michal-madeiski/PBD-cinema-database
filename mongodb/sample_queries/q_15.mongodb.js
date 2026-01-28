//Workers with above-average employment time.
{
    use("cinema_db");

    db.user.aggregate([
        {
            $match: {
                type: {$in: ["service", "supervisor"]}
            }
        },
        {$unwind: "$employments"},
        {
            $addFields: {
                "employments.months_worked": {
                    $dateDiff: {
                        startDate: "$employments.start_date",
                        endDate: {$ifNull: ["$employments.end_date", "$$NOW"]},
                        unit: "month",
                    }
                }
            }
        },
        {
            $group: {
                _id: "$_id",
                name: { $first: "$name" },
                surname: { $first: "$surname" },
                username: {$first: "$username"},
                total_months_worked: { $sum: "$employments.months_worked" }
            }
        },
        {
            $setWindowFields: {
                partitionBy: null,
                output: {
                    avg_months_worked: { $avg: "$total_months_worked" }
                }
            }
        },
        {
            $match: {
                $expr: { $gt: ["$total_months_worked", "$avg_months_worked"] }
            }
        },
        {$sort: {"total_months_worked": -1}},
        {
            $project: {
                _id: 0,
                worker: {$concat: ["$name", " ", "$surname", " (", "$username", ")"]},
                total_months_worked: 1,
                average_months_worked: "$avg_months_worked",
            }
        }
    ])
}