//Number of tickets sold per movie
db.screening_archive.aggregate([
    {$group:{
        _id: "$movie_id",
        tytul_filmu: { $first: "$movie_title" },
        sprzedane_miejsca: { $sum: { $size: "$taken_seats" } }
    }}, 
    {$sort : { "sprzedane_miejsca": -1}},
    { $limit: 3 }, 
])