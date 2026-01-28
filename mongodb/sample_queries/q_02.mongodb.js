//Number of screenings per film format.
db.screening_archive.aggregate([
    {$group: {
        _id: {
            version_lang: "$version_snapshot.language", 
            version_subt: "$version_snapshot.subtitles", 
            version_format: "$version_snapshot.format" 
        }, 
        count: { $sum: 1}
    }}, 
    {$sort : { count: -1}}, 
    {$limit:  15}
])
