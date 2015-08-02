var express = require('express');
var bodyParser = require('body-parser')
var path = require('path');
var config = require('./config');
var https = require('https');
var http = require('http');
var fs = require('fs');
var morgan = require('morgan');
var cors = require('cors');
var formidable = require('formidable');
var base64 = require('base-64');

var options = {
  key: fs.readFileSync(path.join(__dirname, config.key_path) ),
  cert: fs.readFileSync(path.join(__dirname, config.cert_path) )
};

var app = express();
app.use(morgan('dev'));
app.use(cors());

var corsOptions = {
  origin: '*',
  allowedHeaders : 'Content-Type'
};

app.use('/allowed-resources',
	express.static(path.join(__dirname, config.js_repository)));

app.use('/libs',
	express.static(path.join(__dirname, config.lib_repository)));

app.use(bodyParser({limit: '50mb'}));
app.use(bodyParser.json() );
//app.use(bodyParser.urlencoded({extended:false}));

app.options('/js-factory', cors(corsOptions)); // enable pre-flight request for DELETE request 
app.post('/js-factory', cors(corsOptions), function(req, res, next){
	var file_name, script, full_path, decoded_script;
  try{
    //console.log("file_name: "+req.body.file_name);
    //console.log("script: "+req.body.script);
    full_path = path.join(__dirname, config.js_repository, req.body.file_name);
    decoded_script = decodeURI(req.body.script);
    fs.writeFileSync(full_path,decoded_script);
    res.json({ success: true,
        message: 'saved '+ req.body.file_name}); 
  }
  catch (e) {
    console.log('error in js-factory: '+e);
  }
  
  /*try{
    console.log("file_name: "+req.body.file_name);
    console.log("script: "+req.body.script);
    full_path = path.join(__dirname, config.js_repository, req.body.file_name);
    console.log("full_path: "+full_path);
    var decoded_script = base64.decode(req.body.script);
    console.log("decoded_script: "+decoded_script);

    fs.writeFileSync(full_path, decoded_script);
    res.json({ success: true,
      message: 'saved '+ req.body.file_name}); 
  }
  catch(e){
    console.log('error in js-factory: '+e);
  }*/
  
  /*
  var form = new formidable.IncomingForm();
  form.parse(req, function(err, fields, files) {
    //logger.infoMsg("PARSE:"+files.image.name+" "+files.image.path);
    try{
      console.log("file_name: "+fields.file_name);
      console.log("script: "+fields.script.length);
      full_path = path.join(__dirname, config.js_repository, fields.file_name);
      console.log("full_path: "+full_path);
      //var decoded_script = new Buffer(fields.script, 'base64');
      var x= decodeURI(fields.script);
      var decoded_script = base64.decode(x);
      console.log("decoded_script: "+x);

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
  */
});

http.createServer(app).listen(config.http_port);
https.createServer(options, app).listen(config.https_port);
console.log('Listening on port http:' + 
	config.http_port+' https:'+config.https_port+
	' dirname'+__dirname);