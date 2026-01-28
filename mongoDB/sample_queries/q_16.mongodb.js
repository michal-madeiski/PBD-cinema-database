//Every 10,000th customer in the system
db.user.aggregate([
    {
        $match: {
            "type": "client"
        }
    },
    {
        $setWindowFields: {
            sortBy: { account_create_date: 1 },
            output: {
                client_number: {
                    $documentNumber: {}
                }
            }
        }
    },
    {
        $match: {
            $expr: {
                $eq: [{ $mod: ["$client_number", 10_000] }, 0]
            }
        }
    },
    {
        $project: {
            _id: 1,
            name: 1,
            surname: 1,
            account_create_date: 1,
            client_number: 1
        }
    }
])
