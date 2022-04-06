import * as mongoose from 'mongoose';

// empty location == global
export const RegionSchema = new mongoose.Schema({
    continent : String,
    country : String,
    state: String, // state, province, county, etc; varies
    city : String
})

export interface Region extends mongoose.Document {
    id_reg: mongoose.Schema.Types.ObjectId;
    continent : string;
    country : string;
    state: string; // state, province, county, etc; varies
    city : string;
}

export const EventSchema = new mongoose.Schema({
    timeStamp: { type: Date, required: true },
    positivity: Number,
    relevance : Number,
    source: { type: String, required: true },
    category: { type: String, required: true },
    subcategory: { type: String },
    detail : String,
    regions : [{ type: mongoose.Schema.Types.ObjectId, ref: 'Region'}],
    actors : [String],
    stocks : [String]
})

export interface Event extends mongoose.Document {
    id: mongoose.Schema.Types.ObjectId;
    timeStamp: Date;
    positivity: Number,
    relevance : Number,
    source: string;
    category: string;
    subcategory: string;
    detail: string;
    regions: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Region'}];
    actors: string[];
    stocks: string[]
}

export class RegionCreationDTO {
    isFIPS : boolean;
    continent : string;
    country : string;
    state: string; // state, province, county, etc; varies
    city : string;
}

export class EventCreationDTO {
    id: mongoose.Schema.Types.ObjectId;
    timeStamp: Date;
    positivity: Number;
    relevance : Number;
    source: string;
    category: string;
    subcategory: string;
    detail: string;
    regions: mongoose.Schema.Types.ObjectId[];
    actors: string[];
    stocks: string[]

    eventRegions: RegionCreationDTO[]
}

export class QueryDTO {
    from: Date;
    to: Date;

    isFIPS: boolean

    continent : string;
    country : string;
    state: string;
    city : string;
    categories: string[];
    subcategories: string[];
    stocks: string[]
}
