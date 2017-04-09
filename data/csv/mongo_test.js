var mongodb = require('mongodb');
var server = new mongodb.Server('127.0.0.1', 13209, {auto_reconnect:true});
var db = new mongodb.Db('ayesha', server, {safe:true});

db.open(function(err, db){
    if(!err){
        console.log('connect success');
        db.createCollection('ayesha',  function(err, collection){
            if(err){
                console.log(err);
            }else{
                console.log("success");
            }
    });
    }
    else{
        console.log(err);
    }
});