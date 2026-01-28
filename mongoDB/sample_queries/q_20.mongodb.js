// Regional managers who managed 3 or more DISTINCT regions
db.user.aggregate([
    {
        $match: {
            "type": "regional_manager"
        }
    },
    {
        $unwind: "$terms"
    },
    {
        $group: {
            _id: "$_id",
            name: { $first: "$name" },
            surname: { $first: "$surname" },
            unique_regions: { $addToSet: "$terms.region_name" }
        }
    },
    {
        $project: {
            name: 1,
            surname: 1,
            number_of_regions: { $size: "$unique_regions" }
        }
    },
    {
        $match: {
            "number_of_regions": { $gte: 3 }
        }
    },
    {
        $sort: { number_of_regions: -1 }
    }
])
