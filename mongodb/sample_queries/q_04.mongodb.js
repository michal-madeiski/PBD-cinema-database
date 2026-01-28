//Total ticket revenue per cinema from the last year.
db.order.aggregate([
    {$match : {
        "time_of_payment": {
            $gte: new Date("2025-01-01T00:00:00Z"), // Przykładowa data początkowa
            $lt: new Date("2026-01-01T00:00:00Z")   // Przykładowa data końcowa
        }
    }}, 
    { $unwind: "$ticket" },
    {$group: {
        _id: "$cinema_id", 
        ticket_revenue: {$sum: "$ticket.total_price"}
    }},
    {$sort: {"ticket_revenue": -1}}, 
    {$limit: 10}
])