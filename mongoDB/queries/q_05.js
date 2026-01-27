//Ticket promotion breakdown
db.order.aggregate([
    { $unwind: "$ticket" },
    {
        $addFields: {
            has_special: { 
                $gt: [ { $ifNull: ["$ticket.special_offer_amount", 0] }, 0 ] 
            },

            has_discount: {
                $or: [
                    { $gt: [ { $ifNull: ["$ticket.group_type_snapshot.discount_percentage", 0] }, 0 ] },
                    
                    { $gt: [ { $max: "$ticket.seats_snapshot.discount_percentage" }, 0 ] }
                ]
            }
        }
    },

    {
        $project: {
            typ_biletu: {
                $switch: {
                    branches: [
                        { 
                            case: { $and: ["$has_special", "$has_discount"] }, 
                            then: "Znizka + Special Offer" 
                        },
                        { 
                            case: "$has_special", 
                            then: "Tylko Special Offer" 
                        },
                        { 
                            case: "$has_discount", 
                            then: "Tylko Znizka" 
                        }
                    ],
                    default: "Brak (Pełna cena)"
                }
            }
        }
    },

    {
        $group: {
            _id: "$typ_biletu",
            ilosc: { $sum: 1 }
        }
    }
])