//Average daily screenings per cinema.
db.cinema.aggregate([
    {
        $lookup: {
        from: "screening_archive",
        let: { c_id: "$_id" },
        pipeline: [{ 
            $match: {
                $expr: { 
                    $eq: ["$cinema_id", "$$c_id"]
                }
            }
            },
            { 
            $project: {
                _id: 0,
                start_time: 1
            } 
            }
        ],
        as: "archive_data"
        }
    },
    {
        $addFields: {
            number_of_screenings: { $size: "$archive_data" },
            number_of_days: {
                $cond: {
                    if: { $eq: [{$size: "$archive_data"}, 0] },
                    then: 1,
                    else: {
                        $add: [
                            {
                                $dateDiff: {
                                    startDate: { $min: "$archive_data.start_time" },
                                    endDate: new Date(),
                                    unit: "day"
                                }
                            },
                            1
                        ]
                    }
                }
            },
            address: {
                $concat: ["$city", ", ul. ", "$street", " ", "$building_number"],
            }
        }
    },
    {
        $addFields: {
          average_screening_per_day: {
            $round: [{
                $divide: [ "$number_of_screenings", "$number_of_days"]
                },
                2
            ]
          }
        }
    },
    {
        $sort: {
          average_screening_per_day: -1
        }
    },
    {
        $project: {
            _id: 1,
            address: 1,
            average_screening_per_day: 1,
        }
    }
])