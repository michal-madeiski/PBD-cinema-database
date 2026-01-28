//Top 10 best-selling products.
db.order.aggregate([
    { $unwind: "$product_snapshot" },
    {
      $group: {
        _id: "$product_snapshot.product_id",
        name: { $first: "$product_snapshot.name" },
        number_of_sold: { $sum: "$product_snapshot.count" }
      }
    },
    { $sort: { number_of_sold: -1} },
    { $limit: 10 },
    {
      $project: {
        _id: 0,
        name: 1,
        number_of_sold: 1
      }
    }
])