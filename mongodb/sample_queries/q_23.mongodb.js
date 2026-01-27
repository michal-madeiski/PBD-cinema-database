//Client's ticket history.

db.order.aggregate([
  {
    $match: {
      user_id: ObjectId('69786a31958640ef62bd93d5') 
    }
  },
  { $unwind: "$ticket" },
  {
    $lookup: {
      from: "cinema",
      localField: "cinema_id",
      foreignField: "_id",
      as: "cinema_info"
    }
  },
  { $unwind: "$cinema_info" },
  {
    $lookup: {
      from: "screening_archive",
      localField: "ticket.screening_id",
      foreignField: "_id",
      as: "screening_info"
    }
  },
  { $unwind: "$screening_info" },
  {
    $project: {
      _id: 0,
      title: "$ticket.movie_title",
      address: {
        $concat: ["$cinema_info.city", ", ul. ", "$cinema_info.street", " ", "$cinema_info.building_number"]
      },
      date: {
        $dateToString: { format: "%Y-%m-%d", date: "$screening_info.start_time" }
      },
      time: {
        $dateToString: { format: "%H:%M:%S", date: "$screening_info.start_time" }
      },
      room: "$screening_info.room_number",
      seats: {
        $map: {
          input: "$ticket.seats_snapshot",
          as: "seat",
          in: "$$seat.seat_number"
        }
      },
      status: "$ticket.status",
      price: "$ticket.total_price" 
    }
  },
  { $sort: { "Date": 1, "Time": 1 } },
])