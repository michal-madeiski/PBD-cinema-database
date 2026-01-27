//Product revenue vs ticket revenue

db.order.aggregate([
    { $group: {
        _id: null,
        products: {  
          $sum: {  
            $sum: { 
              $map: {
                input: "$product_snapshot",
                as: "product",
                in: {
                  $multiply: ["$$product.count", "$$product.price"]
                }
              }
            }
          }
        },
        tickets: {
          $sum: {
            $sum: "$ticket.total_price"
          }
        }
      }
    },
    { $project: {
        _id: 0,
        products: 1,
        tickets: 1
      }
    }
])