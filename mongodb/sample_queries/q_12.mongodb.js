//Most screened version for each movie.
{
    use("cinema_db");

    db.screening_archive.aggregate([
        {
            $group: {
                _id: {
                    title: "$movie_title",
                    version: "$version_snapshot",
                },
                screening_count: {$sum: 1}
            }
        },
        { $sort: {"screening_count": -1} },
        {
            $group: {
                _id: "$_id.title",
                version: {$first: "$_id.version"},
                screening_count: {$first: "$screening_count"},
            }
        },
        { $sort: {"screening_count": -1}},
        {
            $project: {
                _id: 0,
                title: "$_id",
                version: "$version",
                screening_count: "$screening_count",
            }
        }
    ])
}