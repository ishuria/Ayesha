var lineReader = require('line-reader');
var mongodb = require('mongodb');
var config = require('./config/default');



var mysql  = require('mysql');  //调用MySQL模块

//创建一个connection
var connection = mysql.createConnection(config.mysql_config);

//创建一个connection
connection.connect(function(err){

    if(err){       

        console.log('[query] - :'+err);

        return;

    }

    console.log('[connection connect]  succeed!');

}); 

//执行SQL语句
connection.query('SELECT 1 + 1 AS solution', function(err, rows, fields) {

    if (err) {

        console.log('[query] - :'+err);

        return;

    }

    console.log('The solution is: ', rows[0].solution); 

}); 

//关闭connection
connection.end(function(err){

    if(err){       

        return;

    }

    console.log('[connection end] succeed!');

});




//增加
var mysql = require('mysql');
var DATABASE = "seckill";
var TABLE="seckill"
var connection = mysql.createConnection({
    host:'127.0.0.1',
    user:'root',
    password:'12345',
    port:'3306',
    database: DATABASE
});

connection.connect();

var addVip = 'insert into seckill(name,number) values(?,?)';
var param = ['100元秒杀家教机',100];
connection.query(addVip, param, function(error, result){
    if(error)
    {
        console.log(error.message);
    }else{
        console.log('insert id: '+result.insertId);
    }
});

connection.end();




//删除
var mysql = require('mysql');
var DATABASE = "node";
var TABLE="seckill"
var connection = mysql.createConnection({
    host:'127.0.0.1',
    user:'root',
    password:'12345',
    port:'3306',
    database: DATABASE
});

connection.connect();

var addVip = 'delete from seckill where seckill_id = 1005';
connection.query(addVip, function(error, result){
    if(error)
    {
        console.log(error.message);
    }else{
        console.log('affectedRows: '+result.affectedRows);
    }
});

connection.end();



//查找
var mysql = require("mysql");
var DATABASE = "node";
var TABLE="seckill"
var connection = mysql.createConnection({
    host:'127.0.0.1',
    user:'root',
    password:'12345',
    port:'3306',
});

connection.connect();
connection.query('use '+DATABASE);
connection.query('select * from '+TABLE, function(error, results, fields){
    if (error) {
        throw error;
    }
    if (results) {
        for(var i = 0; i < results.length; i++)
        {
            console.log('%s\t%s',results[i].name,results[i].end_time);
        }
    }
});

connection.end();




//修改
var mysql = require('mysql');
var DATABASE = "seckill";
var connection = mysql.createConnection({
    host:'127.0.0.1',
    user:'root',
    password:'12345',
    port:'3306',
    database: DATABASE
});
connection.connect();
var userSql = "update seckill set number = number-1 where seckill_id = ?";
var param = [1000, 2];
connection.query(userSql, param, function (error, result) {
    if(error)
    {
        console.log(error.message);
    }else{
        console.log('affectedRows: '+result.affectedRows);
    }
});
connection.end();
