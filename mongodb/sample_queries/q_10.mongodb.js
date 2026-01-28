//Room occupancy by month
db.screening_archive.aggregate([
  {
    $lookup: {
      from: "cinema",
      let: { 
        c_id: "$cinema_id", 
        r_num: "$room_number" 
      },
      pipeline: [
        { $match: { $expr: { $eq: ["$_id", "$$c_id"] } } },
        { $unwind: "$rooms" },
        { $match: { $expr: { $eq: ["$rooms.room_number", "$$r_num"] } } },
        {
          $project: {
            capacity: { $size: "$rooms.seats" }
          }
        }
      ],
      as: "room_data"
    }
  },
  {
    $addFields: {
      month: { $month: "$start_time" },
      room_total_capacity: { $ifNull: [ { $first: "$room_data.capacity" }, 0 ] },
      room_used_seats: { $size: "$taken_seats" }
    }
  },
  {
    $group: {
      _id: "$month",
      total_possible: { $sum: "$room_total_capacity" },
      total_actual: { $sum: "$room_used_seats" }
    }
  },
  {
    $project: {
      _id: 0,
      month: "$_id",
      percentage: {
        $cond: {
          if: { $eq: ["$total_possible", 0] },
          then: 0.0,
          else: {
            $round: [
              {
                $multiply: [
                  { $divide: ["$total_actual", "$total_possible"] },
                  100
                ]
              },
              2
            ]
          }
        }
      }
    }
  },
  { $sort: { month: 1 } }
])