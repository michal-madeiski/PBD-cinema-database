//Cinema ranking by last month's ticket revenue.
db.cinema.aggregate([
    {
        $lookup: {
            from: "screening_archive",
            let: { cin_id: "$_id" },
            pipeline: [
            { 
                $match: {
                $expr: {
                    $and: [
                    { $eq: ["$cinema_id", "$$cin_id"] },
                    { $gte: ["$start_time", { 
                        $dateSubtract: { startDate: "$$NOW", unit: "month", amount: 1 } 
                    }]}
                    ]
                }
                }
            },
            { $project: { _id: 1 } } 
            ],
            as: "recent_screenings"
        }
    },
    {
        $addFields: {
            target_screening_ids: {
                $map: { input: "$recent_screenings", as: "s", in: "$$s._id" }
            }
        }
    },
    {
        $lookup: {
            from: "order",
            let: { 
            valid_ids: "$target_screening_ids"
            },
            pipeline: [
            { $unwind: "$ticket" },
            { 
                $match: { 
                    $expr: { $in: ["$ticket.screening_id", "$$valid_ids"] } 
                } 
            },
            { 
                $group: {
                    _id: null,
                    total_revenue: { $sum: "$ticket.total_price" }
                }
            }
            ],
            as: "revenue_data"
        }
    },
    {
    $project: {
        _id: 1,
        address: { 
        $concat: ["$city", ", ul. ", "$street", " ", "$building_number"] 
        },
        revenue: {
            $ifNull: [ { $first: "$revenue_data.total_revenue" }, 0 ]
        }
    }
    },
    { $sort: { revenue: -1 } }
])