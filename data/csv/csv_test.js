var lineReader = require('line-reader');
var iconv = require('iconv-lite');

var line_number = 0;

//lineReader.eachLine('test.csv', { encoding: 'gbk'}, function(line, last) {
  //console.log(line);
//  console.log(iconv.decode(line,'gbk'));
//});



var fs=require("fs");  




function readLines(input, func) {
  var remaining = '';
  input.on('data', function(data) {
    remaining += data;
    var index = remaining.indexOf('\n');
    while (index > -1) {
      var line = remaining.substring(0, index);
      remaining = remaining.substring(index + 1);
      //console.log(iconv.decode(line,'gbk'));
      func(line);
      index = remaining.indexOf('\n');
    }
 
  });
 
  input.on('end', function() {
    if (remaining.length > 0) {
        console.log("remaining");
      func(remaining);
    }
  });
}
 


function func(data) {
  //container.push(data);
  //console.log(iconv.decode(data,'gbk'));
}
 
var input = fs.createReadStream("test.csv");
readLines(input, func);