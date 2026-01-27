// Number of free tickets per special offer
db.order.aggregate([
    {
        $unwind: "$ticket"
    },
    {
        $match: {
            "ticket.special_offer_id": { $exists: true, $ne: null },
            "ticket.total_price": { $lt: 14 }
        }
    },
    {
        $group: {
            _id: "$ticket.special_offer_id",
            cheep_tickets_count: { $sum: 1 }
        }
    },
    {
        $lookup: {
            from: "special_offer",
            localField: "_id",
            foreignField: "_id",
            as: "offer_details"
        }
    },
    {
        $unwind: "$offer_details"
    },
    {
        $project: {
            special_offer_id: "$_id",
            name: "$offer_details.name",
            amount: "$offer_details.amount",
            cheap_tickets_count: 1
        }
    },
    {
        $sort: {
            amount: -1,
            cheap_tickets_count: -1
        }
    }
])
