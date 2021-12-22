const express = require('express');
const mysql = require('mysql');
const app = express();

app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({limit: '50mb'}));

var toSend;

const sql = mysql.createConnection({
user: 'root',
password: 'AIEProject1234@',
database: 'test',
host: 'localhost',
port: '3306'
});

sql.connect(function (err) {
    if (err) throw err;
});



app.get('/test/', (req, res) =>
{
    toSend = sql.query('SELECT * FROM photos', function (err, result)
    {
        if(err)
        {
            throw err;
        }
        console.log(result);
        res.send(JSON.stringify(result));
    });
    
});

app.post('/add/', (req, res) => 
{
    console.log(req.body);
    res.status(200).send("Done");

    var query = `INSERT INTO photos (BASE, DESCRIPTION, DATE) VALUES ("` + req.body.BASE + `", 'No description','` + req.body.DATE +  `')`;
    sql.query(query, function (err, result) 
    {
        if(err)
        {
            throw err;
        }
    });
});

app.listen(4000, () => console.log('Listening on port 4000'));