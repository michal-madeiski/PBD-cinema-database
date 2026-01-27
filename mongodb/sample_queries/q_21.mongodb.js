//Which seats are available for the given screening?
{
    use("cinema_db");

    const screening_id = "69786a1b958640ef62bd7cdb";

    db.screening.aggregate([
        {$match: {_id: ObjectId(screening_id)}},
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
            $addFields: {
                screening_room: {
                    $arrayElemAt: [
                        {
                            $filter: {
                                input: "$cinema_snapshot.rooms",
                                as: "room",
                                cond: {$eq: ["$$room.room_number", "$room_number"]}
                            }
                        }, 0
                    ]
                }
            }
        },
        {
            $project: {
                all_seats: {
                    $map: {
                        input: "$screening_room.seats",
                        as: "seat",
                        in: "$$seat.seat_number"
                    }
                },
                taken_seats: {
                    $map: {
                        input: {$ifNull: ["$taken_seats", []]},
                        as: "taken",
                        in: "$$taken.seat_number"
                    }
                }
            }
        },
        {
            $project: {
                _id: 0,
                available_seats: { $setDifference: ["$all_seats", "$taken_seats"] }
            }
        }
    ])
}