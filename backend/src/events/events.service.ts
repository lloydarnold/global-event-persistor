import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Event, Region, EventCreationDTO, QueryDTO } from './events.model';
import * as CATS from './../res/categories.json';
import * as CONTS from './../res/continents.json'
import * as COUNTCODES from './../res/codesToCountries.json'
import * as COUNTNAMES from './../res/countriesToCodes.json'

@Injectable()
export class EventsService {
    constructor (
      @InjectModel('Event') private readonly eventModel: Model<Event>,
      @InjectModel('Region') private readonly regionModel: Model<Region>){
    }

    /** Prepare an event received from endpoint for creation.
      *  @param eventDict
      *   Validates the given region
      *   Verifies if region exists and create one if not
      *   Connects event with the corresponding region record
      *   TODO (?) - Parse relevant stocks - is this the place or is that a job
      *     for scrapers ?
      *
      * PRE : continent, country, state are in correct form
      */
    private async prepareForCreation(eventCreationDTO: EventCreationDTO) {
      var myRegion = {
        continent: eventCreationDTO.continent,
        country: eventCreationDTO.country,
        state: eventCreationDTO.state,
        city:  eventCreationDTO.city
      };

      myRegion = this.validateRegion(myRegion);
      // TODO verify if EU / GER / undefined comes up with eg. EU / GER / BAV / MUNICH
      // we don't want it to ! - it does:( -- TODO fix this
      const docs = await this.regionModel.find( myRegion ).exec();

      var doc;
      if (docs.length == 0) {
          const createdRegion = new this.regionModel(myRegion)
          console.log(`Region ${createdRegion} did not exist but was created`);
          doc = await createdRegion.save()
      }
      else doc = docs[0]
      eventCreationDTO.region = doc._id
      console.log(eventCreationDTO);
    }

    /** Create event
      *  @param eventDict
      *   Verifies if region exists and create one if not
      *   TODO (?) - Parse relevant stocks - is this the place or is that a job
      *     for scrapers ?
      *
      * PRE : continent, country, state are in correct form
      */
    async create(eventCreationDTO: EventCreationDTO) : Promise<Event>{
        // console.log(eventCreationDTO.detail);
        // console.log(new this.eventModel(eventCreationDTO));
        // console.log(new this.regionModel(eventCreationDTO));
        // console.log(eventCreationDTO.source);

        await this.prepareForCreation(eventCreationDTO);
        const createdEvent = new this.eventModel(eventCreationDTO);
        return createdEvent.save();
    }

    /** Create multiple events
      *  @param eventDict
      *   Verifies if region exists and create one if not
      *   TODO (?) - Parse relevant stocks - is this the place or is that a job
      *     for scrapers ?
      *
      * PRE : continent, country, state are in correct form
      */
     async createMany(eventDTOArray: EventCreationDTO[]) : Promise<Event[]>{
      // console.log(eventCreationDTO.detail);
      // console.log(new this.eventModel(eventCreationDTO));
      // console.log(new this.regionModel(eventCreationDTO));
      // console.log(eventCreationDTO.source);

      eventDTOArray.forEach.call(this, this.prepareForCreation); // use .call() to avoid scope problems
      const createdEvents = this.eventModel.create(eventDTOArray)
      return createdEvents;
  }

    private validateRegion( toCheck: {
      continent: string, country: string, state: string, city:  string} ) {

        for (const [key, value] of Object.entries(toCheck)) {
          if (toCheck[key] == undefined) {
              delete toCheck[key]
          } else {
            toCheck[key] = this.validateKey(key, value)
          }
        }

        return toCheck
    }

    /** Layer of abstraction between validateRegion & each individual check.
      * Makes it easier to update region in future
      */
    private validateKey(key : string, value : string) :string {
      // TODO finish validation
      switch(key) {
        case "continent":
          // put in try catch
          return this.fixCont(value);
        case "country":
        // put in try catch
          return this.fixCountry(value);
        case "state":
          break;
        case "city":
          break;
        default:
          //raise error. Invalid key given in region.
      }

      return value
    }

    /** validate continent codes
      *
      * will convert to ISO code from english, approve if already given as code
      * or complain if not
      * @param myCont : String the value of the continent code to check
      */
    private fixCont(myCont : string) :string {
      myCont = myCont.trim().toUpperCase();

      for (const [key, value] of Object.entries(CONTS)) {
          if (myCont == key || myCont == value) { return value };
      }

      // raise error
      throw new Error("Invalid Continent")
    }

