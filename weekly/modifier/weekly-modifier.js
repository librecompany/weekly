/**
 
 Copyright (c) 2014 Giuseppe Futia <giuseppe.futia@gmail.com>

 Permission to use, copy, modify, and distribute this software for any
 purpose with or without fee is hereby granted, provided that the above
 copyright notice and this permission notice appear in all copies.

 THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

**/

var fs  = require("fs");

var jsonFile = require("./project-topics.json");
var dict = JSON.parse(JSON.stringify(jsonFile));

console.info("Starting to modify your weekly reports...");

var weekly;

process.argv.forEach(function(val, index, array) {
    if(index == 2) weekly = val;
});

//TODO Sanitize Path

fs.readFileSync("../../archive/"+weekly).toString().split('\n').forEach(function (line) { 
    
    for(var key in dict) {
    	if(line.indexOf(key) != -1) {
    	    console.info("Old entry: "+line);
    	    line = line.replace(key, dict[key].replace("\'","").replace("\'","")); //TODO: improve it!
            console.info("New entry: "+line);
    	    console.info('\n');
    	}
    } 
    fs.appendFileSync("./output/"+weekly, line.toString() + "\n");
});

//TODO YAML Importer

