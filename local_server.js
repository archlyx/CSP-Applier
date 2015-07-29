var express = require('express');
var path = require('path');
var config = require('./config');
var https = require('https');
var http = require('http');
var fs = require('fs');
var morgan = require('morgan');
var cors = require('cors');
var formidable = require('formidable');

var options = {
  key: fs.readFileSync(path.join(__dirname, config.key_path) ),
  cert: fs.readFileSync(path.join(__dirname, config.cert_path) )
};

var app = express();
app.use(morgan('dev'));
app.use(cors());

app.use('/allowed-resources',
	express.static(path.join(__dirname, config.js_repository)));

app.use('/libs',
	express.static(path.join(__dirname, config.lib_repository)));

app.options('/js-factory', cors()); // enable pre-flight request for DELETE request 
app.post('/js-factory', cors(), function(req, res, next){
	var form = new formidable.IncomingForm();
	var file_name, script, full_path, decoded_script;

  form.parse(req, function(err, fields, files) {
    //logger.infoMsg("PARSE:"+files.image.name+" "+files.image.path);
    try{
      console.log("file_name: "+fields.file_name);
      console.log("script: "+fields.script);
      full_path = path.join(__dirname, config.js_repository, fields.file_name);
      console.log("full_path: "+full_path);
      var decoded_script = new Buffer(fields.script, 'base64');
      console.log("decoded_script: "+decoded_script);

      fs.writeFileSync(full_path, decoded_script);

      res.json({ success: true,
        message: 'saved '+ fields.file_name}); 
    }
    catch (e) {
      console.log("failed parsing post request: "+e);
      res.json({ success: false,
        message: e }); 
    }
  });

});

http.createServer(app).listen(config.http_port);
https.createServer(options, app).listen(config.https_port);
console.log('Listening on port http:' + 
	config.http_port+' https:'+config.https_port+
	' dirname'+__dirname);