import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Event, Region, EventCreationDTO, QueryDTO } from './events.model';
import * as CATS from './../res/categories.json';
import * as CONTS from './../res/continents.json'
import * as COUNTCODES from './../res/codesToCountries.json'
import * as COUNTNAMES from './../res/countriesToCodes.json'
import * as COUNTCONT from './../res/countriesToConts.json'
import * as SUBCOUNT from './../res/subdivisionToCountry.json'
import * as SUBNAMECODE from './../res/subdivisionNameToCode.json'

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
      // console.log(eventCreationDTO);
      return eventCreationDTO
    }

    // replaced by a call to createMany
    // /** Create event
    //   *  @param eventDict
    //   *   Verifies if region exists and create one if not
    //   *   TODO (?) - Parse relevant stocks - is this the place or is that a job
    //   *     for scrapers ?
    //   *
    //   * PRE : continent, country, state are in correct form
    //   */
    // async create(eventCreationDTO: EventCreationDTO) : Promise<Event>{
    //     // console.log(eventCreationDTO.detail);
    //     // console.log(new this.eventModel(eventCreationDTO));
    //     // console.log(new this.regionModel(eventCreationDTO));
    //     // console.log(eventCreationDTO.source);

    //     await this.prepareForCreation(eventCreationDTO);
    //     const createdEvent = new this.eventModel(eventCreationDTO);
    //     return createdEvent.save();
    // }

    /** Create multiple events
      *  @param eventDict
      *   Verifies if region exists and create one if not
      *   TODO (?) - Parse relevant stocks - is this the place or is that a job
      *     for scrapers ?
      *
      * PRE : continent, country, state are in correct form
      */
     async createMany(eventDTOArray: EventCreationDTO[]) : Promise<{ 
          newEvents: Event[],
          duplicateEvents: Event[] }> {
      // console.log(eventCreationDTO.detail);
      // console.log(new this.eventModel(eventCreationDTO));
      // console.log(new this.regionModel(eventCreationDTO));
      // console.log(eventCreationDTO.source);
      //console.log(eventDTOArray)

      eventDTOArray = await Promise.all(eventDTOArray.map(this.prepareForCreation, this)); // use .call() to avoid scope problems
      const isDuplicate = await Promise.all(eventDTOArray.map(this.checkDuplicate, this))
      //console.log(isDuplicate)

      const nonDuplicates = eventDTOArray.filter(function(value, index, arr) {
        return !isDuplicate[index]
      })

      const duplicateEvents = await this.eventModel.find(
          { '_id' : { $in: (isDuplicate
                            .filter(x => x !== null)
                            .map(x => { if (x !== null) return x._id })
                          ) 
                    } 
      }).populate('region', '', this.regionModel).exec()

      await this.regionModel.populate(nonDuplicates, { path: 'region' })
      //console.log(nonDuplicates)

      const createdEvents = this.eventModel.create(nonDuplicates)

      return Promise.resolve({ newEvents: await createdEvents, duplicateEvents: await duplicateEvents });
    }

    async checkDuplicate(eventDTO: EventCreationDTO) {
      return await this.eventModel.exists(eventDTO)
    }

    private validateRegion( toCheck: {
      continent: string, country: string, state: string, city:  string} ) {

        for (const [key, value] of Object.entries(toCheck)) {
          if (!toCheck[key] || toCheck[key].length == 0) {
              delete toCheck[key]
          } else {
            toCheck[key] = this.validateKey(key, value)
          }
        }

        if (Object.keys(toCheck).includes('continent') && 
              Object.keys(toCheck).includes('country')) {
          if (!COUNTCONT[`${toCheck.country}`].includes(toCheck.continent)) 
            throw new Error('Country is not in the given continent')
        }

        if (Object.keys(toCheck).includes('state')) {
          //console.log(toCheck)
          toCheck['state'] = this.fixSubdiv(toCheck['state'], toCheck['country'])
          //console.log(toCheck)
        }

        return toCheck
    }

    private trimToUpperNoAccents(s: string) : string {
      return  (s
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .trim()
                .toUpperCase())
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
          break; // subdivision needs to be handles separately
        case "city":
          return this.fixCity(value)
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
      myCountry = this.trimToUpperNoAccents(myCountry);
      console.log(myCountry);

      const name = COUNTCODES[myCountry];
      if ( name ) return myCountry;

      for (const [name, code] of Object.entries(COUNTNAMES)) {
          //console.log(name);
          if (myCountry == name) { return code; }
      }

      throw new Error("Invalid Country")
    }

    private fixSubdiv(mySubdiv: string, myCountryCode: string) : string {
      if (!myCountryCode) {
        throw new Error("Need to specify country to query by state")
      }

      mySubdiv = this.trimToUpperNoAccents(mySubdiv)
      //console.log(mySubdiv);

      const countrySubdivs = SUBCOUNT[`${myCountryCode}`]

      if (countrySubdivs && countrySubdivs.includes(mySubdiv) )
        return mySubdiv

      const subdivs = SUBNAMECODE[`${mySubdiv}`];

      if ( !subdivs ) {
        //console.log(subdivs)
        throw new Error("Subdivision does not exist in any country");
      }

      if (!subdivs.map(x => x.country).includes(myCountryCode)) {
        //console.log(subdivs)
        throw new Error("Subdivision does not exist in the given country");
      }

      const subdivCode = (subdivs
                            .filter(x => x.country == myCountryCode)[0]
                            .code);
      
      return subdivCode;

    }

    /** Take a string, strip it of characters not in the Latin alphabet,
     *  convert to upper case
     *
     * @param toStrip : String string to be stripped and converted
     */
    private stripAccentsToUpper(toStrip: string) :string {
      var r = toStrip.toLowerCase()
      r = r.replace(new RegExp(/\s/g),"");
      r = r.replace(new RegExp(/[àáâãäå]/g),"a");
      r = r.replace(new RegExp(/æ/g),"ae");
      r = r.replace(new RegExp(/ç/g),"c");
      r = r.replace(new RegExp(/[èéêë]/g),"e");
      r = r.replace(new RegExp(/[ìíîï]/g),"i");
      r = r.replace(new RegExp(/ñ/g),"n");
      r = r.replace(new RegExp(/[òóôõö]/g),"o");
      r = r.replace(new RegExp(/œ/g),"oe");
      r = r.replace(new RegExp(/[ùúûü]/g),"u");
      r = r.replace(new RegExp(/[ýÿ]/g),"y");
      r = r.replace(new RegExp(/\W/g),"");
      return r.toUpperCase()
    }

    private fixCity(myCity : string) :string {
      return this.stripAccentsToUpper(myCity)
    }

    async findAllEvents(): Promise<Event[]> {
        return this.eventModel.find().populate('region', '', this.regionModel).exec();
    }

    async findAllRegions(): Promise<Region[]> {
        return this.regionModel.find().exec();
    }

    async findEventsInRange(from: Date, to: Date): Promise<Event[]> {
      var myObj = new QueryDTO;
      myObj.from = from;
      myObj.to = to;

      return await this.findEventsGeneral( myObj )

    }

    async findEventsInRegion(continent: string, country: string, state: string, city: string): Promise<Event[]> {

      var myObj = new QueryDTO;
      myObj.continent = continent;
      myObj.country = country;
      myObj.state = state;
      myObj.city = city;

      return await this.findEventsGeneral( myObj )

    }

    private allSubsHaveCat(cats: Array<String>, subs: Array<String>) {
      console.log(cats)
      console.log(subs)
      return subs.every(sub => { return cats.some(cat => { return CATS[`${cat}`].includes(sub) }) })
    }

    async findEventsOfCategory(cats: string[], subs: string[] ): Promise<Event[]> {
      var myObj = new QueryDTO;
      myObj.categories = cats;
      myObj.subcategories = subs;

      return await this.findEventsGeneral( myObj )
    }

    async findByStock(stocks: string[]) {
      var myObj = new QueryDTO;
      myObj.stocks = stocks

      return await this.findEventsGeneral( myObj )
    }

    private timeMillis(date: Date) : number {
      return new Date(date).getTime()
    }

    private toArr( toConvert : string[]) : string[] {
      return toConvert.map(s => { return s.toString().replace(/[^a-zA-Z0-9 ]/g, "") })
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

      // investigate if this causes logic error in case there's an empty
      // subcategory halfway through array -- think maybe yes? TODO
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

      var regionAttributes = this.validateRegion({
        continent: query.continent,
        country: query.country,
        state: query.state,
        city: query.city,
      })
      //console.log(regionAttributes)

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
