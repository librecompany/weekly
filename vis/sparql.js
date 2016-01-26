/**
 * 
 * Copyright (c) 2013 Giuseppe Futia <giuseppe.futia@gmail.com>
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 * 
 * 
 * */

var SPARQL = {}

var log = function(msg) {
	console.log(msg);
}

SPARQL.endpoint = "http://federicomorando.polito.it:9999/sparql/";

SPARQL.activitiesQuery = "query=PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns%23>"+
						 "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema%23>"	+
						 "SELECT ?a ?o WHERE {" +
						 "?s <http://id.nexa.polito.it/weekly/activity> ?a . " +
						 "?s <http://id.nexa.polito.it/weekly/hours> ?o ." +
						 "}";
						 
SPARQL.launchActivitiesQuery = function(endpoint, query) {
	$.ajax({
		type : "POST",
		url : endpoint,
		data : encodeURI(query),
		success : function(data, textStatus, jqXHR){			
			var xmlDoc = $.parseXML(data);
			var $xml = $(xmlDoc);
			var $activities = $xml.find("uri");
			log($activities.text());
			
		},
	});
}

SPARQL.launchActivitiesQuery(SPARQL.endpoint, SPARQL.activitiesQuery); 