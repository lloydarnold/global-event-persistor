var mongoose = require('mongoose');

var Schema = mongoose.Schema;

// mongoose.connect('mongodb://address', { addNewUrlParser: true, useUnifiedTopology: true });

// Output result of connection to console - update to log file ?
mongoose.connection.on('open', function (ref) {
    console.log('Connected to mongo server.');
});

mongoose.connection.on('error', function (err) {
    console.log('Could not connect to mongo server!');
    console.log(err);
});

// model for event schema, as outlined in planning
// category - finite number, can't take any old string. Same for subcategories.
// put validation in at controller level - makes easier to swap out for other DB
mongoose.exports.event=mongoose.model('event', new Schema({
    timeStamp : [ new Schema({ event : Date, source : Date }) ],
    category : String,
    subcategory : String,
    detail : String,
    region : Schema.Types.ObjectId,
    actors : String,
    stocks : String
}));

// model for location data, as proposed by @Felipe
mongoose.exports.event=mongoose.model('location', new Schema({new Schema({
  continent : String,
  country : String,
  state : String,
  city : String
}));