    private fixCountry(myCountry : string) :string {
      myCountry = myCountry.trim().toUpperCase();
      console.log(myCountry);

        const name = COUNTCODES[myCountry];
        if ( name ) return myCountry;

        for (const [name, code] of Object.entries(COUNTNAMES)) {
            console.log(name);
            if (myCountry == name) { return code; }
        }

      throw new Error("Invalid Country")
    }

    async findAllEvents(): Promise<Event[]> {
        return this.eventModel.find().populate('region', '', this.regionModel).exec();
    }

    async findAllRegions(): Promise<Region[]> {
        return this.regionModel.find().exec();
    }

    async findEventsInRange(from: Date, to: Date): Promise<Event[]> {
        return this.eventModel.find({
            timeStamp: { $gte: from, $lte: to }
        }).populate('region', '', this.regionModel).exec();
    }

    async findEventsInRegion(continent: String, country: String, state: String, city: String|null): Promise<Event[]> {
        var regionAttributes = {
            continent: continent,
            country: country,
            state: state,
            city: city,
        }

        console.log(regionAttributes)

        // delete unspecified fields, thus defaulting to `ALL`
        Object.keys(regionAttributes).forEach(key => {
            if (regionAttributes[key] == undefined) {
                delete regionAttributes[key]
            }
        })

        const regions = await this.regionModel.find(regionAttributes).exec()

        return this.eventModel.find({
            'region': { $in: regions }
        }).populate('region', '', this.regionModel).exec()
    }

    private allSubsHaveCat(cats: Array<String>, subs: Array<String>) {
      console.log(cats)
      console.log(subs)
      return subs.every(sub => { return cats.some(cat => { return CATS[`${cat}`].includes(sub) }) })
    }

    async findEventsOfCategory(cats: String[], subs: String[] ): Promise<Event[]> {
      var myObj = new QueryDTO;
      myObj.categories = cats;
      myObj.subcategories = subs;

      return await this.findEventsGeneral( myObj )
    }

    async findByStock(stocks: String[]) {
      var myObj = new QueryDTO;
      myObj.stocks = stocks

      return await this.findEventsGeneral( myObj )
    }

    private timeMillis(date: Date) : number {
      return new Date(date).getTime()
    }

    private toArr( toConvert : String[]) : String[] {
      return toConvert.toString().replace(/[^a-zA-Z0-9 ]/g, "").split(" ")
    }

    async findEventsGeneral(query: QueryDTO) {
      var eventsQuery = this.eventModel.find();

      if (query.stocks && query.stocks.length > 0) {
        eventsQuery.where('stocks').in(this.toArr(query.stocks));
      };

      if (query.from && query.to) {
          eventsQuery.where('timeStamp').gte(this.timeMillis(query.from)
            ).lte(this.timeMillis(query.to))
        };

      if (query.from) {
        eventsQuery.where('timeStamp').gte(this.timeMillis(query.from));
      };

      if (query.to) {
        eventsQuery.where('timeStamp').lte(this.timeMillis(query.to));
      };

      if (query.categories && query.categories.length > 0) {
        const myCats = this.toArr( query.categories )

        eventsQuery.where('category').in(myCats);

        if (query.subcategories && query.subcategories.length > 0) {
          const mySubs = this.toArr( query.subcategories )
          if (!this.allSubsHaveCat(myCats, mySubs)) {
            throw new Error("Subcategory does not belong to the given category")
          };
          eventsQuery.where('subcategory').in(mySubs);
        }

      }

      var regionAttributes = {
        continent: query.continent,
        country: query.country,
        state: query.state,
        city: query.city,
      }

      // delete unspecified fields, thus defaulting to `ALL`
      Object.keys(regionAttributes).forEach(key => {
          if (regionAttributes[key] == undefined) {
              delete regionAttributes[key]
          }
      })

      if (Object.keys(regionAttributes).length > 0) {
        const regions = await this.regionModel.find(regionAttributes).exec()
        eventsQuery.where('region').in(regions);
      }

      return eventsQuery.populate('region', '', this.regionModel).exec()
    }
}
