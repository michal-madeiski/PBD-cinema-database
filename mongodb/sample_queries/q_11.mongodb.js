//Cash payments percentage: tickets, products, total.
{
    use("cinema_db");
    
    db.order.aggregate([
        {$match: {status: "paid"}},
        {
            $group: {
                _id: null,
                total_all: {$sum: 1},
                ticket_all: {$sum: {$cond: [{$ne: ["$ticket", null]}, 1, 0]}},
                product_all: {$sum: {$cond: [{$ne: ["$product_snapshot", null]}, 1, 0]}},
                total_cash: {$sum: {$cond: [{$eq: ["$payment_type", "cash"]}, 1, 0]}},
                ticket_cash: {$sum: {$cond: [
                    {
                        $and: [{$ne: ["$ticket", null]}, {$eq: ["$payment_type", "cash"]}]
                    }, 1, 0
                ]}},
                product_cash: {$sum: {$cond: [
                    {
                        $and: [{$ne: ["$product_snapshot", null]}, {$eq: ["$payment_type", "cash"]}]
                    }, 1, 0
                ]}},
            }
        },
        {
            $project: {
                _id: 0,
                percent_tickets_cash: {
                    $multiply: [ { $divide: ["$ticket_cash", "$ticket_all"] }, 100 ]
                },
                percent_products_cash: {
                    $multiply: [ { $divide: ["$product_cash", "$product_all"] }, 100 ]
                },
                percent_all_cash: {
                    $multiply: [ { $divide: ["$total_cash", "$total_all"] }, 100 ]
                },
            }
        }
    ])
}