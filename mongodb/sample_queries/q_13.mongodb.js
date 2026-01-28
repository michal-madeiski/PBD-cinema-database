//Top 10 movie incomes.
{
    use("cinema_db");

    db.order.aggregate([
        {$match: {status: "paid"}},
        { $addFields: {total_ticket_price: {$sum: "$ticket.total_price"}}},
        {
            $lookup: {
                from: "screening_archive",
                localField: "ticket.0.screening_id",
                foreignField: "_id",
                as: "screening_snapshot"
            }
        },
        {$unwind: "$screening_snapshot"},
        {
            $lookup: {
                from: "movie",
                localField: "screening_snapshot.movie_id",
                foreignField: "_id",
                as: "movie_snapshot"
            }
        },
        {$unwind: "$movie_snapshot"},
        {
            $group: {
                _id: "$movie_snapshot._id",
                title: {$first: "$movie_snapshot.title"},
                ticket_sell: {$sum: "$total_ticket_price"},
                license_cost: {$first: "$movie_snapshot.license.cost"}
            }
        },
        { $addFields: {balance: {$subtract: ["$ticket_sell", "$license_cost"]}}},
        {$sort: {balance: -1}},
        {
            $project: {
                _id: 1,
                title: 1,
                balance: 1,
            }
        },
        {$limit: 10}
    ])
}