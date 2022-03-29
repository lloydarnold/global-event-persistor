import * as mongoose from 'mongoose';

// empty location == global
export const RegionSchema = new mongoose.Schema({
    continent : String,
    country : String,
    state: String, // state, province, county, etc; varies
    city : String
})

// TODO: update to include two numbers under sentiment
export const EventSchema = new mongoose.Schema({
    timeStamp: { type: Date, required: true },
    sentiment: Number,
    source: { type: String, required: true },
    category: { type: String, required: true },
    subcategory: { type: String },
    detail : String,
    region : { type: mongoose.Schema.Types.ObjectId, ref: 'Region'},
    actors : [String],
    stocks : [String]
})

export interface Event extends mongoose.Document {
    id: mongoose.Schema.Types.ObjectId;
    timeStamp: Date;
    sentiment: Number;
    source: string;
    category: string;
    subcategory: string;
    detail: string;
    region: mongoose.Schema.Types.ObjectId;
    actors: string[];
    stocks: string[]
}

export interface Region extends mongoose.Document {
    id_reg: mongoose.Schema.Types.ObjectId;
    continent : string;
    country : string;
    state: string; // state, province, county, etc; varies
    city : string;
}

export class EventCreationDTO {
    id: mongoose.Schema.Types.ObjectId;
    timeStamp: Date;
    sentiment: Number;
    source: string;
    category: string;
    subcategory: string;
    detail: string;
    region: mongoose.Schema.Types.ObjectId;
    actors: string[];
    stocks: string[]

    id_reg: mongoose.Schema.Types.ObjectId;
    continent : string;
    country : string;
    state: string; // state, province, county, etc; varies
    city : string;
}

export class QueryDTO {
    from: Date;
    to: Date;
    continent : string;
    country : string;
    state: string;
    city : string;
    category: String;
    subcategory: String;
    stock: String
}
