//Region breakdown: cinema count, total revenue, revenue per cinema from last month's tickets.
db.order.aggregate([
    {
        $match: {
            "status": "paid"
        }
    },
    {
        $group: {
            _id: "$cinema_id",
            cinema_revenue: { $sum: "$amount" }
        }
    },
    {
        $lookup: {
            from: "cinema",
            localField: "_id",
            foreignField: "_id",
            as: "cinema_details"
        }
    },
    {
        $unwind: "$cinema_details"
    },
    {
        $group: {
            _id: "$cinema_details.region_name",
            cinemas_count: { $sum: 1 },
            total_ticket_revenue: { $sum: "$cinema_revenue" }
        }
    },
    {
        $project: {
            region_name: "$_id",
            cinemas_count: 1,
            total_ticket_revenue: 1,
            revenue_per_cinema: {
                $divide: ["$total_ticket_revenue", "$cinemas_count"]
            }
        }
    },
    {
        $sort: { total_ticket_revenue: -1 }
    }
])