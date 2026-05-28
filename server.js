const express = require('express'); 
const cors = require('cors'); 
const https = require('https'); 
const path = require('path'); 
const fs = require('fs'); 
const app = express(); 
app.use(cors()); 
app.use(express.json());`nconst path = require('path');`napp.get('/', function(req,res){ res.sendFile(path.join(__dirname,'public','index.html')); }); 
app.get('/', function(req, res) { res.sendFile(path.join(__dirname, 'public', 'index.html')); }); 
