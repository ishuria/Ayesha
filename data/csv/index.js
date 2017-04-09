var lineReader = require('line-reader');
var mongodb = require('mongodb');
var server = new mongodb.Server('127.0.0.1', 13209, {auto_reconnect:true});
var db = new mongodb.Db('ayesha', server, {safe:true});




db.open(function(err, db){
    if(!err){
        console.log('connect success');




        db.createCollection('fin_data', function(err, collection){
            if(err){
                console.log(err);
            }else{
                console.log("success");

                var line_number = 0;
				lineReader.eachLine('D:\\BaiduYunGuanjia\\download\\TB0408\\财报数据私募版2016S3\\all_financial_data_utf8.csv', { encoding: 'utf8'}, function(line, last) {

					if(0==line_number){

					}
					else{
						//collection.insert({content:line});
						console.log(line);
					}


					line_number++;
				});


				console.log("finish");
				return;
            }
    });
    }
    else{
        console.log(err);
    }
});


